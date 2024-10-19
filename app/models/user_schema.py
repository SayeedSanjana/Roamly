# app/models/user_schema.py
from marshmallow import Schema, fields, validate # type: ignore

class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2), error_messages={
        "required": "Name is required.",
        "minlength": "Name must be at least 2 characters long."
    })
    email = fields.Email(required=True, error_messages={
        "required": "Email is required.",
        "invalid": "Invalid email format."
    })
    password = fields.String(required=True, validate=validate.Length(min=6), error_messages={
        "required": "Password is required.",
        "minlength": "Password must be at least 6 characters long."
    })
