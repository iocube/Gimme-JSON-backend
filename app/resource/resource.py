import json
from flask import Blueprint, request, Response
from app.resource.model import ResourceModel
from app.resource import validators
from pymongo.errors import DuplicateKeyError

HTTP_OK = 200
HTTP_BAD_REQUEST = 400

blueprint = Blueprint('resource', __name__)
resource_model = ResourceModel()

def select_from_request(target, what):
    properties = {key: val for key, val in target.iteritems() if key in what}
    return properties

def which_fields_missing(request, fields):
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

@blueprint.route('/resource', methods=['GET'])
def get_resources_list():
    return Response(
        response=resource_model.get_all_resources().to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )

@blueprint.route('/resource', methods=['POST'])
def create_new_resource():
    error_response = ErrorResponse()

    missing_fields = which_fields_missing(request.json, ['endpoint', 'methods', 'response', 'queryParams'])
    for field in missing_fields:
        error_response.push(field, '{field} field is required'.format(field=field))

    if request.json.has_key('methods') and not validators.is_methods_field_valid(request.json['methods']):
        error_response.push('methods', 'methods field should contain list of valid HTTP methods')

    if request.json.has_key('response') and not validators.is_response_field_valid(request.json['response']):
        error_response.push('response', 'response field is not valid JSON.')

    if not error_response.is_empty():
        return Response(
            response=error_response.to_json(),
            status=HTTP_BAD_REQUEST,
            mimetype='application/json'
        )

    try:
        new_resource = resource_model.create(request.json['endpoint'], request.json['methods'], request.json['response'], request.json['queryParams'])
    except DuplicateKeyError:
        error_response.push('endpoint', 'Each endpoint should have unique methods.')
        return Response(
            response=error_response.to_json(),
            status=HTTP_BAD_REQUEST,
            mimetype='application'
        )

    return Response(
        response=new_resource.to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )

@blueprint.route('/resource/<string:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    if not validators.is_resource_id_valid(resource_id):
        return Response(
            status=HTTP_BAD_REQUEST,
            mimetype='application/json'
        )

    deleted = resource_model.delete(resource_id)

    if deleted:
        return Response(
            status=HTTP_OK,
            mimetype='application/json'
        )

    # such id does not exist, nothing was deleted.
    return Response(
        status=HTTP_BAD_REQUEST,
        mimetype='application/json'
    )

@blueprint.route('/resource/<string:resource_id>', methods=['PATCH'])
def patch_resource(resource_id):
    if not validators.is_resource_id_valid(resource_id) or len(request.json.keys()) == 0:
        return Response(
            status=HTTP_BAD_REQUEST,
            mimetype='application/json'
        )

    error_response = ErrorResponse()
    updated_fields = select_from_request(request.json, ['endpoint', 'methods', 'response', 'queryParams'])

    # if no fields to update return error
    if not updated_fields:
        error_response.push('general', 'nothing to update')
        return Response(
            response=error_response.to_json(),
            status=HTTP_BAD_REQUEST,
            mimetype='application/json'
        )

    if request.json.has_key('endpoint') and not validators.is_endpoint_field_valid(request.json['endpoint']):
        error_response.push('endpoint', 'endpoint should contain valid characaters and no spaces.')

    if request.json.has_key('methods') and not validators.is_methods_field_valid(request.json['methods']):
        error_response.push('methods', 'methods field should contain list of valid HTTP methods.')

    if request.json.has_key('response') and not validators.is_response_field_valid(request.json['response']):
        error_response.push('response', 'response field is not valid JSON.')

    if not error_response.is_empty():
        return Response(
            response=error_response.to_json(),
            status=HTTP_BAD_REQUEST,
            mimetype='application/json'
        )

    try:
        patched_resource = resource_model.patch(resource_id, updated_fields)
    except DuplicateKeyError:
        error_response.push('endpoint', 'Each endpoint should have unique methods.')
        return Response(
            response=error_response.to_json(),
            status=HTTP_BAD_REQUEST,
            mimetype='application'
        )

    return Response(
        response=patched_resource.to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )
