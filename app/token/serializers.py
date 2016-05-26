from marshmallow import Schema, fields


class Token(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
