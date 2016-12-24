from marshmallow import Schema
from app.fields import *
from app.validators import Unique


class Endpoint(Schema):
    _id = ObjectIdField()
    route = EndpointField(required=True)
    storage = fields.List(fields.String(), required=True, validate=[Unique()])
    get = fields.String(required=True)
    post = fields.String(required=True)
    put = fields.String(required=True)
    patch = fields.String(required=True)
    delete = fields.String(required=True)