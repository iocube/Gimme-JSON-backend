FROM python:3.5.1-alpine

# source code
RUN mkdir -p /srv/webapp
ADD . /srv/webapp
WORKDIR /srv/webapp

# dependencies
RUN pip install -r requirements.txt

CMD gunicorn --config gunicorn_config.py gimmejson:application
