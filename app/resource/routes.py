from app.resource import api
from flask import Blueprint


blueprint = Blueprint('resource', __name__)

blueprint.add_url_rule('/resource/', view_func=api.get_list, methods=['GET'])
blueprint.add_url_rule('/resource/', view_func=api.create, methods=['POST'])
blueprint.add_url_rule('/resource/<string:resource_id>/', view_func=api.delete, methods=['DELETE'])
blueprint.add_url_rule('/resource/<string:resource_id>/', view_func=api.partial_update, methods=['PATCH'])
blueprint.add_url_rule('/resource/<string:resource_id>/', view_func=api.save, methods=['PUT'])
