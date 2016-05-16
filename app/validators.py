from marshmallow import validate, ValidationError


class Unique(validate.Validator):
    default_message = 'Duplicate values not allowed.'

    def __init__(self, error=None):
        self.error = error or self.default_message

    def _format_error(self, value):
        return self.error.format(input=value)

    def __call__(self, value):
        hashtable = {}
        for k in value:
            if hashtable.has_key(k):
                raise ValidationError(self._format_error(value))
            hashtable[k] = k
        return value
