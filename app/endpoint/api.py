from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.endpoint import serializers
from app.exceptions import raise_invalid_api_usage, raise_not_found
from app.endpoint.dao import EndpointDAO
from app.util import is_object_id_valid


endpoint = EndpointDAO()


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def get_list():
    endpoint_list = endpoint.get_all()
    serialized = serializers.Endpoint(many=True).dump(endpoint_list)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def create():
    error_missing_fields = {'error': '\'endpoint\', \'methods\' and \'response\' are required fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    data, error = serializers.Endpoint().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        new_endpoint = endpoint.create(**data)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.Endpoint().dump(new_endpoint)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def delete(endpoint_id):
    if not is_object_id_valid(endpoint_id):
        raise_not_found()

    deleted = endpoint.delete(endpoint_id)

    if deleted:
        return {}

    return raise_not_found()


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def partial_update(endpoint_id):
    if not is_object_id_valid(endpoint_id):
        raise_not_found()

    error_missing_fields = {'error': 'expecting at least one field.'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    fields_to_update, error = serializers.PartialEndpoint(exclude=('_id',)).load(incoming_json)
    if error:
        raise_invalid_api_usage(error)
    elif not fields_to_update:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        patched_endpoint = endpoint.update(endpoint_id, fields_to_update)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.PartialEndpoint().dump(patched_endpoint)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def save(endpoint_id):
    if not is_object_id_valid(endpoint_id):
        raise_not_found()

    error_missing_fields = {'error': '\'endpoint\', \'methods\' and \'response\' are required fields'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    updated_endpoint, error = serializers.Endpoint(exclude=('_id',)).load(incoming_json)

    if error:
        raise_invalid_api_usage(error)
    elif not updated_endpoint:
        error_nothing_to_update = {'error': 'Nothing to update.'}
        raise_invalid_api_usage(error_nothing_to_update)

    try:
        updated_endpoint = endpoint.save(endpoint_id, updated_endpoint)
    except DuplicateKeyError:
        error_duplicate_values = {'endpoint': 'Each endpoint should have unique methods.'}
        raise_invalid_api_usage(error_duplicate_values)

    serialized = serializers.Endpoint().dump(updated_endpoint)
    return serialized.data
