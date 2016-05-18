from app.server import api
from flask import Blueprint


blueprint = Blueprint('server', __name__)

blueprint.add_url_rule('/server/', view_func=api.server_reload, methods=['DELETE'])
