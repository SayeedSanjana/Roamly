from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService

def create_notification_routes(db):
    notification_routes = Blueprint('notification', __name__)
    notification_service = NotificationService(db)

    @notification_routes.route('/get_notifications', methods=['GET'])
    @jwt_required()
    def get_notifications():
        user_id = get_jwt_identity()
        notifications = notification_service.get_unseen_notifications(user_id)
        return jsonify(notifications), 200

    @notification_routes.route('/notifications/seen', methods=['POST'])
    @jwt_required()
    def mark_notifications_as_seen():
        user_id = get_jwt_identity()
        notification_service.mark_as_seen(user_id)
        return jsonify({"message": "Notifications marked as seen"}), 200

    return notification_routes
