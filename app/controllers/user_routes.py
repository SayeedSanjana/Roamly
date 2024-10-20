from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService

def create_user_routes(db):
    user_routes = Blueprint('user', __name__)
    user_service = UserService(db)

    @user_routes.route('/update_profile', methods=['POST'])
    @jwt_required()  # Protect the route with JWT
    def update_profile():
        """
        Updates user profile preferences. Only allowed for logged-in users.
        Expects: JSON body with fields like 'cuisines', 'indoor_activities', etc.
        """
        user_id = get_jwt_identity()  # Get user ID from JWT
        user_id = ObjectId(user_id)   # Convert to ObjectId

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Pass the data to the UserService for processing
        response, status_code = user_service.update_preferences(user_id, data)
        return jsonify(response), status_code

    @user_routes.route('/get_preferences', methods=['GET'])
    @jwt_required()  # Protect the route with JWT
    def get_preferences():
        """
        Fetches the preferences of a logged-in user by their ID.
        """
        user_id = get_jwt_identity()  # Get user ID from JWT
        user_id = ObjectId(user_id)   # Convert to ObjectId

        response, status_code = user_service.get_preferences(user_id)
        return jsonify(response), status_code

    return user_routes
