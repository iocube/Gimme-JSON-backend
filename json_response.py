def json_response(f):
    def json_wrapper(*args, **kwargs):
        wrapped_response = f(*args, **kwargs)
        wrapped_response.mimetype = 'application/json'
        if wrapped_response.response and hasattr(wrapped_response.response, 'to_json'):
            wrapped_response.set_data(wrapped_response.response.to_json())
        return wrapped_response
    return json_wrapper
