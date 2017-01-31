from app.storage import api
from flask import Blueprint


blueprint = Blueprint('storage', __name__)

blueprint.add_url_rule('/storage/', view_func=api.StorageCollection.as_view('storage_collection'))
blueprint.add_url_rule('/storage/<string:storage_id>', view_func=api.StorageEntity.as_view('storage_entity'))
