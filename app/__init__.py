# app/__init__.py
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config
from flask_jwt_extended import JWTManager # type: ignore
from app.utils.scheduler import start_scheduler  # Import the scheduler function

def create_app():
    app = Flask(__name__)
    CORS(app)
    # Setup JWT
    jwt = JWTManager(app)

    # Load configuration
    app.config.from_object(Config)

    # Initialize MongoDB connection
    client = MongoClient(app.config['MONGO_URI'])
    db = client['roamly_database']  # Replace with your actual database name

    # Register authentication routes
    from app.controllers.auth_routes import create_auth_routes
    app.register_blueprint(create_auth_routes(db), url_prefix='/auth')

    # Register user profile and preferences routes
    from app.controllers.user_routes import create_user_routes
    app.register_blueprint(create_user_routes(db), url_prefix='/user')

    # Register the location routes blueprint
    from app.controllers.location_routes import create_location_routes
    app.register_blueprint(create_location_routes(db), url_prefix='/location')

    # Register the time_context routes blueprint
    from app.controllers.meal_routes import create_meal_routes
    app.register_blueprint(create_meal_routes(db), url_prefix='/meal')

   
    # Start the background scheduler
    start_scheduler(app, db)  # Pass the app and db to the scheduler

    return app
