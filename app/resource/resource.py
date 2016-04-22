import json
from flask import Blueprint, request, Response
from model import ResourceModel


HTTP_OK = 200
HTTP_BAD_REQUEST = 400

blueprint = Blueprint('resource', __name__)
resource_model = ResourceModel()

def select_from(target, what):
    properties = {key: val for key, val in target.iteritems() if key in what}
    return properties

@blueprint.route('/resource', methods=['GET'])
def get_resources_list():
    return Response(
        response=resource_model.get_all_resources().to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )

@blueprint.route('/resource', methods=['POST'])
def create_new_resource():
    payload = request.json
    payload['methods'].sort()
    new_resource = resource_model.create(payload['endpoint'], payload['methods'], payload['response'], payload['queryParams'])
    return Response(
        response=new_resource.to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )

@blueprint.route('/resource/<string:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    resource_model.delete(resource_id)
    return Response(
        response = '{}',
        status=HTTP_OK,
        mimetype='application/json'
    )

@blueprint.route('/resource/<string:resource_id>', methods=['PATCH'])
def patch_resource(resource_id):
    properties_to_update = select_from(request.json, ['endpoint', 'methods', 'response', 'queryParams'])
    patched_resource = resource_model.patch(resource_id, properties_to_update)
    return Response(
        response=patched_resource.to_json(),
        status=HTTP_OK,
        mimetype='application/json'
    )
