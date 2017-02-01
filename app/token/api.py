from flask import request
from flask.views import MethodView

from app.decorators import to_json, crossdomain
from app.exceptions import raise_validation_error
from app.token import serializers
from app.token.dao import TokenDAO
from app.user.dao import UserDAO
from app.error_messages import ERR_EMPTY_PAYLOAD

token = TokenDAO()
user = UserDAO()


class TokenCollection(MethodView):
    decorators = [
        to_json,
        crossdomain()
    ]

    def post(self):
        incoming_json = request.get_json(silent=True) or raise_validation_error(
            non_field_errors=[ERR_EMPTY_PAYLOAD]
        )

        credentials, error = serializers.Token().load(incoming_json)
        if error:
            raise_validation_error(field_errors=error)

        if user.is_valid_credentials(credentials['username'], credentials['password']):
            return {'token': token.generate_jwt_token().decode('utf-8')}

        raise_validation_error(non_field_errors=['Invalid username or password'])
