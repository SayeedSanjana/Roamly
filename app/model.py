import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)
class User:
    def __init__(self, db):
        self.db = db

    # Create user with basic fields (authentication-related)
    def create_user(self, name, email, password):
        hashed_password = generate_password_hash(password)
        user = {
            'name': name,
            'email': email,
            'password': hashed_password
        }
        user_id = self.db.users_auth.insert_one(user).inserted_id
        
        # Create an empty preferences record linked to this user_id
        preferences = {
            'user_id': user_id,  # Reference to the authentication record
            'cuisines': [],
            'indoor_activities': [],
            'outdoor_activities': [],
            'restaurants_visited': [],
            'indoor_places_visited': [],
            'outdoor_places_visited': [],
            'other_preferences': []
        }
        self.db.user_preferences.insert_one(preferences)
        return user_id

    # Find user by email for authentication
    def find_user(self, email):
        return self.db.users_auth.find_one({'email': email})

    # Find user by _id for authentication
    def find_user_by_id(self, user_id):
        return self.db.users_auth.find_one({'_id': user_id})

    # Check if the password matches
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

    # Update preferences by user_id
    def update_preferences_by_user_id(self, user_id, cuisines, indoor_activities, outdoor_activities, restaurants_visited, indoor_places_visited, outdoor_places_visited, other_preferences):
        update_data = {
            'cuisines': cuisines,
            'indoor_activities': indoor_activities,
            'outdoor_activities': outdoor_activities,
            'restaurants_visited': restaurants_visited,
            'indoor_places_visited': indoor_places_visited,
            'outdoor_places_visited': outdoor_places_visited,
            'other_preferences': other_preferences
        }
        # Update the user preferences using the user_id as reference
        return self.db.user_preferences.update_one({'user_id': user_id}, {'$set': update_data})

    # Retrieve preferences by user_id
    def get_preferences_by_user_id(self, user_id):
        return self.db.user_preferences.find_one({'user_id': user_id})
