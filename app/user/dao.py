from settings import settings
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import database


class UsernameTaken(Exception):
    pass


class UserDAO(object):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_USER]

    def create(self, username, password):
        # TODO: set an index on username field
        if self.is_user_exists(username):
            raise UsernameTaken()

        hashed_password = generate_password_hash(password)
        self.collection.insert_one({'username': username, 'password': hashed_password})

    def is_user_exists(self, username):
        return self.collection.find_one({'username': username}) is not None

    def is_valid_credentials(self, username, password):
        user = self.collection.find_one({'username': username})

        if not user or not check_password_hash(user['password'], password):
            return False

        return True
