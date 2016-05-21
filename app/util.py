from bson import json_util, objectid
from bson.objectid import ObjectId

def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)

def is_object_id_valid(objectId):
    return objectid.ObjectId.is_valid(objectId)
