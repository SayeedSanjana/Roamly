from flask import Blueprint, request, jsonify
from app.model import User  # Ensure this path is correct
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_user_routes(db):
    user_routes = Blueprint('user', __name__)
    user_model = User(db)

    @user_routes.route('/update_profile/<user_id>', methods=['POST'])
    def update_profile(user_id):
        # Log received user_id
        logging.debug(f"Received user_id: {user_id}")

        # Extract JSON data from the request
        data = request.get_json()
        logging.debug(f"Received data: {data}")
        logging.debug(f"User ID in request: {user_id}")

        if not data:
            return jsonify({"error": "Invalid or missing JSON data"}), 400

        # Extract fields from JSON data, providing defaults if fields are missing
        cuisines = data.get('cuisines', [])
        indoor_activities = data.get('indoor_activities', [])
        outdoor_activities = data.get('outdoor_activities', [])
        restaurants_visited = data.get('restaurants_visited', [])
        indoor_places_visited = data.get('indoor_places_visited', [])
        outdoor_places_visited = data.get('outdoor_places_visited', [])
        other_preferences = data.get('other_preferences', [])

        # Find user by user_id
        user = user_model.find_user_by_id(user_id)
        logging.debug(f"User found: {user}")

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update preferences
        updated = user_model.update_preferences_by_user_id(
            user_id,
            cuisines,
            indoor_activities,
            outdoor_activities,
            restaurants_visited,
            indoor_places_visited,
            outdoor_places_visited,
            other_preferences
        )
        logging.debug(f"Update result: {updated}")

        if updated:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update profile"}), 500

    @user_routes.route('/preferences/<user_id>', methods=['GET'])
    def get_preferences(user_id):
        # Fetch preferences by user_id
        preferences = user_model.get_preferences_by_user_id(user_id)
        logging.debug(f"Preferences fetched: {preferences}")

        if not preferences:
            return jsonify({"error": "Preferences not found"}), 404

        return jsonify(preferences), 200

    return user_routes
