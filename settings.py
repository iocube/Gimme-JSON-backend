import os


class BaseSettings(object):
    MONGODB_COLLECTION_RESOURCE = 'resources'
    TOUCH_ME_TO_RELOAD = 'settings.py'

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
