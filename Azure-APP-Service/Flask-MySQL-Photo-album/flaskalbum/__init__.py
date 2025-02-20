from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from oauthlib.oauth2 import WebApplicationClient

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'



# Load environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
PHOTO_ALBUM_DB = os.getenv('PHOTO_ALBUM_DB')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD

# Configure upload folder
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the upload folder path relative to the current directory
UPLOAD_FOLDER = os.path.join(current_directory, '..', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure SQLAlchemy with MySQL Connector
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{MYSQL_USER}:"
    f"{MYSQL_ROOT_PASSWORD}@"
    f"{MYSQL_HOST}/"
    f"{PHOTO_ALBUM_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Connection health check
    'pool_recycle': 3600,   # Recycle connections after 1 hour
}

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# OAuth 2.0 client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Configure login manager
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models
from flaskalbum.models import Photo, User

# User loader callback
@login_manager.user_loader
def load_user(id):
    if id is None:
        return None
    try:
        return User.query.get(id)
    except (ValueError, TypeError):
        return None

# Create database if not exists
def create_database():
    mydb = mysql.connector.connect(
        host=f"{MYSQL_HOST}",
        user=f"{MYSQL_USER}",
        password=f"{MYSQL_ROOT_PASSWORD}"
    )
    mycursor = mydb.cursor()
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {PHOTO_ALBUM_DB}")
    mycursor.execute(f"USE {PHOTO_ALBUM_DB}")
    mycursor.close()

# Initialize database
with app.app_context():
    create_database()
    db.create_all()

# Add model views to admin interface
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Photo, db.session))

# Import routes
from flaskalbum import routes