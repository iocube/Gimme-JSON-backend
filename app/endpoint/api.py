from flask import request
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError

from app.decorators import to_json, crossdomain, jwt_auth_required
from app.endpoint import serializers
from app.exceptions import raise_validation_error, raise_not_found
from app.endpoint.dao import EndpointDAO
from app.util import is_object_id_valid
from app.error_messages import ERR_EMPTY_PAYLOAD, ERR_NOTHING_TO_UPDATE, ERR_DUPLICATE_VALUE

endpoint = EndpointDAO()


class EndpointCollection(MethodView):
    decorators = [
        jwt_auth_required,
        to_json,
        crossdomain()
    ]

    def get(self):
        endpoint_list = endpoint.get_all()
        serialized = serializers.Endpoint(many=True).dump(endpoint_list)
        return serialized.data

    def create(self):
        incoming_json = request.get_json(silent=True) or raise_validation_error(
            non_field_errors=[ERR_EMPTY_PAYLOAD]
        )

        data, error = serializers.Endpoint(exclude=('_id',)).load(incoming_json)
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


class EndpointEntity(MethodView):
    decorators = [
        jwt_auth_required,
        to_json,
        crossdomain()
    ]

    def get(self, endpoint_id):
        single_endpoint = endpoint.get_by_id(endpoint_id)
        if single_endpoint:
            serialized = serializers.Endpoint().dump(single_endpoint)
            return serialized.data

        return raise_not_found()

    def delete(self, endpoint_id):
        if not is_object_id_valid(endpoint_id):
            raise_not_found()

        deleted = endpoint.delete(endpoint_id)

        if deleted:
            return {}

        return raise_not_found()

    def put(self, endpoint_id):
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

    def patch(self, endpoint_id):
        if not is_object_id_valid(endpoint_id):
            raise_not_found()

        incoming_json = request.get_json(silent=True) or raise_validation_error(
            non_field_errors=[ERR_EMPTY_PAYLOAD]
        )

        fields_to_update, error = serializers.Endpoint(exclude=('_id',), partial=True).load(incoming_json)
        if error:
            raise_validation_error(error)
        elif not fields_to_update:
            raise_validation_error(non_field_errors=[ERR_NOTHING_TO_UPDATE])

        try:
            patched_endpoint = endpoint.update(endpoint_id, fields_to_update)
        except DuplicateKeyError:
            field = 'route'
            raise_validation_error(field_errors={field: ERR_DUPLICATE_VALUE.format(field=field)})

        serialized = serializers.Endpoint().dump(patched_endpoint)
        return serialized.data
