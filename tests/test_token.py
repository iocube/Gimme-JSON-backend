import unittest
import pymongo

from app import database
from tests.client import Client
from settings import settings
from app.http_status_codes import *


class TokenClient(Client):
    BASE_URL = '/token/'

    def create_token(self, user):
        return self.post(TokenClient.BASE_URL, data=user)

    def add_user(self):
        user = {'username': 'admin', 'password': '123456'}
        return self.post('/user/', data=user)


class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)
        database.database[settings.MONGODB_COLLECTION_ENDPOINT].create_index(
            [('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)],
            unique=True
        )
        self.client = TokenClient()
        self.client.add_user()

    def tearDown(self):
        pass

    def assertOK(self, response):
        return self.assertEqual(response.status_code, HTTP_OK)

    def assertBadRequest(self, response):
        return self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def assertMethodNotAllowed(self, response):
        return self.assertEqual(response.status_code, HTTP_METHOD_NOT_ALLOWED)


class TokenGET(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.get(TokenClient.BASE_URL)
        self.assertMethodNotAllowed(response)


class TokenPOST(BaseTest):
    def test_create_new_token(self):
        credentials = {'username': 'admin', 'password': '123456'}
        response = self.client.create_token(credentials)
        self.assertOK(response)
        self.assertTrue('token' in response.json)

    def test_return_error_if_bad_password(self):
        credentials = {'username': 'admin', 'password': 'abc'}
        response = self.client.create_token(credentials)
        self.assertBadRequest(response)

    def test_return_error_if_no_credentials(self):
        credentials = {}
        response = self.client.create_token(credentials)
        self.assertBadRequest(response)


class TokenDELETE(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.delete(TokenClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


class TokenPATCH(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.patch(TokenClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


class TokenPUT(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.put(TokenClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


if __name__ == '__main__':
    unittest.main()