from marshmallow import Schema, fields

class DummyUserVisitsSchema(Schema):
    user_name = fields.String(required=True, error_messages={"required": "User name is required."})
    category = fields.String(required=True, error_messages={"required": "Category is required."})
    place_name = fields.String(required=True, error_messages={"required": "Place name is required."})
    address = fields.String(required=True, error_messages={"required": "Address is required."})
    detail = fields.String(required=True, error_messages={"required": "Detail is required."})
    rating = fields.Float(required=True, error_messages={"required": "Rating is required."})
