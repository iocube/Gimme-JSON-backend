import re
import json

from marshmallow import fields, ValidationError
from bson.objectid import ObjectId


class JSONStringField(fields.Field):
    def _serialize(self, value, attr, obj):
        return value

    def _deserialize(self, value, attr, data):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise ValidationError('Please provide a valid JSON.')

class HTTPMethodField(fields.Field):
    def _serialize(self, value, attr, obj):
        return value

    def _deserialize(self, value, attr, data):
        HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        if value in HTTP_METHODS:
            return value
        raise ValidationError('\'{value}\' is not valid HTTP method'.format(value=value))

class ObjectIdField(fields.Field):
    def _serialize(self, value, attr, data):
        return str(value)

    def _deserialize(self, value, attr, data):
        if ObjectId.is_valid(value):
            return {'$oid': value}
        raise ValidationError('Not a valid object id.')

class EndpointField(fields.Field):
    def _serialize(self, value, attr, obj):
        return value

    def _deserialize(self, value, attr, data):
        if len(value) == 0:
            raise ValidationError('Endpoint can not be empty.')
        elif re.search(r'\s', value):
            raise ValidationError('Endpoint should not contain space characters.')
        return value
