from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.recommendation_service import RecommendationService

def create_recommendation_routes(db):
    recommendation_routes = Blueprint('recommendation', __name__)
    recommendation_service = RecommendationService(db)

    @recommendation_routes.route('/get_recommendations', methods=['POST'])
    @jwt_required()
    def get_recommendations():
        user_id = get_jwt_identity()
        user_id=ObjectId(user_id)
        data = request.get_json()
        current_location = data.get("location")  # [latitude, longitude]
        current_time = data.get("time")  # "HH:MM AM/PM" format
        weather = data.get("weather")  # "sunny", "rainy", etc.

        if not current_location or not current_time or not weather:
            return jsonify({"error": "Location, time, and weather are required"}), 400

        response = recommendation_service.get_recommendations(user_id, current_location, current_time, weather)
        return jsonify(response)

    return recommendation_routes
