from app.endpoint import api
from flask import Blueprint


blueprint = Blueprint('endpoint', __name__)

blueprint.add_url_rule('/endpoint/', view_func=api.EndpointCollection.as_view('endpoint_collection'))
blueprint.add_url_rule('/endpoint/<string:endpoint_id>/', view_func=api.EndpointEntity.as_view('endpoint_entity'))
