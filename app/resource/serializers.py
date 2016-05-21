from marshmallow import Schema
from app.fields import *
from app.validators import *

    
class Resource(Schema):
    _id = ObjectIdField()
    endpoint = EndpointField(required=True)
    methods = fields.List(HTTPMethodField(), required=True, validate=[validate.Length(min=1), Unique()])
    response = JSONStringField(required=True)


class PartialResource(Schema):
    _id = ObjectIdField()
    endpoint = EndpointField()
    methods = fields.List(HTTPMethodField(), validate=[validate.Length(min=1), Unique()])
    response = JSONStringField()
