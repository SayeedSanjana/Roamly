from datetime import datetime
import math

class RecommendationService:
    def __init__(self, db):
        self.db = db

    def get_user_preferences(self, user_id):
        return self.db.user_preferences.find_one({"user_id": user_id})

    def get_similar_users_recommendations(self, user_id):
        # Collaborative filtering logic
        user_ratings = self.db.dummy_user_visits.find({"user_id": user_id})
        if not user_ratings:
            return []

        all_users = self.db.dummy_user_visits.distinct("user_id")
        similarity_scores = {}
        for other_user in all_users:
            if other_user != user_id:
                other_user_ratings = self.db.dummy_user_visits.find({"user_id": other_user})
                common_ratings = sum(1 for r in user_ratings if r in other_user_ratings)
                similarity_scores[other_user] = common_ratings

        sorted_users = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
        top_similar_users = [user[0] for user in sorted_users[:5]]

        recommendations = []
        for user in top_similar_users:
            user_recs = self.db.dummy_user_visits.find({"user_id": user}).limit(5)
            recommendations.extend(user_recs)

        return recommendations

    def get_content_based_recommendations(self, preferences):
        # Content-based filtering logic
        recommendations = []

        # Filter restaurants and set type without subtype
        if "cuisines" in preferences:
            cuisine_matches = self.db.restaurants.find({
                "cuisine_type": {"$in": preferences["cuisines"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "cuisine_type": 1, "review_count": 1,
                "rating": 1}).limit(5)
            
            for match in cuisine_matches:
                match["type"] = "restaurant"  # Only set the type, no subtype
                recommendations.append(match)

        # Filter indoor activities and add "type" as "indoor"
        if "indoor_activities" in preferences:
            indoor_matches = self.db.indoor_activities.find({
                "category": {"$in": preferences["indoor_activities"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "category": 1, "review_count": 1,
                "rating": 1}).limit(5)
            for match in indoor_matches:
                match["type"] = "indoor"
                recommendations.append(match)

        # Filter outdoor activities and add "type" as "outdoor"
        if "outdoor_activities" in preferences:
            outdoor_matches = self.db.outdoor_activities.find({
                "category": {"$in": preferences["outdoor_activities"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "category": 1, "review_count": 1,
                "rating": 1}).limit(5)
            for match in outdoor_matches:
                match["type"] = "outdoor"
                recommendations.append(match)

        return recommendations

    def prioritize_recommendations(self, recommendations, current_time, weather, meal_times):
        # Prioritization logic
        prioritized = []
        try:
            current_time_obj = datetime.strptime(current_time, "%I:%M %p")
        except ValueError:
            raise ValueError("Current time must be in the format 'HH:MM AM/PM'.")

        is_meal_time = False
        for meal in meal_times:
            if " - " in meal["time"]:
                start_time, end_time = meal["time"].split(" - ")
                try:
                    start_time_obj = datetime.strptime(start_time.strip(), "%I:%M %p")
                    end_time_obj = datetime.strptime(end_time.strip(), "%I:%M %p")
                    if start_time_obj <= current_time_obj <= end_time_obj:
                        is_meal_time = True
                        break
                except ValueError:
                    raise ValueError("Time in 'preferred_meal_time' must be in the format 'HH:MM AM/PM - HH:MM PM'.")
            else:
                try:
                    meal_time_obj = datetime.strptime(meal["time"].strip(), "%I:%M %p")
                    if meal_time_obj == current_time_obj:
                        is_meal_time = True
                        break
                except ValueError:
                    raise ValueError("Time in 'preferred_meal_time' must be in the format 'HH:MM AM/PM'.")

        if is_meal_time:
            prioritized.extend([rec for rec in recommendations if rec.get("type") == "restaurant"])
        else:
            if weather in ["rainy", "snowy", "windy","cloudy"]:
                prioritized.extend([rec for rec in recommendations if rec.get("type") == "indoor"])
            else:
                prioritized.extend([rec for rec in recommendations if rec.get("type") == "outdoor"])

        return prioritized

    def filter_nearby_places(self, recommendations, current_location):
        """
        Filter Recommendations Based on Proximity:
        - Use Haversine formula to calculate distance between current location and place
        """
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in kilometers
            d_lat = math.radians(lat2 - lat1)
            d_lon = math.radians(lon2 - lon1)
            a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        lat1, lon1 = current_location
        nearby_recommendations = []
        for rec in recommendations:
            distance = haversine(lat1, lon1, rec["latitude"], rec["longitude"])
            if distance <= 10:
                rec["distance"] = round(distance, 2)  # Add distance to each recommendation
                nearby_recommendations.append(rec)

        return nearby_recommendations

    def get_recommendations(self, user_id, current_location, current_time, weather):
        user_preferences = self.get_user_preferences(user_id)
        if not user_preferences:
            return {"error": "User preferences not found"}, 404

        similar_user_recs = self.get_similar_users_recommendations(user_id)
        content_recs = self.get_content_based_recommendations(user_preferences)

        all_personalized_recs = similar_user_recs + content_recs
        prioritized_personalized_recs = self.prioritize_recommendations(
            all_personalized_recs, current_time, weather, user_preferences.get("preferred_meal_time", [])
        )

        # Retrieve popular restaurants, indoor, and outdoor activities
        popular_recs = list(self.db.restaurants.find().sort("rating", -1).limit(5)) + \
                    list(self.db.indoor_activities.find().sort("rating", -1).limit(5)) + \
                    list(self.db.outdoor_activities.find().sort("rating", -1).limit(5))

        # Add type attribute for popular restaurants
        for rec in popular_recs:
            if "cuisine_type" in rec:
                rec["type"] = "restaurant"
            elif "category" in rec:
                if rec["category"] in ["Parks", "Outdoor Activities"]:
                    rec["type"] = "outdoor"
                else:
                    rec["type"] = "indoor"

        personalized_nearby_recs = self.filter_nearby_places(prioritized_personalized_recs, current_location)
        popular_nearby_recs = self.filter_nearby_places(popular_recs, current_location)

        # Convert ObjectId to string for JSON serialization
        def serialize_object_id(recommendations):
            for rec in recommendations:
                if "_id" in rec:
                    rec["_id"] = str(rec["_id"])
            return recommendations

        personalized_nearby_recs = serialize_object_id(personalized_nearby_recs)
        popular_nearby_recs = serialize_object_id(popular_nearby_recs)

        return {
            "personalized_recommendations": personalized_nearby_recs,
            "popular_recommendations": popular_nearby_recs
        }
