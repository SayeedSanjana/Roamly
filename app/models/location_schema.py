# app/models/location_schema.py
from marshmallow import Schema, fields, ValidationError

class LocationSchema(Schema):
    """
    Unified schema for both automatic and manual location detection.
    Latitude and longitude are required for both.
    Other fields are optional for automatic detection but can be required for manual.
    """
    latitude = fields.Float(required=True, error_messages={"required": "Latitude is required."})
    longitude = fields.Float(required=True, error_messages={"required": "Longitude is required."})

    # The following fields are optional for automatic detection but required for manual entry
    street = fields.String(required=False, error_messages={"required": "Street is required."})
    city = fields.String(required=False, error_messages={"required": "City is required."})
    state = fields.String(required=False, error_messages={"required": "State is required."})
    country = fields.String(required=False, error_messages={"required": "Country is required."})
    postal_code = fields.String(required=False, error_messages={"required": "Postal code is required."})

    def validate_manual_location(self, data):
        """
        Custom validation to ensure all fields are present for manual location entry.
        """
        if 'street' not in data or not data['street']:
            raise ValidationError("Street is required for manual location.")
        if 'city' not in data or not data['city']:
            raise ValidationError("City is required for manual location.")
        if 'state' not in data or not data['state']:
            raise ValidationError("State is required for manual location.")
        if 'country' not in data or not data['country']:
            raise ValidationError("Country is required for manual location.")
        if 'postal_code' not in data or not data['postal_code']:
            raise ValidationError("Postal code is required for manual location.")
