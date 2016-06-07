FROM python:3.5.1-alpine

RUN mkdir -p /srv/webapp
ADD . /srv/webapp
WORKDIR /srv/webapp

# dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-file", "/var/log/gunicorn.log", "--access-logfile", "/var/log/gunicorn.access.log", "--error-logfile", "/var/log/gunicorn.error.log", "gimmejson:application"]
