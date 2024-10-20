from bson import ObjectId
from flask import Blueprint, request, jsonify
from app.services.user_service import UserService

def create_user_routes(db):
    user_routes = Blueprint('user', __name__)
    user_service = UserService(db)

    @user_routes.route('/update_profile/<user_id>', methods=['POST'])
    def update_profile(user_id):
        """
        Updates user profile preferences.
        Expects: JSON body with fields like 'cuisines', 'indoor_activities', etc.
        """
        try:
            user_id = ObjectId(user_id)  # Convert user_id to ObjectId
        except Exception as e:
            return jsonify({"error": "Invalid user ID format"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Pass the data to the UserService for processing
        response, status_code = user_service.update_preferences(user_id, data)
        return jsonify(response), status_code

    @user_routes.route('/get_preferences/<user_id>', methods=['GET'])
    def get_preferences(user_id):
        """
        Fetches the preferences of a user by their ID.
        """
        try:
            user_id = ObjectId(user_id)  # Convert user_id to ObjectId
        except Exception as e:
            return jsonify({"error": "Invalid user ID format"}), 400

        response, status_code = user_service.get_preferences(user_id)
        return jsonify(response), status_code

    return user_routes
