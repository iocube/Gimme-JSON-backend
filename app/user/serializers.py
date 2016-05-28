from marshmallow import Schema, fields, validate


class User(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
