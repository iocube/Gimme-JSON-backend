from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.storage import serializers
from app.exceptions import raise_invalid_api_usage, raise_not_found
from app.storage.dao import StorageDAO


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
    error_bad_json = {'error': 'Bad JSON'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_bad_json)

    data, error = serializers.Storage().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        new_storage = storage.create(**data)
    except DuplicateKeyError:
        error_duplicate_values = {'id': 'id should be unique.'}
        raise_invalid_api_usage(error_duplicate_values)

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