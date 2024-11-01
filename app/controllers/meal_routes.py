from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from app.services.meal_service import MealService

def create_meal_routes(db):
    meal_routes = Blueprint('meal', __name__)
    meal_service = MealService(db)

    @meal_routes.route('/reminders', methods=['POST'])
    @jwt_required()  # Protect the route with JWT
    def handle_meal_reminders():
        """
        Handles creating meal reminders and managing reminder actions (snooze, dismiss).
        POST method with 'action' parameter determines whether to create reminders, snooze, or dismiss.
        """
        try:
            data = request.get_json()
            action = data.get("action", "create")  # Default action is 'create'

            # Get the user ID from the JWT token
            user_id = get_jwt_identity()
            user_id = ObjectId(user_id)  # Convert to ObjectId

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

    @meal_routes.route('/get_reminders', methods=['GET'])
    @jwt_required()  # Protect the route with JWT
    def get_reminders():
        """
        Fetch all pending or upcoming reminders for the logged-in user.
        """
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()
            user_id = ObjectId(user_id)  # Convert to ObjectId

            response, status_code = meal_service.get_pending_reminders(user_id)
            return jsonify(response), status_code
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        

    @meal_routes.route('/most_recent_reminder', methods=['GET'])
    @jwt_required()  # Protect the route with JWT
    def get_most_recent_reminder():
        """
        Fetch the most recent pending reminder for the logged-in user.
        """
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()
            user_id = ObjectId(user_id)  # Convert to ObjectId

            # Get the most recent reminder
            response, status_code = meal_service.get_most_recent_reminder(user_id)
            return jsonify(response), status_code
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return meal_routes

    return meal_routes

