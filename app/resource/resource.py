from flask import Blueprint, jsonify


blueprint = Blueprint('resource', __name__)

@blueprint.route('/')
def get_resource():
    return jsonify(status="OK")
