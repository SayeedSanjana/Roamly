from bson import ObjectId
from geopy.distance import geodesic

class RecommendationService:
    def __init__(self, db):
        self.db = db
        self.current_location = (0.0, 0.0)
        self.weather = None
        self.time_of_day = None

    def update_context(self, location, weather, time_of_day):
        if location:
            self.current_location = tuple(map(float, location.split(',')))
        self.weather = weather
        self.time_of_day = time_of_day

    def get_recommendations(self, user_id, current_location, weather, time_of_day):
        try:
            user_id = ObjectId(user_id)
            user_preferences = self.db.user_preferences.find_one({"user_id": user_id})
            if not user_preferences:
                return {"error": "User preferences not found"}

            # Update context
            self.update_context(current_location, weather, time_of_day)

            # Initialize recommendation sections
            recommendations = {
                "based_on_preferences": [],
                "most_popular": []
            }

            # Content-Based Filtering: Recommend based on user preferences
            if user_preferences:
                recommendations["based_on_preferences"].extend(self._recommend_based_on_preferences(user_preferences))

            # Collaborative Filtering: Recommend popular options
            recommendations["most_popular"].extend(self._get_most_popular())

            return recommendations
        except Exception as e:
            return {"error": str(e)}

    def _recommend_based_on_preferences(self, user_preferences):
        recommendations = []

        # Check if it's meal time and recommend restaurants
        is_meal_time = any(self.time_of_day in pref['time'] for pref in user_preferences.get('preferred_meal_time', []))
        if is_meal_time:
            recommendations.extend(self._recommend_restaurants(user_preferences))
        else:
            if self.weather.lower() == 'sunny':
                recommendations.extend(self._recommend_outdoor_activities(user_preferences))
            else:
                recommendations.extend(self._recommend_indoor_activities(user_preferences))

        return recommendations

    def _get_most_popular(self):
        popular_recommendations = []

        # Fetch popular restaurants
        popular_restaurants = self.db.restaurants.find().sort("rating", -1).limit(10)
        for restaurant in popular_restaurants:
            distance = geodesic(self.current_location, (restaurant['latitude'], restaurant['longitude'])).miles
            popular_recommendations.append({
                "name": restaurant["name"],
                "address": restaurant["address"],
                "rating": restaurant["rating"],
                "distance": round(distance, 2),
                "category": "restaurant",
                "cuisine_type": restaurant.get("cuisine_type")
            })

        # Fetch popular activities based on weather
        if self.weather.lower() in ["sunny", "clear"]:
            popular_activities = self.db.outdoor_activities.find().sort("rating", -1).limit(10)
            category = "outdoor"
        else:
            popular_activities = self.db.indoor_activities.find().sort("rating", -1).limit(10)
            category = "indoor"

        for activity in popular_activities:
            distance = geodesic(self.current_location, (activity['latitude'], activity['longitude'])).miles
            popular_recommendations.append({
                "name": activity["name"],
                "location": activity["address"],
                "rating": activity["rating"],
                "distance": round(distance, 2),
                "category": category,
                "details": activity.get("details")
            })

        return popular_recommendations

    def _recommend_restaurants(self, user_preferences):
        cuisine_preferences = user_preferences.get('cuisines', [])
        nearby_restaurants = self.db.restaurants.find({"cuisine_type": {"$in": cuisine_preferences}})
        sorted_restaurants = sorted(
            nearby_restaurants,
            key=lambda r: geodesic(self.current_location, (r['latitude'], r['longitude'])).miles
        )
        return [
            {
                "name": r["name"],
                "address": r["address"],
                "rating": r["rating"],
                "distance": round(geodesic(self.current_location, (r['latitude'], r['longitude'])).miles, 2),
                "category": "restaurant",
                "cuisine_type": r.get("cuisine_type")
            } for r in sorted_restaurants
        ]

    def _recommend_outdoor_activities(self, user_preferences):
        outdoor_preferences = user_preferences.get('outdoor_activities', [])
        outdoor_activities = self.db.outdoor_activities.find({"activity_type": {"$in": outdoor_preferences}})
        sorted_activities = sorted(
            outdoor_activities,
            key=lambda a: geodesic(self.current_location, (a['latitude'], a['longitude'])).miles
        )
        return [
            {
                "name": a["name"],
                "location": a["address"],
                "rating": a["rating"],
                "distance": round(geodesic(self.current_location, (a['latitude'], a['longitude'])).miles, 2),
                "category": "outdoor",
                "details": a.get("category")
            } for a in sorted_activities
        ]

    def _recommend_indoor_activities(self, user_preferences):
        indoor_preferences = user_preferences.get('indoor_activities', [])
        indoor_activities = self.db.indoor_activities.find({"activity_type": {"$in": indoor_preferences}})
        sorted_activities = sorted(
            indoor_activities,
            key=lambda a: geodesic(self.current_location, (a['latitude'], a['longitude'])).miles
        )
        return [
            {
                "name": a["name"],
                "location": a["address"],
                "rating": a["rating"],
                "distance": round(geodesic(self.current_location, (a['latitude'], a['longitude'])).miles, 2),
                "category": "indoor",
                "details": a.get("details")
            } for a in sorted_activities
        ]
