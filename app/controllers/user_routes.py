from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService

def create_user_routes(db):
    user_routes = Blueprint('user', __name__)
    user_service = UserService(db)

    @user_routes.route('/update_profile', methods=['POST'])
    @jwt_required()
    def update_profile():
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        response, status_code = user_service.update_preferences(user_id, data)
        return jsonify(response), status_code

    @user_routes.route('/get_preferences', methods=['GET'])
    @jwt_required()
    def get_preferences():
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)

        response, status_code = user_service.get_preferences(user_id)
        return jsonify(response), status_code

    @user_routes.route('/add_visited_places', methods=['POST'])
    @jwt_required()
    def add_visited_places():
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)

        places = request.get_json().get('visited_places')
        if not places or not isinstance(places, list):
            return jsonify({"error": "An array of places is required"}), 400

        response, status_code = user_service.add_visited_places(user_id, places)
        return jsonify(response), status_code

    @user_routes.route('/rate_place', methods=['POST'])
    @jwt_required()
    def rate_place():
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)

        data = request.get_json()
        unique_id = data.get('unique_id')
        rating = data.get('rating')

        # Check if unique_id is provided (mandatory) and rating is optional
        if not unique_id:
            return jsonify({"error": "Unique ID is required"}), 400

        # Call the service method, passing the unique_id and rating
        response, status_code = user_service.rate_place(user_id, unique_id, rating)
        return jsonify(response), status_code

    return user_routes
