import datetime

import jwt
from settings import settings


class TokenDAO(object):
    def __init__(self):
        self.collection = None

    def generate_jwt_token(self):
        return jwt.encode(
            {'exp': datetime.datetime.utcnow() + settings.JWT_TOKEN_EXPIRE_IN},
            settings.SECRET_KEY
        )
