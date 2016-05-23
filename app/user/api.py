from flask import request
from pymongo.errors import DuplicateKeyError
from app import decorators
from app.exceptions import raise_invalid_api_usage
from app.user import serializers
from app.user.dao import UserDAO, InvalidCredentials


user = UserDAO()


@decorators.crossdomain()
@decorators.to_json
def registration():
    error_missing_fields = {'error': 'Username and Password are required fields'}
    incoming_json = request.get_json() or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        user.register(credentials['username'], credentials['password'])
    except DuplicateKeyError:
        error_already_exists = {'error': 'Username already exists.'}

    return {}

@decorators.crossdomain()
@decorators.to_json
def generate_api_key():
    error_missing_fields = {'error': 'Username and Password are required fields'}
    incoming_json = request.get_json() or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        api_key = user.generate_api_key_for_user(
            credentials['username'],
            credentials['password']
        )
    except InvalidCredentials:
        error_invalid_credentials = {'error': 'Wrong username or password.'}
        raise_invalid_api_usage(error_invalid_credentials)

    return api_key