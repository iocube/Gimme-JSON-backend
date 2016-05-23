from flask import request, Response
from pymongo.errors import DuplicateKeyError

from app import decorators
from app.exceptions import raise_invalid_api_usage
from app.user import serializers
from app.user.dao import UserDAO, SessionDAO, InvalidCredentials, InvalidSession


user = UserDAO()
session = SessionDAO()


@decorators.crossdomain()
@decorators.to_json
def registration():
    error_missing_fields = {'error': 'Username and Password are required fields.'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        user.create(credentials)
    except DuplicateKeyError:
        raise_invalid_api_usage({'username': 'This username is already taken.'})

    return {}


@decorators.crossdomain()
@decorators.to_json
def login():
    error_missing_fields = {'error': 'Username and Password are required fields.'}
    incoming_json = request.get_json(silent=True) or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.User().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    try:
        encoded_session, expires = session.create(credentials['username'],
                                         credentials['password'],
                                         request.remote_addr,
                                         request.user_agent)
    except (InvalidSession, InvalidCredentials):
        raise_invalid_api_usage({'error': 'Invalid credentials.'})

    response = Response(mimetype='application/json')
    response.set_cookie('sessionId', value=encoded_session, expires=expires)
    return response
