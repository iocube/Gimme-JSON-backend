import flask
from app import blueprints


def register_many_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

application = flask.Flask(__name__)
register_many_blueprints(application, blueprints)

if __name__ == '__main__':
    application.run(debug=True)
