from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.resource import serializers
from app.exceptions import raise_invalid_api_usage, raise_not_found
from app.resource.dao import ResourceDAO
from app.util import is_object_id_valid


resource = ResourceDAO()


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def get_list():
    resource_list = resource.get_all()
    serialized = serializers.Resource(many=True).dump(resource_list)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def create():
    error_missing_fields = {'error': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    data, error = serializers.Resource().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        new_resource = resource.create(**data)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.Resource().dump(new_resource)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def delete(resource_id):
    if not is_object_id_valid(resource_id):
        raise_not_found()

    deleted = resource.delete(resource_id)

    if deleted:
        return {}

    return raise_not_found()


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def partial_update(resource_id):
    if not is_object_id_valid(resource_id):
        raise_not_found()

    error_missing_fields = {'error': 'expecting at least one field.'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    fields_to_update, error = serializers.PartialResource(exclude=('_id',)).load(incoming_json)
    if error:
        raise_invalid_api_usage(error)
    elif not fields_to_update:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        patched_resource = resource.update(resource_id, fields_to_update)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.PartialResource().dump(patched_resource)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def save(resource_id):
    if not is_object_id_valid(resource_id):
        raise_not_found()

    error_missing_fields = {'error': 'resource should contain \'endpoint\', \'methods\' and \'response\' fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    updated_resource, error = serializers.Resource(exclude=('_id',)).load(incoming_json)

    if error:
        raise_invalid_api_usage(error)
    elif not updated_resource:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        updated_resource = resource.save(resource_id, updated_resource)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.Resource().dump(updated_resource)
    return serialized.data
