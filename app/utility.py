import functools
from flask import request, Response


def crossdomain(func):
    @functools.wraps(func)
    def crossdomain_wrapper(*args, **kwargs):
        allowed_methods = ', '.join(sorted(method.upper() for method in request.url_rule.methods))
        crossdomain_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': allowed_methods
        }

        if request.method == 'OPTIONS':
            return Response(headers=crossdomain_headers)

        crossdomain_response = func(*args, **kwargs)

        for key in crossdomain_headers.keys():
            crossdomain_response.headers[key] = crossdomain_headers[key]

        return crossdomain_response

    # tell flask that OPTIONS requests will be handled manually by the decorator.
    crossdomain_wrapper.required_methods = ['OPTIONS']
    crossdomain_wrapper.provide_automatic_options = False

    return crossdomain_wrapper
