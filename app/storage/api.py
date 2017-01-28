from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.storage import serializers
from app.exceptions import raise_validation_error, raise_not_found
from app.storage.dao import StorageDAO
from app.error_messages import ERR_EMPTY_PAYLOAD, ERR_DUPLICATE_VALUE, ERR_NOTHING_TO_UPDATE

storage = StorageDAO()

@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def get_list():
    storage_list = storage.get_all()
    serialized = serializers.Storage(many=True).dump(storage_list)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def get(storage_id):
    single_storage = storage.get_by_id(storage_id)
    if single_storage:
        serialized = serializers.Storage().dump(single_storage)
        return serialized.data

    return raise_not_found()


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def create():
    incoming_json = request.get_json(silent=True) or raise_validation_error(
        non_field_errors=[ERR_EMPTY_PAYLOAD]
    )

    data, error = serializers.Storage().load(incoming_json)
    if error:
        raise_validation_error(error)

    try:
        new_storage = storage.create(**data)
    except DuplicateKeyError:
        field = 'id'
        raise_validation_error(field_errors={
            field: ERR_DUPLICATE_VALUE.format(field='id')
        })

    serialized = serializers.Storage().dump(new_storage)
    return serialized.data


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def delete(storage_id):
    deleted = storage.delete(storage_id)

    if deleted:
        return {}

    return raise_not_found()

@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def save(storage_id):
    incoming_json = request.get_json(silent=True) or raise_validation_error(
        non_field_errors=[ERR_EMPTY_PAYLOAD]
    )

    incoming_storage, error = serializers.Storage(exclude=('_id',)).load(incoming_json)
    if error:
        raise_validation_error(error)
    elif not incoming_storage:
        raise_validation_error(non_field_errors=[ERR_NOTHING_TO_UPDATE])

    single_storage = storage.get_by_id(storage_id)
    if not single_storage:
        raise_not_found()

    saved_storage = storage.save(storage_id, incoming_storage)

    serialized = serializers.Storage().dump(saved_storage)
    return serialized.data
