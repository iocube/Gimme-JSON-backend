from marshmallow import validate, ValidationError


class Unique(validate.Validator):
    default_message = 'Duplicate values not allowed.'

    def __init__(self, error=None):
        self.error = error or self.default_message

    def _format_error(self, value):
        return self.error.format(input=value)

    def __call__(self, value):
        hash_table = {}
        for k in value:
            if k in hash_table:
                raise ValidationError(self._format_error(value))
            hash_table[k] = k
        return value
