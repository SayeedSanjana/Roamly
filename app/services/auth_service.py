from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_schema import UserSchema
from app.models.preferences_schema import PreferencesSchema
from bson import ObjectId
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token
import datetime

class AuthService:
    def __init__(self, db):
        self.db = db
        self.user_schema = UserSchema()
        self.preferences_schema = PreferencesSchema()

    def signup(self, data):
        """
        Registers a new user after validating the data.
        """
        try:
            # Validate the user input
            validated_data = self.user_schema.load(data)
        except ValidationError as err:
            return {"error": err.messages}, 400

        # Check if the user already exists
        if self.db.users_auth.find_one({"email": validated_data['email']}):
            return {"error": "User already exists"}, 400

        # Hash the password and create the user
        hashed_password = generate_password_hash(validated_data['password'])
        user = {
            'name': validated_data['name'],
            'email': validated_data['email'],
            'password': hashed_password
        }

        user_id = self.db.users_auth.insert_one(user).inserted_id

        # Initialize the user preferences
        preferences = {
            'user_id': user_id,
            'cuisines': [],
            'indoor_activities': [],
            'outdoor_activities': [],
            'visited_places': [],
            'preferred_meal_time': [],
            'other_preferences': []
        }
        self.db.user_preferences.insert_one(preferences)

        return {"message": "User created successfully", "user_id": str(user_id)}, 201

    def login(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        # Find user by email
        user = self.db.users_auth.find_one({"email": email})
        if not user:
            return {"error": "User not found"}, 404

        # Verify password
        if not check_password_hash(user['password'], password):
            return {"error": "Invalid credentials"}, 401

        # Create JWT access token
        access_token = create_access_token(identity=str(user['_id']), expires_delta=datetime.timedelta(days=1))

        return {
            "message": "Login successful",
            "access_token": access_token,
            "user_id": str(user['_id'])
        }, 200
