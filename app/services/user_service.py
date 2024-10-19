# app/services/user_service.py
from app.models.preferences_schema import PreferencesSchema
from bson.objectid import ObjectId
from marshmallow import ValidationError

class UserService:
    def __init__(self, db):
        self.db = db
        self.preferences_schema = PreferencesSchema()

    def update_preferences(self, user_id, data):
        """
        Updates user preferences after validating the data.
        """
        try:
            # Validate the preferences data
            validated_data = self.preferences_schema.load(data)
        except ValidationError as err:
            return {"error": err.messages}, 400

        # Check if user exists
        user = self.db.users_auth.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"error": "User not found"}, 404

        # Update preferences in the database
        updated = self.db.user_preferences.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {
                "cuisines": validated_data.get('cuisines', []),
                "indoor_activities": validated_data.get('indoor_activities', []),
                "outdoor_activities": validated_data.get('outdoor_activities', []),
                "restaurants_visited": validated_data.get('restaurants_visited', []),
                "indoor_places_visited": validated_data.get('indoor_places_visited', []),
                "outdoor_places_visited": validated_data.get('outdoor_places_visited', []),
                "preferred_meal_time": validated_data.get('preferred_meal_time', []),
                "other_preferences": validated_data.get('other_preferences', [])
            }}
        )

        if updated.matched_count > 0:
            return {"message": "Profile updated successfully"}, 200
        return {"error": "Failed to update profile"}, 500

    def get_preferences(self, user_id):
        """
        Retrieves the preferences of a user.
        """
        preferences = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
        if not preferences:
            return {"error": "Preferences not found"}, 404

        # Convert ObjectId fields to string for easier JSON serialization
        preferences['_id'] = str(preferences['_id'])
        preferences['user_id'] = str(preferences['user_id'])

        return preferences, 200
