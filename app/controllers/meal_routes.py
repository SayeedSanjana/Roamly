from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.services.meal_service import MealService

def create_meal_routes(db):
    meal_routes = Blueprint('meal', __name__)
    meal_service = MealService(db)

    @meal_routes.route('/reminders/<user_id>', methods=['POST'])
    def handle_meal_reminders(user_id):
        """
        Handles creating meal reminders and managing reminder actions (snooze, dismiss).
        POST method with 'action' parameter determines whether to create reminders, snooze, or dismiss.
        """
        try:
            data = request.get_json()
            action = data.get("action", "create")  # Default action is 'create'
            
            if action == "create":
                # Create meal reminders based on user's meal preferences
                response, status_code = meal_service.create_meal_reminders(user_id)
                return jsonify(response), status_code
            
            elif action in ["snooze", "dismiss"]:
                # Handle snooze or dismiss actions for a reminder
                reminder_id = data.get("reminder_id")
                snooze_duration = data.get("snooze_duration")

                if not reminder_id:
                    return jsonify({"error": "Reminder ID is required for snooze or dismiss actions"}), 400

                # Handle the reminder action
                response, status_code = meal_service.handle_reminder_action(reminder_id, action, snooze_duration)
                return jsonify(response), status_code
            
            else:
                return jsonify({"error": "Invalid action"}), 400

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @meal_routes.route('/get_reminders/<user_id>', methods=['GET'])
    def get_reminders(user_id):
        """
        Fetch all pending or upcoming reminders for the user.
        """
        try:
            response, status_code = meal_service.get_pending_reminders(user_id)
            return jsonify(response), status_code
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return meal_routes
