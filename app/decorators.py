import functools
import jwt
from flask import request, Response, current_app

from app.http_status_codes import HTTP_OK
import util
from app.exceptions import raise_unauthorized
from settings import settings


def crossdomain(origin='*', methods=None, headers=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            default_options_response = current_app.make_default_options_response()

            if not methods:
                # NOTE: default_options_response might not have 'allow' header
                # for example, when there is an error handler on the application level (not on blueprint).
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

            # NOTE: func might raise an exception (i.e BadRequest), currently this error is not catched so
            # execution stops here before headers are set for CORS.
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

        if isinstance(func_response, Response):
            return func_response

        if not isinstance(func_response, tuple):
            return Response(response=util.jsonify(func_response), mimetype='application/json')

        unpack_or_none = lambda resp=None, st_code=HTTP_OK, http_headers=None: (resp, st_code, http_headers)
        response, status, headers = unpack_or_none(*func_response)
        jsonfied_response = Response(response=util.jsonify(response), status=status, mimetype='application/json')

        if headers:
            jsonfied_response.headers.extend(headers)

        return jsonfied_response
    return wrapper


def jwt_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            raise_unauthorized()

        try:
            auth_type, token = _unpack_authorization_header(request.headers['Authorization'])

            if auth_type != 'JWT':
                raise jwt.DecodeError()
            
            jwt.decode(token, settings.SECRET_KEY)
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            raise_unauthorized()

        return func(*args, **kwargs)
    return wrapper


def _unpack_authorization_header(header):
    """
    valid input: "JWT abcdef..."
    """
    if not header:
        raise jwt.DecodeError()

    try:
        auth_type, token = header.split()
        return auth_type, token
    except:
        raise jwt.DecodeError()
