from marshmallow import Schema, fields, validate
from app.fields import *
from app.validators import *


class Resource(Schema):
    endpoint = EndpointField(required=True)
    methods = fields.List(HTTPMethodField(), required=True, validate=[validate.Length(min=1), Unique()])
    response = JSONStringField(required=True)

class PartialResource(Schema):
    endpoint = EndpointField()
    methods = fields.List(HTTPMethodField(), validate=[validate.Length(min=1), Unique()])
    response = JSONStringField()
