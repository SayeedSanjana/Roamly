from marshmallow import Schema, fields

class OutdoorActivitySchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required."})
    address = fields.String(required=True, error_messages={"required": "Address is required."})
    latitude = fields.Float(required=True, error_messages={"required": "Latitude is required."})
    longitude = fields.Float(required=True, error_messages={"required": "Longitude is required."})
    category = fields.String(required=True, error_messages={"required": "Category is required."})
    rating = fields.Float(required=True, error_messages={"required": "Rating is required."})
    review_count = fields.Integer(required=True, error_messages={"required": "Review count is required."})
