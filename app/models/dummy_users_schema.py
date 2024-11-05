from marshmallow import Schema, fields

class DummyUserVisitsSchema(Schema):
    user = fields.String(required=True, error_messages={"required": "User is required."})
    category = fields.String(required=True, error_messages={"required": "Category is required."})
    place = fields.String(required=True, error_messages={"required": "Place is required."})
    address = fields.String(required=True, error_messages={"required": "Address is required."})
    detail = fields.String(required=True, error_messages={"required": "Detail is required."})
    rating = fields.Float(required=True, error_messages={"required": "Rating is required."})
