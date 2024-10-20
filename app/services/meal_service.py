import uuid
from datetime import datetime, timedelta

from bson import ObjectId
from app.models.reminder_schema import ReminderSchema
from marshmallow import ValidationError

class MealService:
    def __init__(self, db):
        self.db = db
        self.reminder_schema = ReminderSchema()

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
            meal_start_time = datetime.strptime(meal_time_str.split("-")[0].strip(), "%I:%M %p")

            # Generate a reminder time based on the meal start time
            reminder_time = datetime.combine(datetime.now(), meal_start_time.time())
            
            reminder_message = f"Reminder: It's time for {meal_name} at {meal_time_str}!"
            reminder_id = str(uuid.uuid4())  # Generate unique reminder ID

            reminder_data = {
                "_id": reminder_id,
                "user_id": user_id,
                "meal": meal_name,
                "time": meal_time_str,
                "reminder_time": reminder_time,
                "reminder_message": reminder_message,
                "status": "pending"  # Set status as 'pending'
            }

            # Validate the reminder before inserting into DB
            try:
                self.reminder_schema.load(reminder_data)
            except ValidationError as err:
                return {"error": err.messages}, 400

            # Insert the reminder into the database
            self.db.meal_reminders.insert_one(reminder_data)
            reminders.append(reminder_data)

        if not reminders:
            return {"message": "No reminders created"}, 200

        return {"message": "Reminders created", "reminders": reminders}, 201

    def handle_reminder_action(self, reminder_id, action, snooze_duration=None):
        """
        Handles user interactions with meal reminders (snooze, dismiss).
        """
        reminder = self.db.meal_reminders.find_one({"_id": reminder_id})

        if not reminder:
            return {"error": "Reminder not found"}, 404

        if action == "snooze":
            if not snooze_duration:
                return {"error": "Snooze duration is required"}, 400

            # Update the reminder's time
            snoozed_time = reminder["reminder_time"] + timedelta(minutes=snooze_duration)
            self.db.meal_reminders.update_one(
                {"_id": reminder_id},
                {"$set": {"reminder_time": snoozed_time, "status": "snoozed"}}
            )
            return {"message": f"Reminder snoozed until {snoozed_time}"}, 200

        elif action == "dismiss":
            self.db.meal_reminders.update_one(
                {"_id": reminder_id},
                {"$set": {"status": "dismissed"}}
            )
            return {"message": "Reminder dismissed"}, 200

        else:
            return {"error": "Invalid action"}, 400

    def get_pending_reminders(self, user_id):
        """
        Retrieves all pending reminders for the user.
        """
        reminders = self.db.meal_reminders.find({"user_id": ObjectId(user_id), "status": "pending"})
        reminders_list = list(reminders)

        for reminder in reminders_list:
            reminder["_id"] = str(reminder["_id"])  # Convert ObjectId to string for JSON serialization

        if reminders_list:
            return {"reminders": reminders_list}, 200

        return {"message": "No pending reminders found"}, 200
