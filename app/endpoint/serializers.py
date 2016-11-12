from marshmallow import Schema
from app.fields import *

    
class Endpoint(Schema):
    _id = ObjectIdField()
    route = EndpointField(required=True)
    storage_id = fields.String(required=True)
    get = fields.String(required=True)
    post = fields.String(required=True)
    put = fields.String(required=True)
    patch = fields.String(required=True)
    delete = fields.String(required=True)


class PartialEndpoint(Schema):
    _id = ObjectIdField()
    route = EndpointField()
    storage_id = fields.String()
    get = fields.String()
    post = fields.String()
    put = fields.String()
    patch = fields.String()
    delete = fields.String()
