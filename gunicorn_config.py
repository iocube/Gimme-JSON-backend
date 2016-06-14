bind = ['0.0.0.0:8000']

# The number of worker processes for handling requests.
workers = 3

accesslog = '/var/log/gunicorn.access.log'
errorlog = '/var/log/gunicorn.error.log'
