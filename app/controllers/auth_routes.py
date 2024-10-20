from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

def create_auth_routes(db):
    auth_routes = Blueprint('auth', __name__)
    auth_service = AuthService(db)

    @auth_routes.route('/signup', methods=['POST'])
    def signup():
        """
        Handles user signup.
        Expects: JSON body with 'name', 'email', and 'password'.
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        response, status_code = auth_service.signup(data)
        return jsonify(response), status_code

    @auth_routes.route('/login', methods=['POST'])
    def login():
        """
        Handles user login.FLASK
        Expects: JSON body with 'email' and 'password'.
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        response, status_code = auth_service.login(data)
        return jsonify(response), status_code

    return auth_routes
