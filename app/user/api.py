from flask import request
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.exceptions import raise_invalid_api_usage
from app.user import serializers
from app.user.dao import UserDAO


user = UserDAO()


@decorators.crossdomain()
@decorators.to_json
def create():
    error_missing_fields = {'error': 'Username and Password are required fields.'}
    incoming_json = request.get_json() or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        user.create(credentials['username'], credentials['password'])
    except DuplicateKeyError:
        error_already_exists = {'error': 'Username already exists.'}
        raise_invalid_api_usage(error_already_exists)

    return {}
