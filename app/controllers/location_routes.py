from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.location_service import LocationService

def create_location_routes(db):
    location_routes = Blueprint('location', __name__)
    location_service = LocationService(db)

    @location_routes.route('/set_current_location', methods=['POST'])
    @jwt_required()  # Protect the route with JWT
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
            user_id = get_jwt_identity()  # Get user ID from the JWT

            if not latitude or not longitude:
                return jsonify({"error": "Latitude and longitude are required"}), 400

            # Convert user_id to ObjectId
            user_id = ObjectId(user_id)

            response, status_code = location_service.set_current_location(user_id, latitude, longitude)
            return jsonify(response), status_code

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @location_routes.route('/set_manual_location', methods=['POST'])
    @jwt_required()  # Protect the route with JWT
    def set_manual_location():
        """
        Allows the user to manually set their location.
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON or missing request body"}), 400

            user_id = get_jwt_identity()  # Get user ID from the JWT
            user_id = ObjectId(user_id)   # Convert to ObjectId

            response, status_code = location_service.set_manual_location(user_id, data)
            return jsonify(response), status_code

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return location_routes
