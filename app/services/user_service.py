from bson import ObjectId
from marshmallow import ValidationError
from app.models.preferences_schema import PreferencesSchema

class UserService:
    def __init__(self, db):
        self.db = db
        self.preferences_schema = PreferencesSchema()

        # def update_preferences(self, user_id, data):
        #     try:
        #         # Validate the input data using your schema
        #         validated_data = self.preferences_schema.load(data, partial=True)

        #         # Prepare the update operations
        #         update_operations = {}

        #         # Append new values to existing arrays
        #         if "indoor_activities" in validated_data:
        #             update_operations["$push"] = {
        #                 "indoor_activities": {"$each": validated_data["indoor_activities"]}
        #             }

        #         if "outdoor_activities" in validated_data:
        #             if "$push" not in update_operations:
        #                 update_operations["$push"] = {}
        #             update_operations["$push"]["outdoor_activities"] = {
        #                 "$each": validated_data["outdoor_activities"]
        #             }

        #         if "cuisines" in validated_data:
        #             if "$push" not in update_operations:
        #                 update_operations["$push"] = {}
        #             update_operations["$push"]["cuisines"] = {"$each": validated_data["cuisines"]}

        #         if "preferred_meal_time" in validated_data:
        #             if "$push" not in update_operations:
        #                 update_operations["$push"] = {}
        #             update_operations["$push"]["preferred_meal_time"] = {
        #                 "$each": validated_data["preferred_meal_time"]
        #             }

        #         # If there are update operations, proceed to update the database
        #         if update_operations:
        #             updated = self.db.user_preferences.update_one(
        #                 {"user_id": ObjectId(user_id)},
        #                 update_operations,
        #                 upsert=True
        #             )

        #             if updated.matched_count > 0 or updated.upserted_id:
        #                 return {"message": "Preferences updated successfully"}, 200

        #         return {"error": "No valid data to update"}, 400

        #     except ValidationError as err:
        #         return {"error": err.messages}, 400
        #     except Exception as e:
        #         print(f"Error in update_preferences: {str(e)}")
        #         return {"error": "Internal server error"}, 500
    
    def update_preferences(self, user_id, data):
        try:
            # Validate the input data using your schema
            validated_data = self.preferences_schema.load(data, partial=True)

            # Prepare the update operations
            update_operations = {}

            # Overwrite the existing arrays with new values
            if "indoor_activities" in validated_data:
                update_operations["indoor_activities"] = validated_data["indoor_activities"]

            if "outdoor_activities" in validated_data:
                update_operations["outdoor_activities"] = validated_data["outdoor_activities"]

            if "cuisines" in validated_data:
                update_operations["cuisines"] = validated_data["cuisines"]

            if "preferred_meal_time" in validated_data:
                update_operations["preferred_meal_time"] = validated_data["preferred_meal_time"]

            if "other_preferences" in validated_data:
                update_operations["other_preferences"] = validated_data["other_preferences"]

            if "visited_places" in validated_data:
                update_operations["visited_places"] = validated_data["visited_places"]

            # If there are update operations, proceed to update the database
            if update_operations:
                updated = self.db.user_preferences.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$set": update_operations},
                    upsert=True  # Insert the document if it does not exist
                )

                if updated.matched_count > 0 or updated.upserted_id:
                    return {"message": "Preferences updated successfully"}, 200

            return {"error": "No valid data to update"}, 400

        except ValidationError as err:
            return {"error": err.messages}, 400
        except Exception as e:
            print(f"Error in update_preferences: {str(e)}")
            return {"error": "Internal server error"}, 500
    
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
    
    def remove_preferences(self, user_id, category, items):
            try:
                # Validate category
                if category not in ["visited_places", "indoor_activities", "outdoor_activities", "cuisines"]:
                    return {"error": "Invalid category"}, 400

                # Prepare the update operation based on category
                update_operation = {}
                if category == "visited_places":
                    # Remove specific places by "name" in visited_places
                    update_operation = {"$pull": {category: {"name": {"$in": [item["name"] for item in items]}}}}
                else:
                    # Remove specific items in cuisines, indoor_activities, or outdoor_activities
                    update_operation = {"$pull": {category: {"$in": items}}}

                # Perform the update
                updated = self.db.user_preferences.update_one(
                    {"user_id": ObjectId(user_id)},
                    update_operation
                )

                if updated.modified_count > 0:
                    return {"message": f"{category.capitalize()} items removed successfully"}, 200
                else:
                    return {"error": "No matching items found or no changes made"}, 404

            except Exception as e:
                print(f"Error in remove_preferences: {str(e)}")
                return {"error": "Internal server error"}, 500

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
        
        