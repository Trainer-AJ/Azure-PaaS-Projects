from datetime import datetime, timedelta
import os
import random
from flask_login import UserMixin
from flaskalbum import app
import jwt

# Replace 'db' with your SQLAlchemy instance import
from flaskalbum import db, bcrypt
USER_INFO_TABLE = os.getenv('USER_INFO_TABLE')
PHOTO_INFO_TABLE = os.getenv('PHOTO_INFO_TABLE')

class User(db.Model, UserMixin):
    #User model for handling authentication and user management.
    __tablename__ = USER_INFO_TABLE  # Replace with your table name if different

    id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    profile_photo = db.Column(db.String(500))

    # Relationship with photos (one-to-many) - Keep if you need it
    photos = db.relationship('Photo', backref=USER_INFO_TABLE, lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def oauth(data):
        "If user already exists, return the user object. Otherwise, create a new user and return it."
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            return user
        else:
            user = User(
                id=data['id'],
                name=data['name'],
                email=data['email'],
                profile_photo=data['profile_photo'],
            )
            db.session.add(user)
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def register(data):
        "Register a new user. First checks if the username and email already exist in the database. If not, it hashes the password and adds the new user to the database."
        if User.query.filter_by(username=data['username']).first():
            return 'Username already exists!'
        if User.query.filter_by(email=data['email']).first():
            return 'Email address already exists!'

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            username=data['username'],
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            
            return False

    @classmethod
    def authenticate_user(cls, username, password):
        "If username/email exists and password is correct, return the user object."

        user = cls.query.filter(
            (cls.username == username) | (cls.email == username)
        ).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None

    def get_reset_token(self, expires_sec=600):
        expiration_time = (datetime.now() + timedelta(seconds=expires_sec)).isoformat()
        payload = {
            'email': self.email,
            'expiration': expiration_time
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        try:
            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            email = payload['email']
            
            expiration = datetime.strptime(payload['expiration'], '%Y-%m-%dT%H:%M:%S.%f')
            
            
            if expiration < datetime.now():
                return None
            
            return email
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def update_password(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            return True
        return False

    def update_info(username, update_username, name, email):
        try:
            user = User.query.filter_by(username=username).first()
            user.username = update_username
            user.name = name
            user.email = email
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(e)
            return False

    def delete_account(self, username):
        try:
            user_to_delete = User.query.filter_by(username=username).first()
            db.session.delete(user_to_delete)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(e)
            return False
        
    # When printing the object, return the user's username, email, and name
    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}', name='{self.name}, profile_photo='{self.profile_photo}')"

# ===========================================================================

# Database Model (using SQLAlchemy)
class Photo(db.Model):
    __tablename__ = PHOTO_INFO_TABLE

    id = db.Column(db.String(100), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.now().astimezone())
    user_id = db.Column(db.String(50), db.ForeignKey(f'{USER_INFO_TABLE}.id'), nullable=False)
    image_url = db.Column(db.String(500))
    location = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'