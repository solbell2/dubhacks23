from flask import Flask
import pyrebase

# Create a Flask application
app = Flask(__name__)
app.secret_key = '6969'

config = {
    "apiKey": "AIzaSyDEZ2aZKjFoCYhqDmX4jhZ7r0iGi2llj04",
    "authDomain": "caffeine-tracker-d0485.firebaseapp.com",
    "projectId": "caffeine-tracker-d0485",
    "storageBucket": "caffeine-tracker-d0485.appspot.com",
    "messagingSenderId": "491121167276",
    "appId": "1:491121167276:web:4a75bc3785144fbc968809",
    "measurementId": "G-862R05TVN7",
    "databaseURL": "https://caffeine-tracker-d0485-default-rtdb.firebaseio.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

from app import routes
