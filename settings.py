import os


class BaseSettings(object):
    DEBUG = False
    TESTING = False
    MONGODB_COLLECTION_RESOURCE = 'resources'
    MONGODB_COLLECTION_USER = 'user'
    MONGODB_COLLECTION_SESSION = 'session'
    TOUCH_ME_TO_RELOAD = 'settings.py'
    SECRET_KEY = os.environ.get('GIMMEJSON_SECRET_KEY', None)


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
