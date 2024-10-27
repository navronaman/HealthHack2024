from flask import Flask # Import the Flask class
from flask_cors import CORS # Import the CORS class, for cross resouces sharing

from app.blueprints.blood_test_blueprint import blood_test_bp # Import the blood_test_bp blueprint

def create_app():
    app = Flask(__name__) # Create an instance of the Flask class
    CORS(app) # Enable CORS for the app
    app.register_blueprint(blood_test_bp) # Register the blood_test_bp blueprint
    return app 