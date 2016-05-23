from marshmallow import Schema, fields
from app.fields import *
from app.validators import *


class User(Schema):
    _id = ObjectIdField()
    username = fields.String(required=True)
    password = fields.String(required=True)