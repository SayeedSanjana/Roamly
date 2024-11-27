# app/__init__.py
from flask_socketio import SocketIO, join_room  # type: ignore
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config
from flask_jwt_extended import JWTManager # type: ignore
from app.services.recommendation_service import RecommendationService
from app.utils.scheduler import start_scheduler  # Import the scheduler function

# Initialize db as None at the module level
db = None
# socketio = SocketIO()  # Initialize SocketIO
socketio = SocketIO(cors_allowed_origins=["http://localhost:5173", "http://localhost:5174"])

def create_app():
    global db
    app = Flask(__name__)
    # CORS(app)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}}, supports_credentials=True)

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

    # Register data routes
    from app.controllers.data_routes import create_data_routes
    app.register_blueprint(create_data_routes(db), url_prefix='/data')

    # Register the recommendation routes
    from app.controllers.recommendation_routes import create_recommendation_routes
    app.register_blueprint(create_recommendation_routes(db,socketio), url_prefix='/recommendation')

    # Register notification routes (add this if missing)
    from app.controllers.notification_routes import create_notification_routes
    app.register_blueprint(create_notification_routes(db), url_prefix='/notifications')

 
   # Attach Socket.IO to the Flask app
    socketio.init_app(app)
    # Attach Socket.IO to the Flask app
    # socketio.init_app(app)

    # # Define the join room event to assign the client to a room based on user_id
    @socketio.on("join_room")
    def on_join(data):
        user_id = data["userId"]
        room = str(user_id)  # Use userId as the room name
        join_room(room)
        print(f"User {user_id} joined room {room}")
        
        # Use `socketio.emit` instead of `emit`
        socketio.emit("join_ack", {"message": f"User {user_id} joined room {room}"}, to=room)
    
    @app.route('/test_notification/<user_id>')
    def test_notification(user_id):
        recommendation_service = RecommendationService(db, socketio)
        recommendation_service.has_context_changed(user_id, "new_location", "10:00 AM", "sunny")
        return "Context updated, notification should be sent if there's a change.", 200


    return app

if __name__ == "__main__":
    app = create_app()  # Create the app instance
    socketio.run(app, host='0.0.0.0', port=5000)  # Run with Socket.IO