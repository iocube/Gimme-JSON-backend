import json
import flask
from flask import Response, request
from app import blueprints, utility
from app.resource.model import ResourceModel
from settings import settings


def assign(source, destination):
    for k in source.keys():
        destination[k] = source[k]
    return destination

def endpoint_handler_wrapper(response):
    @utility.crossdomain(methods=['OPTIONS', 'GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
    def endpoint_handler(*args, **kwargs):
        response_dict = json.loads(response)
        return Response(response=json.dumps(response_dict), status=200, mimetype='application/json')
    return endpoint_handler

def register_many_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def register_resources(app):
    # register all resources
    resource_model = ResourceModel()
    all_resources = resource_model.get_all_resources().original()
    for resource in all_resources:
        app.add_url_rule(
            rule=resource['endpoint'],
            endpoint=str(resource['_id']),
            view_func=endpoint_handler_wrapper(resource['response']),
            methods=resource['methods']
        )

application = flask.Flask(__name__)
application.config.from_object(settings)

register_many_blueprints(application, blueprints)
register_resources(application)
