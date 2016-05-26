import random
from bson import json_util, objectid


def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)


def is_object_id_valid(object_id):
    return objectid.ObjectId.is_valid(object_id)


def generate_string(chars, length=32):
    sys_random = random.SystemRandom()
    return ''.join([sys_random.choice(chars) for i in xrange(length)])
