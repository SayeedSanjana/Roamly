import logging
from datetime import datetime, timezone
from bson import ObjectId

class NotificationService:
    def __init__(self, db):
        self.db = db
        logging.basicConfig(level=logging.INFO)

    def create_notification(self, user_id, message):
        try:
            notification = {
                "user_id": ObjectId(user_id),
                "message": message,
                "timestamp": datetime.now(timezone.utc),
                "seen": False
            }
            result = self.db.notifications.insert_one(notification)
            logging.info(f"Notification created with ID {result.inserted_id} for user {user_id}")
        except Exception as e:
            logging.error(f"Failed to create notification for user {user_id}: {e}")

    def get_unseen_notifications(self, user_id):
        notifications = list(self.db.notifications.find({
            "user_id": ObjectId(user_id),
            "seen": False
        }))
        logging.info(f"Retrieved {len(notifications)} unseen notifications for user {user_id}")
        return notifications

    def mark_as_seen(self, user_id):
        self.db.notifications.update_many(
            {"user_id": ObjectId(user_id), "seen": False},
            {"$set": {"seen": True}}
        )
        logging.info(f"Marked all notifications as seen for user {user_id}")