from marshmallow import Schema
from app.fields import *


class Storage(Schema):
    _id = fields.String()
    value = fields.String()