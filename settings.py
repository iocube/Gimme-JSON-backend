import os
import datetime


class BaseSettings(object):
    DEBUG = False
    TESTING = False
    TOUCH_ME_TO_RELOAD = 'settings.py'
    SECRET_KEY = os.environ.get('GIMMEJSON_SECRET_KEY', None)
    DATABASE_HOST = os.environ.get('GIMMEJSON_DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.environ.get('GIMMEJSON_DATABASE_PORT', 27017)
    JWT_TOKEN_EXPIRE_IN = datetime.timedelta(hours=8)
    IS_AUTH_REQUIRED = False


class Development(BaseSettings):
    DEBUG = True
    MONGODB_NAME = 'gimmejsondb'


class Testing(BaseSettings):
    TESTING = True
    IS_AUTH_REQUIRED = True
    MONGODB_NAME = 'test_gimmejsondb'

settings = Development
