from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from app.services.location_service import LocationService
# import logging

# logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG for detailed logs


def create_location_routes(db):
    location_routes = Blueprint('location', __name__)
    location_service = LocationService(db)

    @location_routes.route('/set_current_location', methods=['POST'])
    def set_current_location():
        """
        Sets the user's current location based on automatic detection.
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON or missing request body"}), 400

            latitude = data.get('latitude')
            longitude = data.get('longitude')
            user_id = data.get('user_id')

            if not latitude or not longitude or not user_id:
                return jsonify({"error": "Latitude, longitude, and user_id are required"}), 400

            # Ensure the user_id is a valid ObjectId
            try:
                user_id = ObjectId(user_id)
            except InvalidId:
                return jsonify({"error": "Invalid user_id format"}), 400

            response, status_code = location_service.set_current_location(user_id, latitude, longitude)
            return jsonify(response), status_code

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @location_routes.route('/set_manual_location/<user_id>', methods=['POST'])
    def set_manual_location(user_id):
        """
        Allows the user to manually set their location.
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Invalid JSON or missing request body"}), 400

            # Ensure the user_id is a valid ObjectId
            try:
                user_id = ObjectId(user_id)
            except InvalidId:
                return jsonify({"error": "Invalid user_id format"}), 400

            response, status_code = location_service.set_manual_location(user_id, data)
            return jsonify(response), status_code

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return location_routes