from flask import Blueprint, request, jsonify
from app.model import User

def create_auth_routes(db):
    auth_routes = Blueprint('auth', __name__)
    user_model = User(db)

    @auth_routes.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if user_model.find_user(email):
            return jsonify({"error": "User already exists"}), 400

        user_id = user_model.create_user(name, email, password)
        
        return jsonify({"message": "User created successfully", "user_id": str(user_id)}), 201

    @auth_routes.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = user_model.find_user(email)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user_model.check_password(user['password'], password):
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"message": "Login successful", "user_id": str(user['_id'])}), 200

    return auth_routes
