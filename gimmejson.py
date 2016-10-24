import flask

from app import blueprints
from settings import settings
from app import decorators
from app.http_status_codes import *
from app.exceptions import InvalidAPIUsage


def register_many_blueprints(app, blueprint_list):
    for blueprint in blueprint_list:
        app.register_blueprint(blueprint)


application = flask.Flask(__name__)
application.config.from_object(settings)

register_many_blueprints(application, blueprints)

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