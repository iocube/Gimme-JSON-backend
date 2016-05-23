import hashlib
import hmac
from pymongo.errors import DuplicateKeyError

from settings import settings
from werkzeug.security import generate_password_hash, check_password_hash
from app.util import generate_string
from app.database import database


class InvalidCredentials(Exception):
    pass


class UserDAO(object):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_USER]

    def register(self, username, password):
        # TODO: set an index on username field
        if self.is_user_exists(username):
            raise DuplicateKeyError()

        hashed_password = generate_password_hash(password)
        self.collection.insert_one({'username': username, 'password': hashed_password})

    def is_user_exists(self, username):
        return self.collection.find_one({'username': username}) is not None

    def get_user(self, username):
        return self.collection.find_one({'username': username})

    def generate_api_key_for_user(self, username, password):
        user = self.get_user(username)
        if user is None or not check_password_hash(user['password'], password):
            raise InvalidCredentials()

        random_string = generate_string(length=16)
        user_api_key = hmac.new(settings.APPLICATION_SECRET_KEY,
                                random_string,
                                hashlib.sha1)

        self.collection.find_one_and_update(
            {'_id': user['_id']},
            {'$set': {'apiKey': user_api_key.hexdigest()}}
        )

        return {'apiKey': user_api_key.hexdigest()}

    def is_valid_api_key(self, user_api_key):
        return self.collection.find_one({'apiKey': user_api_key}) is not None
