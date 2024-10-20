
from marshmallow import Schema, fields, validate # type: ignore
class ReminderSchema(Schema):
    _id = fields.String(required=True)
    user_id = fields.String(required=True)
    meal = fields.String(required=True, validate=validate.OneOf(["breakfast", "lunch", "dinner"]))
    time = fields.String(required=True, validate=validate.Regexp(r"^\d{1,2}:\d{2} [APM]{2}$", 
                error="Invalid time format. Example: '8:00 AM'"))
    reminder_time = fields.DateTime(required=True)
    reminder_message = fields.String(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["pending", "snoozed", "dismissed", "notified"]))