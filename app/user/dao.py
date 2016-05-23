import hmac
import hashlib
import datetime
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from settings import settings
from app.dao import BaseDAO
from app.database import database
from app.util import generate_random_string


class InvalidCredentials(Exception):
    pass


class InvalidSession(Exception):
    pass


class SessionExpired(Exception):
    pass


class SessionDAO():
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_SESSION]
        self.user = UserDAO()

    def create(self, username, password, ip, user_agent):
        user = self.user.find(username)
        if not user or not self.user.is_password_valid(user['password'], password):
            raise InvalidCredentials()

        expires = datetime.datetime.now() + datetime.timedelta(hours=6)
        new_session = {'sessionId': self._generate_session_id(),
                       'expires': expires,
                       'userId': user['_id'],
                       'ip': ip,
                       'userAgent': user_agent.string}

        self.collection.find_one_and_replace(
            {'userId': user['_id']},
            new_session,
            upsert=True
        )

        return self._encode_session_id(new_session['sessionId']), expires

    def is_user_has_active_session(self, username):
        return self.collection.find_one({'username': username})

    def _generate_session_id(self):
        random_session_id = generate_random_string(length=32)
        sha512 = hashlib.sha512()
        sha512.update(random_session_id)
        return sha512.hexdigest()

    def _encode_session_id(self, session_id):
        # TODO: create SECRET_KEY
        verification_code = hmac.new(settings.SECRET_KEY, session_id, hashlib.sha512)
        return '{0}|{1}'.format(session_id, verification_code.hexdigest())

    def validate_session(self, encoded_session, ip, user_agent):
        session_id = self._decode_session_id(encoded_session)
        session = self.collection.find_one({'sessionId': session_id})

        if session['expires'] <= datetime.datetime.now():
            self.collection.delete_one({'sessionId': session['sessionId']})
            raise SessionExpired()
        elif session['ip'] != ip or session['userAgent'] != user_agent.string:
            self.collection.delete_one({'sessionId': session['sessionId']})
            raise InvalidSession()

        return session

    def _decode_session_id(self, encoded_session):
        try:
            session_id, verification_code = encoded_session.split('|')
        except ValueError:
            raise InvalidSession()

        original_verification_code = hmac.new(settings.SECRET_KEY, session_id, hashlib.sha512)

        if not hmac.compare_digest(str(verification_code), original_verification_code.hexdigest()):
            raise InvalidSession()

        return session_id

class UserDAO(BaseDAO):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_USER]

    def create(self, new_user):
        existing_user = self.collection.find_one({'username': new_user['username']})

        if existing_user:
            raise DuplicateKeyError('Such username is already taken')

        new_user['password'] = generate_password_hash(new_user['password'])

        self.collection.insert_one(new_user)

    def is_password_valid(self, password_a, password_b):
        return check_password_hash(password_a, password_b)

    def find(self, username):
        return self.collection.find_one({'username': username})