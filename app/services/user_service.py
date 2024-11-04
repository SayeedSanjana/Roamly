from bson import ObjectId
from marshmallow import ValidationError
from app.models.preferences_schema import PreferencesSchema

class UserService:
    def __init__(self, db):
        self.db = db
        self.preferences_schema = PreferencesSchema()

    def update_preferences(self, user_id, data):
        try:
            validated_data = self.preferences_schema.load(data)
        except ValidationError as err:
            return {"error": err.messages}, 400

        user = self.db.users_auth.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"error": "User not found"}, 404

        updated = self.db.user_preferences.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": validated_data},
            upsert=True
        )

        if updated.matched_count > 0:
            return {"message": "Profile updated successfully"}, 200
        return {"error": "Failed to update profile"}, 500

    def add_visited_places(self, user_id, places):
        try:
            # Validate only the visited_places field using partial=True
            validated_data = self.preferences_schema.load(
                {"visited_places": places}, partial=True
            )
            visited_places = validated_data["visited_places"]

            # Generate an ObjectId for each place
            for place in visited_places:
                place['unique_id'] = ObjectId()

            # Find the existing user document
            user = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})

            if user and user.get('visited_places'):
                # If visited_places already exists and is not empty, append new places
                self.db.user_preferences.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$push": {"visited_places": {"$each": visited_places}}},
                    upsert=True
                )
            else:
                # If visited_places is empty or doesn't exist, set the entire array
                self.db.user_preferences.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$set": {"visited_places": visited_places}},
                    upsert=True
                )

            # Retrieve the updated data and convert ObjectId to strings for JSON response
            updated_user = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
            for place in updated_user.get('visited_places', []):
                if 'unique_id' in place:
                    place['unique_id'] = str(place['unique_id'])

            # Return the updated visited places and a 200 status code
            return updated_user.get('visited_places', []), 200

        except ValidationError as err:
            return {"error": err.messages}, 400
        except Exception as e:
            print(f"Error in add_visited_places: {str(e)}")
            return {"error": "Internal server error"}, 500

    def get_preferences(self, user_id):
        preferences = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
        if not preferences:
            return {"error": "Preferences not found"}, 404

        preferences['_id'] = str(preferences['_id'])
        preferences['user_id'] = str(preferences['user_id'])

        for place in preferences.get('visited_places', []):
            if 'unique_id' in place:
                place['unique_id'] = str(place['unique_id'])

        return preferences, 200

    def rate_place(self, user_id, unique_id, rating=None):
        try:
            # Retrieve the user preferences
            user_preferences = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
            if not user_preferences:
                return {"error": "User preferences not found"}, 404

            places_list = user_preferences.get("visited_places", [])
            place_found = False

            # Check if the place is in the list
            for place in places_list:
                if str(place["unique_id"]) == unique_id:  # Compare unique_id as a string
                    if rating is not None:
                        # Update or add the rating if provided
                        place["rating"] = rating
                    place_found = True
                    break

            if not place_found:
                return {"error": "Place not found in visited places"}, 404

            # Update the database with the new or updated rating
            updated = self.db.user_preferences.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": {"visited_places": places_list}}
            )

            if updated.matched_count > 0:
                return {"message": "Place rating updated successfully"}, 200
            else:
                return {"error": "Failed to update place rating"}, 500

        except Exception as e:
            print(f"Error in rate_place: {str(e)}")
            return {"error": "Internal server error"}, 500