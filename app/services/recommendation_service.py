from datetime import datetime, timedelta, timezone
import math
import logging
from bson import ObjectId
from flask_socketio import emit

from app.services import notification_service # type: ignore

# Set up a logger for the application
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, db, socketio):
        self.db = db
        self.socketio = socketio  # Inject Socket.IO instance
        self.last_context = {}    # Dictionary to track user's last known context
        self.notification_service = notification_service

    def get_user_preferences(self, user_id):
        return self.db.user_preferences.find_one({"user_id": user_id})
    
    def has_context_changed(self, user_id, current_location, current_time, weather):
        last_context = self.db.user_context.find_one({"user_id": ObjectId(user_id)})

        if not last_context:
            self.db.user_context.insert_one({
                "user_id": ObjectId(user_id),
                "location": current_location,
                "time": current_time,
                "weather": weather,
                "updated_at": datetime.now(timezone.utc)
            })
            return True

        context_changed = (
            last_context["location"] != current_location or
            last_context["time"] != current_time or
            last_context["weather"] != weather
        )

        if context_changed:
            self.db.user_context.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": {
                    "location": current_location,
                    "time": current_time,
                    "weather": weather,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            logging.info(f"Updated context for user {user_id} in the database.")

            # Emit notification to the specific user's room
            message = "Your recommendations have been updated based on your new context."
            logging.info(f"Emitting notification for user {user_id}: {message}")
            self.socketio.emit(
                'notification',
                {'message': message},
                room=str(user_id)  # Emit to the room named after the user ID
            )
            return True

        return False

    # Remove duplicate send_notification definition, and use it as needed
    def send_notification(self, user_id, message):
        logging.info(f"Sending notification to user {user_id}: {message}")
        self.socketio.emit('notification', {'message': message}, room=str(user_id))

  
    def get_similar_users_recommendations(self, user_id):
        # Get the current user's preferences and visited places with ratings
        user_preferences = self.get_user_preferences(user_id)
        if not user_preferences or not user_preferences.get("visited_places"):
            # If no preferences or visited places, fallback to sample recommendations
            return list(self.db.dummy_user_visits.aggregate([{"$sample": {"size": 10}}]))

        # Only include visited places that have a rating
        user_visited_places = {
            place["unique_id"]: place["rating"]
            for place in user_preferences["visited_places"]
            if "rating" in place
        }

        # Calculate similarity scores by comparing visited places and ratings
        all_users = self.db.user_preferences.find({"user_id": {"$ne": user_id}})
        similarity_scores = {}
        
        for other_user in all_users:
            other_user_id = other_user["user_id"]
            other_visited_places = {
                place["unique_id"]: place["rating"]
                for place in other_user.get("visited_places", [])
                if "rating" in place
            }
            
            # Compute similarity based on common places and similar ratings
            common_places = set(user_visited_places.keys()).intersection(set(other_visited_places.keys()))
            similarity_score = sum(
                1 for place_id in common_places 
                if abs(user_visited_places[place_id] - other_visited_places[place_id]) <= 1  # Rating difference within 1
            )
            if similarity_score > 0:
                similarity_scores[other_user_id] = similarity_score

        # Get top similar users
        sorted_users = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
        top_similar_users = [user[0] for user in sorted_users[:5]]

        # Gather recommendations from the top similar users
        recommendations = []
        for similar_user_id in top_similar_users:
            similar_user_recs = list(self.db.dummy_user_visits.find({"user_id": similar_user_id}).limit(5))
            recommendations.extend(similar_user_recs)

        return recommendations


    def get_content_based_recommendations(self, preferences):
        # Content-based filtering logic
        recommendations = []

        # Filter restaurants based on preferred cuisines and set type without subtype
        if "cuisines" in preferences:
            cuisine_matches = self.db.restaurants.find({
                "cuisine_type": {"$in": preferences["cuisines"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "cuisine_type": 1, "review_count": 1,
                "rating": 1, "food_time": 1}).limit(15)
            
            for match in cuisine_matches:
                match["type"] = "restaurant"  # Only set the type, no subtype
                recommendations.append(match)

        # Filter indoor activities and add "type" as "indoor"
        if "indoor_activities" in preferences:
            indoor_matches = self.db.indoor_activities.find({
                "category": {"$in": preferences["indoor_activities"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "category": 1, "review_count": 1,
                "rating": 1}).limit(15)
            for match in indoor_matches:
                match["type"] = "indoor"
                recommendations.append(match)

        # Filter outdoor activities and add "type" as "outdoor"
        if "outdoor_activities" in preferences:
            outdoor_matches = self.db.outdoor_activities.find({
                "category": {"$in": preferences["outdoor_activities"]}
            }, {"_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
                "latitude": 1, "longitude": 1, "category": 1, "review_count": 1,
                "rating": 1}).limit(15)
            for match in outdoor_matches:
                match["type"] = "outdoor"
                recommendations.append(match)

        return recommendations

    def prioritize_recommendations(self, recommendations, current_time, weather, meal_times):
        # Set a buffer time of ±30 minutes for flexibility
        time_buffer = timedelta(minutes=30)
        prioritized = []

        try:
            current_time_obj = datetime.strptime(current_time, "%I:%M %p")
        except ValueError:
            raise ValueError("Current time must be in the format 'HH:MM AM/PM'.")

        meal_type = None
        is_meal_time = False

        # Check if current time falls within any preferred meal time
        for meal in meal_times:
            if " - " in meal["time"]:
                start_time, end_time = meal["time"].split(" - ")
                try:
                    start_time_obj = datetime.strptime(start_time.strip(), "%I:%M %p")
                    end_time_obj = datetime.strptime(end_time.strip(), "%I:%M %p")
                    if start_time_obj - time_buffer <= current_time_obj <= end_time_obj + time_buffer:
                        meal_type = meal["meal"]  # Set the meal type
                        is_meal_time = True
                        break
                except ValueError:
                    raise ValueError("Time in 'preferred_meal_time' must be in the format 'HH:MM AM/PM - HH:MM PM'.")
            else:
                try:
                    meal_time_obj = datetime.strptime(meal["time"].strip(), "%I:%M %p")
                    if meal_time_obj - time_buffer <= current_time_obj <= meal_time_obj + time_buffer:
                        meal_type = meal["meal"]  # Set the meal type
                        is_meal_time = True
                        break
                except ValueError:
                    raise ValueError("Time in 'preferred_meal_time' must be in the format 'HH:MM AM/PM'.")

        # Prioritize based on meal type if within a meal time window
        if is_meal_time and meal_type:
            for rec in recommendations:
                if rec.get("type") == "restaurant" and meal_type in rec.get("food_time", ""):
                    prioritized.append(rec)

        # Add all restaurants if the prioritized list is empty (i.e., no specific match for meal type)
        if is_meal_time and not prioritized:
            prioritized.extend([rec for rec in recommendations if rec.get("type") == "restaurant"])

        # If not meal time or no matches found, prioritize based on weather
        if not is_meal_time or not prioritized:
            if weather in ["rainy", "snowy", "windy", "cloudy"]:
                prioritized.extend([rec for rec in recommendations if rec.get("type") == "indoor"])
            else:
                prioritized.extend([rec for rec in recommendations if rec.get("type") == "outdoor"])

        return prioritized


    def filter_nearby_places(self, recommendations, current_location):
        """
        Filter Recommendations Based on Proximity:
        - Include latitude, longitude, and address in the results.
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
                # Ensure address is included in the recommendation
                rec["address"] = rec.get("address", "Address not available")
                nearby_recommendations.append(rec)

        return nearby_recommendations
    

    def get_transportation_recommendations(self, recommendations):
        def fetch_nearby_transport(lat, lon, distance_km=1.0):
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371  # Earth radius in kilometers
                d_lat = math.radians(lat2 - lat1)
                d_lon = math.radians(lon2 - lon1)
                a = (math.sin(d_lat / 2) ** 2 +
                    math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
                return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            transport_list = []
            transports = self.db.transportation.find({}, {
                "_id": 1,
                "name": 1,
                "latitude": 1,
                "longitude": 1,
                "address": 1,
                "category": 1,
                "rating": 1
            })
            for transport in transports:
                dist = haversine(lat, lon, transport["latitude"], transport["longitude"])
                if dist <= distance_km:
                    transport["distance"] = round(dist, 2)
                    transport["address"] = transport.get("address", "Address not available")  # Ensure address is added
                    transport_list.append(transport)
            return transport_list

        for rec in recommendations:
            rec["transportation"] = fetch_nearby_transport(rec["latitude"], rec["longitude"])
            rec["address"] = rec.get("address", "Address not available")  # Add address to the main recommendation

        return recommendations
    
    def get_recommendations(self, user_id, current_location, current_time, weather):
        # Call `has_context_changed` to update context and send notification if necessary
        self.has_context_changed(user_id, current_location, current_time, weather)

        # Generate recommendations
        user_preferences = self.get_user_preferences(user_id)
        if not user_preferences:
            return {"error": "User preferences not found"}, 404

        similar_user_recs = self.get_similar_users_recommendations(user_id)
        content_recs = self.get_content_based_recommendations(user_preferences)

        all_personalized_recs = similar_user_recs + content_recs
        prioritized_personalized_recs = self.prioritize_recommendations(
            all_personalized_recs, current_time, weather, user_preferences.get("preferred_meal_time", [])
        )

        # Retrieve popular recommendations
        popular_recs = (
            [{"type": "restaurant", **rec} for rec in self.db.restaurants.find().sort("rating", -1).limit(5)] +
            [{"type": "indoor", **rec} for rec in self.db.indoor_activities.find().sort("rating", -1).limit(5)] +
            [{"type": "outdoor", **rec} for rec in self.db.outdoor_activities.find().sort("rating", -1).limit(5)]
        )

        # Filter nearby recommendations
        personalized_nearby_recs = self.filter_nearby_places(prioritized_personalized_recs, current_location)
        popular_nearby_recs = self.filter_nearby_places(popular_recs, current_location)

        # Add transportation recommendations
        personalized_nearby_recs = self.get_transportation_recommendations(personalized_nearby_recs)
        popular_nearby_recs = self.get_transportation_recommendations(popular_nearby_recs)

        # Serialize ObjectId for JSON
        def serialize_object_id(recommendations):
            for rec in recommendations:
                if "_id" in rec:
                    rec["_id"] = str(rec["_id"])
                if "transportation" in rec:
                    for transport in rec["transportation"]:
                        transport["_id"] = str(transport["_id"])
                rec["address"] = rec.get("address", "Address not available")  # Include address explicitly
            return recommendations

        personalized_nearby_recs = serialize_object_id(personalized_nearby_recs)
        popular_nearby_recs = serialize_object_id(popular_nearby_recs)

        return {
            "personalized_recommendations": personalized_nearby_recs,
            "popular_recommendations": popular_nearby_recs
        }