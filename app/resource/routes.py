from app.resource import api
from flask import Blueprint


blueprint = Blueprint('resource', __name__)

blueprint.add_url_rule('/resource', view_func=api.get_resources_list, methods=['GET'])
blueprint.add_url_rule('/resource', view_func=api.create_new_resource, methods=['POST'])
blueprint.add_url_rule('/resource/<string:resource_id>', view_func=api.delete_resource, methods=['DELETE'])
blueprint.add_url_rule('/resource/<string:resource_id>', view_func=api.patch_resource, methods=['PATCH'])
blueprint.add_url_rule('/resource/<string:resource_id>', view_func=api.put_resource, methods=['PUT'])
