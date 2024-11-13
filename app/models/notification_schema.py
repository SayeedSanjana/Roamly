from marshmallow import Schema, fields, ValidationError
from bson import ObjectId

def validate_objectid(value):
    if not ObjectId.is_valid(value):
        raise ValidationError("Invalid ObjectId.")

class NotificationSchema(Schema):
    user_id = fields.String(required=True, validate=validate_objectid)  # Validate format
    message = fields.String(required=True)
    timestamp = fields.DateTime(required=True)
    seen = fields.Boolean(default=False, missing=False)
