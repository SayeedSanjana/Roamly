# app/models/preferences_schema.py
from marshmallow import Schema, fields, ValidationError

class PreferencesSchema(Schema):
    cuisines = fields.List(fields.String(), required=True, error_messages={"required": "Cuisines are required."})
    indoor_activities = fields.List(fields.String(), required=True, error_messages={"required": "Indoor activities are required."})
    outdoor_activities = fields.List(fields.String(), required=True, error_messages={"required": "Outdoor activities are required."})
    restaurants_visited = fields.List(fields.String(), required=True, error_messages={"required": "Restaurants visited are required."})
    indoor_places_visited = fields.List(fields.String(), required=True, error_messages={"required": "Indoor places visited are required."})
    outdoor_places_visited = fields.List(fields.String(), required=True, error_messages={"required": "Outdoor places visited are required."})
    
    # preferred_meal_time is a list of dictionaries (each with "meal" and "time")
    preferred_meal_time = fields.List(
        fields.Dict(
            keys=fields.String(validate=lambda x: x == "meal" or x == "time"),
            values=fields.String(),
        ),
        required=True,
        error_messages={"required": "Preferred meal times are required."}
    )
    
    other_preferences = fields.List(fields.String(), required=False)  # Optional
