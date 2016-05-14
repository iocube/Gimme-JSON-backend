import json
from flask import Blueprint, request, Response
from app.resource.model import ResourceModel
from app.resource import validators
from pymongo.errors import DuplicateKeyError
from app import decorators
from app.http_status_codes import HTTP_OK, HTTP_BAD_REQUEST


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

@decorators.crossdomain(methods=['GET'])
@decorators.to_json
def get_resources_list():
    return resource_model.get_all_resources()

@decorators.crossdomain(methods=['POST'])
@decorators.to_json
def create_new_resource():
    error_response = ErrorResponse()

    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_response.push('general', 'resource should contain \'endpoint\', \'methods\' and \'response\' fields')
        return error_response, HTTP_BAD_REQUEST

    missing_fields = which_fields_missing(request.json, ['endpoint', 'methods', 'response'])
    for field in missing_fields:
        error_response.push(field, '{field} field is required'.format(field=field))

    if not request.json.has_key('endpoint') or request.json.has_key('endpoint') and not validators.is_endpoint_field_valid(request.json['endpoint']):
        error_response.push('endpoint', 'endpoint should contain valid characters and no spaces.')

    if not request.json.has_key('methods') or request.json.has_key('methods') and not validators.is_methods_field_valid(request.json['methods']):
        error_response.push('methods', 'methods field should contain list of valid HTTP methods.')

    if not request.json.has_key('response') or request.json.has_key('response') and not validators.is_response_field_valid(request.json['response']):
        error_response.push('response', 'response field is not valid JSON.')

    if not error_response.is_empty():
        return error_response, HTTP_BAD_REQUEST

    try:
        new_resource = resource_model.create(request.json['endpoint'], request.json['methods'], request.json['response'])
    except DuplicateKeyError:
        error_response.push('endpoint', 'Each endpoint should have unique methods.')
        return error_response, HTTP_BAD_REQUEST

    return new_resource

@decorators.crossdomain()
@decorators.to_json
def delete_resource(resource_id):
    if not validators.is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    deleted = resource_model.delete(resource_id)

    if deleted:
        return {}

    # such id does not exist, nothing was deleted.
    return {}, HTTP_BAD_REQUEST

@decorators.crossdomain()
@decorators.to_json
def patch_resource(resource_id):
    error_response = ErrorResponse()

    if not validators.is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_response.push('general', 'invalid request. nothing to change.')
        return error_response, HTTP_BAD_REQUEST

    updated_fields = select_from_request(request.json, ['endpoint', 'methods', 'response'])

    # if no fields to update return error
    if not updated_fields:
        error_response.push('general', 'nothing to update')
        return error_response, HTTP_BAD_REQUEST

    if request.json.has_key('endpoint') and not validators.is_endpoint_field_valid(request.json['endpoint']):
        error_response.push('endpoint', 'endpoint should contain valid characters and no spaces.')

    if request.json.has_key('methods') and not validators.is_methods_field_valid(request.json['methods']):
        error_response.push('methods', 'methods field should contain list of valid HTTP methods.')

    if request.json.has_key('response') and not validators.is_response_field_valid(request.json['response']):
        error_response.push('response', 'response field is not valid JSON.')

    if not error_response.is_empty():
        return error_response, HTTP_BAD_REQUEST

    try:
        patched_resource = resource_model.patch(resource_id, updated_fields)
    except DuplicateKeyError:
        error_response.push('endpoint', 'Each endpoint should have unique methods.')
        return error_response, HTTP_BAD_REQUEST

    return patched_resource

@decorators.crossdomain()
@decorators.to_json
def put_resource(resource_id):
    error_response = ErrorResponse()

    if not validators.is_resource_id_valid(resource_id):
        return {}, HTTP_BAD_REQUEST

    if not isinstance(request.json, dict) or len(request.json.keys()) == 0:
        error_response.push('general', 'resource should contain \'endpoint\', \'methods\' and \'response\' fields')
        return error_response, HTTP_BAD_REQUEST

    if not request.json.has_key('endpoint') or request.json.has_key('endpoint') and not validators.is_endpoint_field_valid(request.json['endpoint']):
        error_response.push('endpoint', 'endpoint should contain valid characters and no spaces.')

    if not request.json.has_key('methods') or request.json.has_key('methods') and not validators.is_methods_field_valid(request.json['methods']):
        error_response.push('methods', 'methods field should contain list of valid HTTP methods.')

    if not request.json.has_key('response') or request.json.has_key('response') and not validators.is_response_field_valid(request.json['response']):
        error_response.push('response', 'response field is not valid JSON.')

    if not error_response.is_empty():
        return error_response, HTTP_BAD_REQUEST

    if request.json.has_key('_id'):
        del request.json['_id']

    try:
        updated_resource = resource_model.replace(resource_id, request.json)
    except DuplicateKeyError:
        error_response.push('endpoint', 'Each endpoint should have unique methods.')
        return error_response, HTTP_BAD_REQUEST

    return updated_resource
