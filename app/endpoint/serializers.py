from marshmallow import Schema
from app.fields import *
from app.validators import Unique


class Endpoint(Schema):
    _id = ObjectIdField()
    route = EndpointField(required=True)
    storage = fields.List(fields.String(), required=True, validate=[Unique()])
    on_get = fields.String(required=True)
    on_post = fields.String(required=True)
    on_put = fields.String(required=True)
    on_patch = fields.String(required=True)
    on_delete = fields.String(required=True)