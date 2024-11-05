from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from app.services.recommendation_service import RecommendationService  # Import your service class

def create_recommendation_routes(db):
    # Initialize Blueprint for the routes
    recommendation_routes = Blueprint('recommendation_routes', __name__)

    # Initialize the RecommendationService
    recommendation_service = RecommendationService(db)

    @recommendation_routes.route('/get_recommendations', methods=['GET'])
    @jwt_required()
    def get_recommendations():
        """
        GET /get_recommendations
        Fetches recommendations based on user's current context.
        """
        try:
            # Retrieve the user ID from the JWT token
            user_id = get_jwt_identity()
            user_id=ObjectId(user_id)

            # Retrieve query parameters: location, weather, and time
            current_location = request.args.get('location')  # e.g., "45.5088,-73.554"
            weather = request.args.get('weather')  # e.g., "sunny" or "rainy"
            time_of_day = request.args.get('time')  # e.g., "1:00 PM"

            # Check if all required parameters are provided
            if not current_location or not weather or not time_of_day:
                return jsonify({"error": "Missing location, weather, or time parameters"}), 400

            # Fetch recommendations from the service
            recommendations = recommendation_service.get_recommendations(user_id, current_location, weather, time_of_day)
            return jsonify(recommendations)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @recommendation_routes.route('/update_context', methods=['POST'])
    @jwt_required()
    def update_context():
        """
        POST /update_context
        Updates the user's context and provides updated recommendations.
        """
        try:
            # Parse the JSON body
            data = request.get_json()
            location = data.get('location')
            weather = data.get('weather')
            time_of_day = data.get('time')

            # Ensure that all required fields are present
            if not location or not weather or not time_of_day:
                return jsonify({"error": "Missing location, weather, or time parameters"}), 400

            # Update the context in the RecommendationService
            recommendation_service.update_context(location, weather, time_of_day)

            # Fetch updated recommendations
            user_id = get_jwt_identity()
            updated_recommendations = recommendation_service.get_recommendations(user_id, location, weather, time_of_day)

            return jsonify({
                "message": "Context updated successfully",
                "new_recommendations": updated_recommendations
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return recommendation_routes
