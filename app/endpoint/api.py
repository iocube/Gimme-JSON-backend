from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.endpoint import serializers
from app.exceptions import raise_validation_error, raise_not_found
from app.endpoint.dao import EndpointDAO
from app.util import is_object_id_valid
from app.error_messages import ERR_EMPTY_PAYLOAD, ERR_NOTHING_TO_UPDATE, ERR_DUPLICATE_VALUE

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
    incoming_json = request.get_json(silent=True) or raise_validation_error(
        non_field_errors=[ERR_EMPTY_PAYLOAD]
    )

    data, error = serializers.Endpoint().load(incoming_json)
    if error:
        raise_validation_error(field_errors=error)

    try:
        new_endpoint = endpoint.create(**data)
    except DuplicateKeyError:
        field = 'route'
        raise_validation_error(field_errors={
            field: ERR_DUPLICATE_VALUE.format(field=field)
        })

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

    incoming_json = request.get_json(silent=True) or raise_validation_error(
        non_field_errors=[ERR_EMPTY_PAYLOAD]
    )

    fields_to_update, error = serializers.PartialEndpoint(exclude=('_id',)).load(incoming_json)
    if error:
        raise_validation_error(error)
    elif not fields_to_update:
        raise_validation_error(non_field_errors=[ERR_NOTHING_TO_UPDATE])

    try:
        patched_endpoint = endpoint.update(endpoint_id, fields_to_update)
    except DuplicateKeyError:
        field = 'route'
        raise_validation_error(field_errors={field: ERR_DUPLICATE_VALUE.format(field=field)})

    serialized = serializers.PartialEndpoint().dump(patched_endpoint)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def save(endpoint_id):
    if not is_object_id_valid(endpoint_id):
        raise_not_found()

    incoming_json = request.get_json(silent=True) or raise_validation_error(
        non_field_errors=[ERR_EMPTY_PAYLOAD]
    )

    updated_endpoint, error = serializers.Endpoint(exclude=('_id',)).load(incoming_json)

    if error:
        raise_validation_error(field_errors=error)
    elif not updated_endpoint:
        raise_validation_error(non_field_errors=[ERR_NOTHING_TO_UPDATE])

    try:
        updated_endpoint = endpoint.save(endpoint_id, updated_endpoint)
    except DuplicateKeyError:
        field = 'route'
        raise_validation_error(field_errors={
            field: ERR_DUPLICATE_VALUE.format(field=field)
        })

    serialized = serializers.Endpoint().dump(updated_endpoint)
    return serialized.data
