from bson import json_util, objectid


def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)


def is_object_id_valid(object_id):
    return objectid.ObjectId.is_valid(object_id)
