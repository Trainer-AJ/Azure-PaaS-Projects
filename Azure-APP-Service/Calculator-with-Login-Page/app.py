from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import logging

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')  # Default to 'localhost' if not set
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')  # Default to 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')  # Default to 'password'
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'feb18')  # Default to 'feb18'

mysql = MySQL(app)

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/calculate', methods=['POST'])
def calculate():
    num1 = float(request.form['num1'])
    num2 = float(request.form['num2'])
    operation = request.form['operation']
    
    if operation == 'add':
        result = num1 + num2
    elif operation == 'subtract':
        result = num1 - num2
    elif operation == 'multiply':
        result = num1 * num2
    elif operation == 'divide':
        if num2 != 0:
            result = num1 / num2
        else:
            return 'Error: Cannot divide by zero!'
    
    return render_template('result.html', result=result)

def create_table_if_not_exists():
    """Function to create the database and table if they don't exist"""
    try:
        cursor = mysql.connection.cursor()
        
        # Ensure the database exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        
        # Use the specified database
        cursor.execute(f"USE {app.config['MYSQL_DB']}")
        
        # Create the users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        mysql.connection.commit()
        cursor.close()
        logging.info("Database and table checked/created successfully.")
    except Exception as e:
        logging.error(f"Error while creating database or table: {e}")


create_table_if_not_exists()

# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route to the home page (Dashboard or any default page after login)
@app.route('/')
@login_required
def calculator():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    username = session['username']
    return render_template('calculator.html', username=username)

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user[2], password):  # password is hashed
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('calculator'))
            else:
                flash("Invalid credentials, please try again.", 'danger')

        except Exception as e:
            logging.error(f"Database error during login: {e}")
            flash("An error occurred. Please try again later.", 'danger')

    return render_template('login.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            existing_user = cursor.fetchone()
            cursor.close()

            if existing_user:
                flash("Username already exists, please choose another.", 'danger')
            else:
                hashed_password = generate_password_hash(password)
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO users(username, password) VALUES (%s, %s)', (username, hashed_password))
                mysql.connection.commit()
                cursor.close()
                flash("Registration successful! You can now login.", 'success')
                return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Database error during registration: {e}")
            flash("An error occurred. Please try again later.", 'danger')

    return render_template('register.html')

# Route for logout
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
