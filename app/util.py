import random
import string

from bson import json_util, objectid


LOWER_CASE_AND_DIGITS = string.ascii_lowercase + string.digits


def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)


def is_object_id_valid(object_id):
    return objectid.ObjectId.is_valid(object_id)

def generate_string(chars=LOWER_CASE_AND_DIGITS, length=32):
    sys_random = random.SystemRandom()
    return ''.join([sys_random.choice(chars) for i in xrange(length)])