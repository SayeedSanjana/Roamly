from marshmallow import Schema, fields

class RestaurantSchema(Schema):
    name = fields.Str(required=True)
    rating = fields.Float(required=True)
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    postal_code = fields.Str(required=True)
    country = fields.Str(required=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)
