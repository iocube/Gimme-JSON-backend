from flask import Blueprint
from app.token import api

blueprint = Blueprint('token', '__name__')

blueprint.add_url_rule('/token/', view_func=api.login, methods=['POST'])
