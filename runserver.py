import json
import flask
from flask import Response
from app import blueprints
from app.resource.model import ResourceModel


def endpoint_handler_wrapper(response):
    def endpoint_handler(*args, **kwargs):
        return Response(response=response, status=200, mimetype='application/json')
    return endpoint_handler

def register_many_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

application = flask.Flask(__name__)
register_many_blueprints(application, blueprints)

# register all resources
resource_model = ResourceModel()
all_resources = resource_model.get_all_resources().original()
for i, res in enumerate(all_resources):
    application.add_url_rule(res['endpoint'], 'resource-' + str(i), endpoint_handler_wrapper(res['response']), methods=res['methods'])

if __name__ == '__main__':
    application.run(debug=True)
