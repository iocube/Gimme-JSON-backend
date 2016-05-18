from flask import abort
from app.http_status_codes import HTTP_NOT_FOUND, HTTP_BAD_REQUEST


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.message['status'] = self.status_code

def raise_bad_request(msg={}):
    raise InvalidAPIUsage(msg, HTTP_BAD_REQUEST)

def raise_not_found():
    abort(HTTP_NOT_FOUND)
