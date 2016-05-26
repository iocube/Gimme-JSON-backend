from flask import request
from app import decorators
from app.exceptions import raise_invalid_api_usage
from app.token import serializers
from app.token.dao import TokenDAO
from app.user.dao import UserDAO


token = TokenDAO()
user = UserDAO()


@decorators.crossdomain()
@decorators.to_json
def create():
    error_missing_fields = {'error': 'Username and Password are required fields.'}
    incoming_json = request.get_json() or raise_invalid_api_usage(error_missing_fields)

    credentials, error = serializers.Token().load(incoming_json)
    if error:
        raise_invalid_api_usage(error)

    if user.is_valid_credentials(credentials['username'], credentials['password']):
        return {'token': token.generate_jwt_token()}

    raise_invalid_api_usage({'error': 'Bad credentials.'})
