import datetime
import jwt

from settings import settings
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import database


class InvalidCredentials(Exception):
    pass


class UsernameTaken(Exception):
    pass

class UserDAO(object):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_USER]

    def register(self, username, password):
        # TODO: set an index on username field
        if self.is_user_exists(username):
            raise UsernameTaken()

        hashed_password = generate_password_hash(password)
        self.collection.insert_one({'username': username, 'password': hashed_password})
        return self.generate_jwt_token()

    def is_user_exists(self, username):
        return self.collection.find_one({'username': username}) is not None

    def login(self, username, password):
        user = self.collection.find_one({'username': username})

        if not user or not check_password_hash(user['password'], password):
            raise InvalidCredentials

        return self.generate_jwt_token()

    def generate_jwt_token(self):
        #TODO: Read secret key from settings
        encoded = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
            'SECRET_KEY'
        )

        return encoded