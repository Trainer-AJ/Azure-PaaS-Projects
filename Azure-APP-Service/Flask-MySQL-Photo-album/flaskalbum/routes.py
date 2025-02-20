import os
import uuid
from flask import json, render_template, flash, redirect, request, send_from_directory, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
import requests
from flaskalbum.models import Photo, User
from flaskalbum.utils import send_reset_email
from flaskalbum import app, db, client
from werkzeug.utils import secure_filename

GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Route for the home page (login page)
@app.route('/')
def index(): 
    return redirect(url_for('login'))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve user registration form data
        data = {
            'id' : uuid.uuid4().hex,
            'name' : request.form['name'],
            'email' : request.form['email'],
            'username' : request.form['username'],
            'password' : request.form['password']
        }
        
        # display message whether register is success or failed
        if User.register(data):
            message = 'Account created successfully!'
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            message = 'Account creation failed. Please try again.'
            flash(message, 'danger')
            return redirect(url_for('register'))

    # Render the registration form for GET requests
    return render_template('register.html', title='Create Account')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'login' in request.form:    
            username = request.form['username']
            password = request.form['password']

            # Check if user exists and password is correct
            authenticated_user = User.authenticate_user(username, password)
            if authenticated_user:             
                login_user(authenticated_user)
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        
        if 'oauth' in request.form:
            # Find the Google provider configuration
            google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]

            callback_url = f"{os.environ.get('WEBSITE_DOMAIN')}/login/callback"
            # Generate the URL to request access from Google's OAuth 2.0 server
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=callback_url,
                scope=["openid", "email", "profile"],
            )
            return redirect(request_uri)
    
    return render_template('login.html', title='Login')

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    callback_url = f"{os.environ.get('WEBSITE_DOMAIN')}/login/callback"
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=callback_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json())) 

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        profile_photo = userinfo_response.json()["picture"]
        name = userinfo_response.json()["name"]

        data = {
            'id': id,
            'name': name,
            'email': email,
            'profile_photo': profile_photo
        }

        user = User.oauth(data)
        
        login_user(user)
        return redirect(url_for('home'))
        
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    photo_details = Photo.query.filter_by(user_id=current_user.id).all()
    
    # Create a list of photo objects with both details and URLs
    photos = []
    for photo in photo_details:
        if photo.filename:
            photo_data = {
                'id': photo.id,
                'url': photo.image_url,
                'title': photo.title,
                'description': photo.description,
                'location': photo.location,
                'tags': photo.tags,
                'upload_date': photo.upload_date,
                'is_favorite': photo.is_favorite
            }
            photos.append(photo_data)

    if request.method == 'POST':
        if 'edit_details' in request.form:
            return url_for('edit_photo', photo_id=photo.id)
    
    return render_template('home.html', title='Home', name=current_user.name, photos=photos)

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.context_processor
def profile_display():
    if current_user.is_authenticated:
        # 
        if current_user.password != None: # user is not oauth user
            profile_photo = (current_user.profile_photo) if current_user.profile_photo else None
        else: # user is oauth user
            profile_photo = current_user.profile_photo
        return dict(profile_photo=profile_photo)
    return {}

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(email=current_user.email).first()

    if request.method == 'POST':
        if 'profile_photo' in request.files:
            profile_photo = request.files['profile_photo']
            if profile_photo.filename:
                unique_filename = secure_filename(f"{current_user.id}_{profile_photo.filename}")
                api_url = "https://freeimage.host/api/1/upload"
                api_key = os.environ.get('IMG_API_KEY')
                files = {'source': (unique_filename, profile_photo.read())}
                data = {'key': api_key, 'action': 'upload'}
                response = requests.post(api_url, files=files, data=data)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('status_code') == 200:
                    user.profile_photo = response_data['image']['url']
                    db.session.commit()
                    flash('Profile photo updated successfully!', 'success')
                else:
                    flash('Failed to upload profile photo.', 'error')
                    current_app.logger.error(f"FreeImageHost upload failed: {response_data}")
            else:
                flash('No file selected', 'error')
            return redirect(url_for('profile'))

        if 'update_profile' in request.form:
            update_username = request.form['username']
            name = request.form['name']
            email = request.form['email']
            update_info = User.update_info(current_user.username, update_username, name, email)
            if update_info:
                flash("Information updated successfully.", 'info')
                current_user.username = update_username
            else:
                flash("Failed to update information.", 'danger')
            return redirect(url_for('profile'))

        if 'delete_acc' in request.form:
            delete_account = User.delete_account(current_user.username)
            if delete_account:
                flash("Account deleted successfully", 'danger')
                logout_user()
                return redirect('/')
            else:
                flash("Failed to delete account.", 'danger')

    return render_template('profile.html', title='Profile', username=current_user.username, email=user.email, name=user.name, profile_photo=user.profile_photo)

# Route for user logout
@app.route('/logout')
def logout():
    # Remove the username from the session and redirect to the home page
    logout_user()
    return redirect('/')

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'error')
            return redirect(url_for('reset_request'))
            
        user = User.query.filter_by(email=email).first()
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        if user:
            try:
                send_reset_email(user)
            except Exception as e:
                print(e)
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password')

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # Verify the reset token
    email_from_token = User.verify_reset_token(token)
    
    # Check if the token is invalid or expired
    if email_from_token is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect('/')
    
    # Handle POST request for password reset
    if request.method == 'POST':
        try:
            # Retrieve and update the user's password
            password = request.form['password']
            if password:
                User.update_password(email_from_token, password)

                # Display a success message and redirect to the login page
                flash('Your password has been updated! You are now able to log in', 'success')
                return redirect('/login')
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password update failed: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    # Render the password reset form for GET requests
    return render_template('reset_token.html', title='Reset Password')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# ========================================================================================================

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'photo' not in request.files:
        flash('No file part in the request.', 'error')
        return redirect(url_for('home'))

    photo = request.files['photo']
    if photo.filename == '':
        flash('No selected file.', 'error')
        return redirect(url_for('home'))

    try:
        # Generate a unique filename
        unique_filename = secure_filename(f"{current_user.id}_{photo.filename}")
        
        # Use FreeImageHost API to upload the photo
        api_url = "https://freeimage.host/api/1/upload"
        api_key = os.environ.get('IMG_API_KEY')  # Replace with your FreeImageHost API key
        
        files = {
            'source': (unique_filename, photo.read()),
        }
        data = {
            'key': api_key,
            'action': 'upload',
        }

        response = requests.post(api_url, files=files, data=data)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status_code') == 200:
            # Extract image URL from the response
            image_url = response_data['image']['url']
            
            # Save photo details to the database
            new_photo = Photo(
                id=uuid.uuid4().hex,
                filename=unique_filename,  # Store the unique filename
                title=request.form['title'],
                description=request.form['description'],
                location=request.form['location'],
                tags=request.form['tags'],
                user_id=current_user.id,
                image_url=image_url  # Store the uploaded image URL
            )

            db.session.add(new_photo)
            db.session.commit()
            flash('Photo uploaded successfully!', 'success')
        else:
            flash('Failed to upload photo to FreeImageHost.', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('Error uploading photo.', 'error')
        print(e)  # For debugging

    return redirect(url_for('home'))

@app.route('/photo/<photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('home'))
    
    # Delete database record
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/photo/<photo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        photo.title = request.form['title']
        photo.description = request.form['description']
        photo.location = request.form['location']
        photo.tags = request.form['tags']
        
        try:
            db.session.commit()
            flash('Photo details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating photo details.', 'error')
            current_app.logger.error(f"Error updating photo details: {str(e)}")
        
        return redirect(url_for('home'))
    return render_template('edit_photo.html', title='Edit Photo', photo=photo)