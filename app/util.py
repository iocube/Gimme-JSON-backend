from bson import json_util


def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)
