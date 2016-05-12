import functools
from flask import request, Response, current_app, make_response
from app.http_status_codes import HTTP_OK
from bson import json_util


def crossdomain(origin='*', methods=None, headers=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            default_options_response = current_app.make_default_options_response()

            if not methods:
                allowed_methods = default_options_response.headers['allow'].split(', ')
            else:
                allowed_methods = ', '.join(sorted(method.upper() for method in methods))

            if not headers:
                allowed_headers = 'Accept, Accept-Language, Content-Language, Content-Type'
            else:
                allowed_headers = ', '.join(headers)

            crossdomain_headers = {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': allowed_methods,
                'Access-Control-Allow-Headers': allowed_headers
            }

            if request.method == 'OPTIONS':
                default_options_response.headers.extend(crossdomain_headers)
                return default_options_response

            # TODO: func might raise BadRequest if request is invalid, this error not catched so
            # the code stops here and headers aren't set for CORS.
            crossdomain_response = func(*args, **kwargs)
            crossdomain_response.headers.extend(crossdomain_headers)

            return crossdomain_response

        # tell flask that OPTIONS requests will be handled manually by the decorator.
        wrapper.required_methods = ['OPTIONS']
        wrapper.provide_automatic_options = False
        return wrapper
    return decorator

def to_json(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_response = func(*args, **kwargs)

        if not isinstance(func_response, tuple):
            return Response(response=jsonify(func_response), mimetype='application/json')

        unpack_or_none = lambda response=None, status=HTTP_OK, headers=None: (response, status, headers)
        response, status, headers = unpack_or_none(*func_response)
        jsonfied_response = Response(response=jsonify(response), status=status, mimetype='application/json')

        if headers:
            jsonfied_response.headers.extend(headers)

        return jsonfied_response
    return wrapper

def jsonify(data):
    if hasattr(data, 'to_json'):
        return data.to_json()
    return json_util.dumps(data)
