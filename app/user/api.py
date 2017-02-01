from flask import request
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError

from app.decorators import crossdomain, to_json
from app.exceptions import raise_validation_error
from app.user import serializers
from app.user.dao import UserDAO
from app.error_messages import ERR_EMPTY_PAYLOAD

user = UserDAO()


class UserCollection(MethodView):
    decorators = [
        to_json,
        crossdomain()
    ]

    def post(self):
        incoming_json = request.get_json() or raise_validation_error(
            non_field_errors=[ERR_EMPTY_PAYLOAD]
        )

        credentials, error = serializers.User().load(incoming_json)
        if error:
            raise_validation_error(error)

        try:
            user.create(credentials['username'], credentials['password'])
        except DuplicateKeyError:
            raise_validation_error(field_errors={
                'username': 'Username already exists'
            })

        return {}
