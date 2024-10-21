from datetime import datetime, timedelta
from bson import ObjectId
from marshmallow import ValidationError
from app.models.reminder_schema import ReminderSchema

class MealService:
    def __init__(self, db):
        self.db = db
        self.reminder_schema = ReminderSchema()
    
    #Meal reminder function
    def create_meal_reminders(self, user_id):
        """
        Creates reminders for the user's meals based on their preferences.
        """
        user_preferences = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})

        if not user_preferences or "preferred_meal_time" not in user_preferences:
            return {"error": "Meal preferences not set for this user"}, 400

        meal_times = user_preferences.get("preferred_meal_time", [])
        reminders = []

        for meal in meal_times:
            meal_name = meal.get("meal")
            meal_time_str = meal.get("time")

            try:
                # Handle time parsing
                meal_start_time_str = meal_time_str.split("-")[0].strip() if "-" in meal_time_str else meal_time_str.strip()
                meal_start_time = datetime.strptime(meal_start_time_str, "%I:%M %p")
            except ValueError:
                return {"error": f"Invalid time format for {meal_name}. Expected '8:00 AM' or '8:00 AM - 10:00 AM'"}, 400

            reminder_time = datetime.combine(datetime.now().date(), meal_start_time.time())
            reminder_time = reminder_time.replace(microsecond=0)

            reminder_message = f"Reminder: It's time for {meal_name} at {meal_time_str}!"

            reminder_data = {
                "user_id": ObjectId(user_id),
                "meal": meal_name,
                "time": meal_start_time_str,
                "reminder_time": reminder_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "reminder_message": reminder_message,
                "status": "pending"
            }

            try:
                self.reminder_schema.load(reminder_data)
            except ValidationError as err:
                return {"error": err.messages}, 400

            result = self.db.meal_reminders.insert_one(reminder_data)
            reminder_data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
            reminder_data['user_id'] = str(reminder_data['user_id'])  # Convert ObjectId to string
            reminders.append(reminder_data)

        return {"message": "Reminders created", "reminders": reminders}, 201
    
    #Handle reminder dismiss,snooze,create

    def handle_reminder_action(self, reminder_id, action, snooze_duration=None):
        """
        Handles user interactions with meal reminders (snooze, dismiss).
        """
        reminder = self.db.meal_reminders.find_one({"_id": ObjectId(reminder_id)})

        if not reminder:
            return {"error": "Reminder not found"}, 404

        if action == "snooze":
            if not snooze_duration:
                return {"error": "Snooze duration is required"}, 400

            snoozed_time = datetime.strptime(reminder['reminder_time'], "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=snooze_duration)
            snoozed_time = snoozed_time.replace(microsecond=0)

            self.db.meal_reminders.update_one(
                {"_id": ObjectId(reminder_id)},
                {"$set": {"reminder_time": snoozed_time.isoformat(), "status": "snoozed"}}
            )
            return {"message": f"Reminder snoozed until {snoozed_time.isoformat()}"}, 200

        elif action == "dismiss":
            self.db.meal_reminders.update_one(
                {"_id": ObjectId(reminder_id)},
                {"$set": {"status": "dismissed"}}
            )
            return {"message": "Reminder dismissed"}, 200

        else:
            return {"error": "Invalid action"}, 400

    def get_pending_reminders(self, user_id):
        """
        Retrieves all pending reminders for the user.
        """
        try:
            reminders = self.db.meal_reminders.find({
                "user_id": ObjectId(user_id),
                "status": "pending"
            })

            reminders_list = []
            for reminder in reminders:
                reminder["_id"] = str(reminder["_id"])  # Convert ObjectId to string
                reminder["user_id"] = str(reminder["user_id"])  # Convert user_id to string
                reminders_list.append(reminder)

            if reminders_list:
                return {"reminders": reminders_list}, 200

            return {"message": "No pending reminders found"}, 200
        
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
