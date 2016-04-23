import json
import re
from bson.objectid import ObjectId


def is_endpoint_field_valid(endpoint):
    if len(endpoint) == 0:
        return False
    elif re.search(r'\s', endpoint):
        return False
    return True

def is_resource_id_valid(resource_id):
    return ObjectId.is_valid(resource_id)

def is_methods_field_valid(methods):
    VALID_HTTP_METHODS = ['GET', 'POST', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

    if not isinstance(methods, list) or len(methods) == 0:
        return False

    # methods field should contain only valid fields
    for method in methods:
        if not method in VALID_HTTP_METHODS:
            return False
    return True

def is_response_field_valid(response):
    try:
        json.loads(response)
    except:
        return False
    return True
