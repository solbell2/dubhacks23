from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_migrate import Migrate
from datetime import datetime

# Create a Flask application
app = Flask(__name__)
app.secret_key = '6969'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login route

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserDrinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drink_type = db.Column(db.String(255), nullable=False)
    drink_size = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Define a relationship to the User model
    user = db.relationship('User', back_populates='drinks', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    caffeine = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.caffeine = 0

    # Define the one-to-many relationship to drinks
    drinks = db.relationship('UserDrinks', back_populates='user', lazy=True, cascade='all, delete-orphan')


from app import routes

