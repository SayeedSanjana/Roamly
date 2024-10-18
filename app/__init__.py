from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config
import logging

# Disable debug messages for PyMongo
logging.getLogger('pymongo').setLevel(logging.WARNING)

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load configuration
    app.config.from_object(Config)

    # Initialize MongoDB connection
    client = MongoClient(app.config['MONGO_URI'])
    db = client['roamly_database']  # Replace with your actual database name

    # Register authentication routes
    from app.routes.auth_routes import create_auth_routes
    app.register_blueprint(create_auth_routes(db), url_prefix='/auth')

    # Register user profile and preferences routes
    from app.routes.user_routes import create_user_routes
    app.register_blueprint(create_user_routes(db), url_prefix='/user')

    return app
