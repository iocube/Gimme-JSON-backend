from flask import Blueprint
from app.user import api

blueprint = Blueprint('user', __name__)

blueprint.add_url_rule('/registration/', view_func=api.registration, methods=['POST'])
blueprint.add_url_rule('/login/', view_func=api.login, methods=['POST'])