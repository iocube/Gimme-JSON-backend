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


class Development(BaseSettings):
    DEBUG = True
    MONGODB_NAME = 'gimmejsondb'


class Testing(BaseSettings):
    TESTING = True
    MONGODB_NAME = 'test_gimmejsondb'

settings_choices = {
    'default': Development,
    'development': Development,
    'testing': Testing
}

settings_name = os.environ.get('GIMMEJSON_SETTINGS', 'default')
settings = settings_choices[settings_name]
