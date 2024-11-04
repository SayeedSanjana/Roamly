from marshmallow import Schema, fields

class PreferencesSchema(Schema):
    cuisines = fields.List(fields.String(), required=False)
    indoor_activities = fields.List(fields.String(), required=False)
    outdoor_activities = fields.List(fields.String(), required=False)

    visited_places = fields.List(
        fields.Dict(
            keys=fields.String(validate=lambda x: x in ["unique_id", "name", "address", "category", "rating"]),
            values=fields.Raw()
        ),
        required=False
    )

    preferred_meal_time = fields.List(
        fields.Dict(
            keys=fields.String(validate=lambda x: x in ["meal", "time"]),
            values=fields.String()
        ),
        required=False
    )

    other_preferences = fields.List(fields.String(), required=False)
