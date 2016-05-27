import json
from gimmejson import application


class Client(object):
    """
    Wrapper for test_client().
    This class ensures that each client request is converted to json and appropriate mime type is set.

    """
    def __init__(self):
        self.client = application.test_client()

    def get(self, *args, **kwargs):
        return self._http_call(self.client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._http_call(self.client.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._http_call(self.client.put, *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._http_call(self.client.patch, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._http_call(self.client.delete, *args, **kwargs)

    def _http_call(self, method_func, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
            kwargs['content_type'] = 'application/json'
            response = method_func(*args, **kwargs)
        else:
            response = method_func(*args, **kwargs)
        # might raise ValueError: No JSON object could be decoded
        try:
            response.json = json.loads(response.get_data().decode('utf-8'))
        except ValueError:
            # couldn't decode.
            response.json = False

        return response
