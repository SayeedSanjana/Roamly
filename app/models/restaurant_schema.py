from marshmallow import Schema, fields

class RestaurantSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required."})
    address = fields.String(required=True, error_messages={"required": "Address is required."})
    city = fields.String(required=True, error_messages={"required": "City is required."})
    state = fields.String(required=True, error_messages={"required": "State is required."})
    zip_code = fields.String(required=True, error_messages={"required": "Zip code is required."})
    latitude = fields.Float(required=True, error_messages={"required": "Latitude is required."})
    longitude = fields.Float(required=True, error_messages={"required": "Longitude is required."})
    cuisine_type = fields.String(required=True, error_messages={"required": "Cuisine type is required."})
    review_count = fields.Integer(required=True, error_messages={"required": "Review count is required."})
    rating = fields.Float(required=True, error_messages={"required": "Rating is required."})
    food_time = fields.String(required=True, error_messages={"required": "Food time is required."})
