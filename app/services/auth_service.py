# app/services/auth_service.py
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_schema import UserSchema
from bson import ObjectId
from marshmallow import ValidationError

class AuthService:
    def __init__(self, db):
        self.db = db
        self.user_schema = UserSchema()
    
    #Signup Function
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

        # Hash the password of the user and create the user
        hashed_password = generate_password_hash(validated_data['password'])
        user = {
            'name': validated_data['name'],
            'email': validated_data['email'],
            'password': hashed_password
        }

        user_id = self.db.users_auth.insert_one(user).inserted_id

        # Create an empty preferences record linked to this user_id
        preferences = {
            'user_id': user_id,
            'cuisines': [],
            'indoor_activities': [],
            'outdoor_activities': [],
            'restaurants_visited': [],
            'indoor_places_visited': [],
            'outdoor_places_visited': [],
            'preferred_meal_time': [],
            'other_preferences': []
        }
        self.db.user_preferences.insert_one(preferences)

        return {"message": "User created successfully", "user_id": str(user_id)}, 201

    #Login function 
    def login(self, data):
        """
        Authenticates a user by checking email and password.
        """
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

        return {"message": "Login successful", "user_id": str(user['_id'])}, 200
