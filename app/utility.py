import functools
from flask import request, Response, current_app, make_response
from werkzeug.exceptions import BadRequest

def crossdomain(*args, **kwargs):
    methods = kwargs['methods']
    methods.append('OPTIONS')

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print "methods: {methods}".format(methods=methods)
            allowed_methods = ', '.join(sorted(method.upper() for method in methods))
            crossdomain_headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': allowed_methods
            }

            if request.method == 'OPTIONS':
                default_options_response = current_app.make_default_options_response()
                default_options_response.headers['Access-Control-Allow-Origin'] = crossdomain_headers['Access-Control-Allow-Origin']
                default_options_response.headers['Access-Control-Allow-Methods'] = crossdomain_headers['Access-Control-Allow-Methods']
                default_options_response.headers['Access-Control-Allow-Headers'] = 'Accept, Accept-Language, Content-Language, Content-Type'
                return default_options_response

            # TODO: func might raise BadRequest if request is invalid, this error not catched so
            # the code stops here and headers aren't set for CORS.
            crossdomain_response = func(*args, **kwargs)

            for key in crossdomain_headers.keys():
                crossdomain_response.headers[key] = crossdomain_headers[key]

            return crossdomain_response

        # tell flask that OPTIONS requests will be handled manually by the decorator.
        wrapper.required_methods = ['OPTIONS']
        wrapper.provide_automatic_options = False
        return wrapper
    return decorator
