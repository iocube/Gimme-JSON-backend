FROM python:3.5.1-alpine

RUN mkdir -p /srv/application
ADD . /srv/application
WORKDIR /srv/application

# dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "gimmejson:application"]
