import datetime

import jwt
from settings import settings
from app.database import database


class TokenDAO(object):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_USER]

    def generate_jwt_token(self):
        # TODO: Read secret key from settings
        return jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
            'SECRET_KEY'
        )
