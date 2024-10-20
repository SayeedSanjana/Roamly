from bson import ObjectId
from marshmallow import Schema, fields, validates, ValidationError
class ObjectIdField(fields.Field):
    """
    Custom field for MongoDB ObjectId validation.
    """

    def _deserialize(self, value, attr, data, **kwargs):
        # Check if the value is a valid ObjectId
        if not ObjectId.is_valid(value):
            raise ValidationError(f"Invalid ObjectId: {value}")
        return ObjectId(value)

    def _serialize(self, value, attr, obj, **kwargs):
        # Serialize ObjectId as string
        return str(value)
class ReminderSchema(Schema):
    user_id = ObjectIdField(required=True)  # Custom ObjectId field
    meal = fields.Str(required=True)
    time = fields.Str(required=True)
    reminder_time = fields.Str(required=True)
    reminder_message = fields.Str(required=True)
    status = fields.Str(required=True)

    @validates('status')
    def validate_status(self, status):
        if status not in ['pending', 'snoozed', 'dismissed']:
            raise ValidationError("Invalid status value")
