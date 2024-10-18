from bson import ObjectId
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
         # Convert string user_id to ObjectId
        try:
            user_id = ObjectId(user_id)
        except Exception as e:
            return jsonify({"error": "Invalid user ID format"}), 400

        # Extract JSON data from the request
        data = request.get_json()

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


        if updated:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update profile"}), 500

   
    # Helper function to convert ObjectId to string recursively
    def convert_objectid_to_str(document):
        """
        Recursively convert ObjectId fields in a MongoDB document to strings.
        """
        if isinstance(document, dict):
            return {key: convert_objectid_to_str(value) for key, value in document.items()}
        elif isinstance(document, list):
            return [convert_objectid_to_str(element) for element in document]
        elif isinstance(document, ObjectId):
            return str(document)
        else:
            return document

    @user_routes.route('/get_preferences/<user_id>', methods=['GET'])
    def get_preferences(user_id):
        try:
            # Convert the user_id to ObjectId
            user_id = ObjectId(user_id)
        except Exception as e:
            return jsonify({"error": "Invalid user ID format"}), 400

        # Fetch preferences by user_id
        preferences = user_model.get_preferences_by_user_id(user_id)

        if not preferences:
            return jsonify({"error": "Preferences not found"}), 404

        # Convert all ObjectId fields in the preferences to strings
        preferences = convert_objectid_to_str(preferences)

        return jsonify(preferences), 200

    return user_routes
