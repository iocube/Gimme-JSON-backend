import json
from flask import request
from app.resource.model import ResourceModel
from app.resource import serializers
from pymongo.errors import DuplicateKeyError
from app import decorators
from app.exceptions import raise_invalid_api_usage, raise_not_found
from bson.objectid import ObjectId


resource_model = ResourceModel()

def is_resource_id_valid(resource_id):
    return ObjectId.is_valid(resource_id)

@decorators.crossdomain()
@decorators.to_json
def get_list():
    return resource_model.get_all_resources()

@decorators.crossdomain()
@decorators.to_json
def create():
    error_missing_fields = {'error': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    data, error = serializers.Resource().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        new_resource = resource_model.create(request.json['endpoint'], request.json['methods'], request.json['response'])
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    return new_resource

@decorators.crossdomain()
@decorators.to_json
def delete(resource_id):
    if not is_resource_id_valid(resource_id):
        raise_not_found()

    deleted = resource_model.delete(resource_id)

    if deleted:
        return {}

    # such id does not exist
    return raise_not_found()

@decorators.crossdomain()
@decorators.to_json
def partial_update(resource_id):
    if not is_resource_id_valid(resource_id):
        raise_not_found()

    error_missing_fields = {'error': 'expecting at least one field.'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    fields_to_update, error = serializers.PartialResource().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)
    elif not fields_to_update:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        patched_resource = resource_model.patch(resource_id, fields_to_update)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    return patched_resource

@decorators.crossdomain()
@decorators.to_json
def save(resource_id):
    if not is_resource_id_valid(resource_id):
        raise_not_found()

    error_missing_fields = {'error': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    updated_resource, error = serializers.Resource().load(incoming_json)

    if error:
        raise_invalid_api_usage(error)
    elif not updated_resource:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        updated_resource = resource_model.replace(resource_id, updated_resource)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    return updated_resource
