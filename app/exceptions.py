from flask import abort
from app.http_status_codes import HTTP_NOT_FOUND, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED


class BaseHTTPError(Exception):
    def __init__(self, response, http_status_code):
        self.code = http_status_code
        self.response = {
            'status': http_status_code,
            'error': response
        }


class ValidationError(Exception):
    def __init__(self, field_errors, non_field_errors):
        self.code = HTTP_BAD_REQUEST
        self.response = {
            'status': self.code,
            'field_errors': field_errors,  # errors specific to particular field
            'non_field_errors': non_field_errors  # general errors
        }


def raise_validation_error(field_errors=None, non_field_errors=None):
    raise ValidationError(field_errors, non_field_errors)


def raise_not_found():
    abort(HTTP_NOT_FOUND)


def raise_unauthorized():
    abort(HTTP_UNAUTHORIZED)
