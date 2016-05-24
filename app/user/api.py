from flask import request
from app import decorators
from app.exceptions import raise_invalid_api_usage
from app.user import serializers
from app.user.dao import UserDAO, UsernameTaken, InvalidCredentials
from app.http_status_codes import HTTP_OK

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
        token = user.register(credentials['username'], credentials['password'])
    except UsernameTaken:
        error_already_exists = {'error': 'Username already exists.'}
        raise_invalid_api_usage(error_already_exists)

    return {}, HTTP_OK, {'Authorization': 'Bearer {0}'.format(token)}


@decorators.crossdomain()
@decorators.to_json
def login():
    error_missing_fields = {'error': 'Username and Password are required fields'}

    incoming_json = request.get_json() or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        token = user.login(credentials['username'], credentials['password'])
    except InvalidCredentials:
        error_bad_credentials = {'error': 'Bad credentials'}
        raise_invalid_api_usage(error_bad_credentials)

    return {}, HTTP_OK, {'Authorization': 'Bearer {0}'.format(token)}