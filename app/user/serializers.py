from marshmallow import Schema, fields


class User(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)