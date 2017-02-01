from flask import Blueprint
from app.token import api

blueprint = Blueprint('token', '__name__')

blueprint.add_url_rule('/token/', view_func=api.TokenCollection.as_view('token_collection'))
