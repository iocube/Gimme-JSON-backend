import json
import flask
from flask import Response
from app import blueprints
from settings import settings
from app import decorators
from app.http_status_codes import *
from app.exceptions import InvalidAPIUsage
from app.endpoint.dao import EndpointDAO


def assign(source, destination):
    for k in source.keys():
        destination[k] = source[k]
    return destination


def endpoint_handler_wrapper(response):
    @decorators.crossdomain(methods=['OPTIONS', 'GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
    def endpoint_handler(*args, **kwargs):
        response_dict = json.loads(response)
        return Response(response=json.dumps(response_dict), status=200, mimetype='application/json')
    return endpoint_handler


def register_many_blueprints(app, blueprint_list):
    for blueprint in blueprint_list:
        app.register_blueprint(blueprint)


def register_endpoints(app):
    # register all endpoints
    endpoint = EndpointDAO()
    all_endpoints = endpoint.get_all()
    for endpoint in all_endpoints:
        app.add_url_rule(
            rule=endpoint['endpoint'],
            endpoint=str(endpoint['_id']),
            view_func=endpoint_handler_wrapper(endpoint['response']),
            methods=endpoint['methods']
        )

application = flask.Flask(__name__)
application.config.from_object(settings)

register_many_blueprints(application, blueprints)
register_endpoints(application)


@application.errorhandler(HTTP_NOT_FOUND)
@decorators.crossdomain(methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
@decorators.to_json
def handle_not_found(error):
    return {'status': error.code}, error.code


@application.errorhandler(HTTP_METHOD_NOT_ALLOWED)
@decorators.crossdomain()
@decorators.to_json
def handle_method_not_allowed(error):
    status = error.code
    headers = {'Allow': ', '.join(error.valid_methods)}
    response = {'status': status}
    return response, status, headers


@application.errorhandler(InvalidAPIUsage)
@decorators.crossdomain()
@decorators.to_json
def handle_invalid_api_usage(error):
    return error.message, error.code


@application.errorhandler(HTTP_BAD_REQUEST)
@decorators.crossdomain()
@decorators.to_json
def handle_bad_request(error):
    return {'status': error.code}, error.code


@application.errorhandler(HTTP_INTERNAL_SERVER_ERROR)
@decorators.crossdomain()
@decorators.to_json
def handle_internal_server_error(error):
    return {'status': error.code}, error.code


@application.errorhandler(HTTP_UNAUTHORIZED)
@decorators.crossdomain()
@decorators.to_json
def handle_unauthorized(error):
    return {'status': error.code}, error.code