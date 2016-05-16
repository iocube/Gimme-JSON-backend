import json
from flask import request
from app.resource.model import ResourceModel
from app.resource import serializers
from pymongo.errors import DuplicateKeyError
from app import decorators
from app.http_status_codes import HTTP_BAD_REQUEST
from bson.objectid import ObjectId

resource_model = ResourceModel()

def select_from_request(target, what):
    properties = {key: val for key, val in target.iteritems() if key in what}
    return properties

def which_fields_missing(request, fields):
    if not request:
        return fields

    missing_fields = []
    for prop in fields:
        if not request.has_key(prop):
            missing_fields.append(prop)
    return missing_fields

def is_resource_id_valid(resource_id):
    return ObjectId.is_valid(resource_id)

class ErrorResponse(object):
    def __init__(self):
        self.response = {}

    def push(self, field, error):
        if self.response.has_key(field):
            self.response[field].append(error)
        else:
            self.response[field] = [error]

    def to_json(self):
        return json.dumps(self.response)

    def is_empty(self):
        return self.response == {}

@decorators.crossdomain()
@decorators.to_json
def get_resources_list():
    return resource_model.get_all_resources()

@decorators.crossdomain()
@decorators.to_json
def create_new_resource():
    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_missing_fields = {'general': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
        return error_missing_fields, HTTP_BAD_REQUEST

    data, error = serializers.Resource().load(request.json)
    if error:
        return error, HTTP_BAD_REQUEST

    try:
        new_resource = resource_model.create(request.json['endpoint'], request.json['methods'], request.json['response'])
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        return error_duplicate_values, HTTP_BAD_REQUEST

    return new_resource

@decorators.crossdomain()
@decorators.to_json
def delete_resource(resource_id):

    if not is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    deleted = resource_model.delete(resource_id)

    if deleted:
        return {}

    # such id does not exist, nothing was deleted.
    return {}, HTTP_BAD_REQUEST

@decorators.crossdomain()
@decorators.to_json
def patch_resource(resource_id):
    if not is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_invalid_payload = {'general': 'Invalid payload.'}
        return error_invalid_payload, HTTP_BAD_REQUEST

    fields_to_update, error = serializers.PartialResource().load(request.json)
    if error:
        return error, HTTP_BAD_REQUEST
    elif not fields_to_update:
        error_nothing_to_update = {'general': 'Nothing to update.'}
        return error_nothing_to_update, HTTP_BAD_REQUEST

    try:
        patched_resource = resource_model.patch(resource_id, fields_to_update)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        return error_duplicate_values, HTTP_BAD_REQUEST

    return patched_resource

@decorators.crossdomain()
@decorators.to_json
def put_resource(resource_id):
    if not is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_missing_fields = {'general': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
        return error_missing_fields, HTTP_BAD_REQUEST

    updated_resource, error = serializers.Resource().load(request.json)

    if error:
        return error, HTTP_BAD_REQUEST
    elif not updated_resource:
        error_nothing_to_update = {'general': 'Nothing to update.'}
        return error_nothing_to_update, HTTP_BAD_REQUEST

    try:
        updated_resource = resource_model.replace(resource_id, updated_resource)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        return error_duplicate_values, HTTP_BAD_REQUEST

    return updated_resource
