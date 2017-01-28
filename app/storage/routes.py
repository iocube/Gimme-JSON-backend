from app.storage import api
from flask import Blueprint


blueprint = Blueprint('storage', __name__)

blueprint.add_url_rule('/storage/', view_func=api.get_list, methods=['GET'])
blueprint.add_url_rule('/storage/<string:storage_id>', view_func=api.get, methods=['GET'])
blueprint.add_url_rule('/storage/', view_func=api.create, methods=['POST'])
blueprint.add_url_rule('/storage/<string:storage_id>', view_func=api.delete, methods=['DELETE'])
blueprint.add_url_rule('/storage/<string:storage_id>', view_func=api.save, methods=['PUT'])
