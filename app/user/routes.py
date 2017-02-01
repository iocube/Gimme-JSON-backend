from flask import Blueprint
from app.user import api

blueprint = Blueprint('user', __name__)

blueprint.add_url_rule('/user/', view_func=api.UserCollection.as_view('user_collection'))
