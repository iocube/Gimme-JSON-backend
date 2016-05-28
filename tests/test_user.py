import unittest

from app import database
from tests.client import Client
from settings import settings
from app.http_status_codes import *
import manage

class UserClient(Client):
    BASE_URL = '/user/'

    def add_user(self, user):
        return self.post(UserClient.BASE_URL, data=user)


class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)

        # create all indexes
        manage.index()

        self.client = UserClient()

    def tearDown(self):
        pass

    def assertOK(self, response):
        return self.assertEqual(response.status_code, HTTP_OK)

    def assertBadRequest(self, response):
        return self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def assertMethodNotAllowed(self, response):
        return self.assertEqual(response.status_code, HTTP_METHOD_NOT_ALLOWED)


class UserGET(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.get(UserClient.BASE_URL)
        self.assertMethodNotAllowed(response)


class UserPOST(BaseTest):
    def test_create_new_user(self):
        user = {'username': 'admin', 'password': '12345678'}
        response = self.client.add_user(user)
        self.assertOK(response)

    def test_return_error_if_no_username(self):
        user = {'password': '12345678'}
        response = self.client.add_user(user)
        self.assertBadRequest(response)

    def test_return_error_if_no_password(self):
        user = {'username': 'admin'}
        response = self.client.add_user(user)
        self.assertBadRequest(response)

    def test_return_error_if_no_username_and_password(self):
        user = {}
        response = self.client.add_user(user)
        self.assertBadRequest(response)

    def test_return_error_if_username_is_taken(self):
        user = {'username': 'admin', 'password': '12345678'}
        self.client.add_user(user)

        response = self.client.add_user(user)
        self.assertBadRequest(response)

    def test_return_error_if_password_less_then_minimum(self):
        user = {'username': 'admin', 'password': '123456'}
        response = self.client.add_user(user)
        self.assertBadRequest(response)

class UserDELETE(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.delete(UserClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


class UserPATCH(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.patch(UserClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


class UserPUT(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.put(UserClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


if __name__ == '__main__':
    unittest.main()