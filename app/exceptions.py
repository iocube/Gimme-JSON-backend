from flask import abort
from app.http_status_codes import HTTP_NOT_FOUND, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED


class BaseHTTPException(Exception):
    code = None

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.message['status'] = self.status_code


class InvalidAPIUsage(BaseHTTPException):
    code = 400


def raise_invalid_api_usage(message=None):
    raise InvalidAPIUsage(message, HTTP_BAD_REQUEST)


def raise_not_found():
    abort(HTTP_NOT_FOUND)


def raise_unauthorized():
    abort(HTTP_UNAUTHORIZED)