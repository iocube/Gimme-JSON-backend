import os
import unittest
import pymongo

from app import database
from client import Client
from app.http_status_codes import *
from settings import settings


class ServerClient(Client):
    BASE_URL = '/server/'

    def restart_server(self, headers=None):
        return self.client.delete(ServerClient.BASE_URL, headers=headers)

    def add_user(self, headers=None):
        return self.post('/user/', data={'username': 'admin', 'password': '123456'}, headers=headers)

    def get_token(self, headers=None):
        response = self.post('/token/', data={'username': 'admin', 'password': '123456'}, headers=headers)
        return response.json['token']


class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)
        database.database[settings.MONGODB_COLLECTION_RESOURCE].create_index(
            [('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)],
            unique=True
        )
        self.client = ServerClient()
        self.client.add_user()
        self.auth_token = self.client.get_token()
        self.auth_headers = {'Authorization': 'JWT {0}'.format(self.auth_token)}

    def tearDown(self):
        pass

    def assertUnauthorized(self, response):
        return self.assertEqual(response.status_code, HTTP_UNAUTHORIZED)

    def assertMethodNotAllowed(self, response):
        return self.assertEqual(response.status_code, HTTP_METHOD_NOT_ALLOWED)


class ServerGET(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.get(ServerClient.BASE_URL)
        self.assertMethodNotAllowed(response)


class ServerPOST(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.post(ServerClient.BASE_URL)
        self.assertMethodNotAllowed(response)


class ServerDELETE(BaseTest):
    def test_request_server_restart(self):
        response = self.client.restart_server(headers=self.auth_headers)
        self.assertEqual(response.status_code, HTTP_OK)

    def test_touch_to_reload(self):
        mtime_before = os.stat(settings.TOUCH_ME_TO_RELOAD).st_mtime
        self.client.restart_server(headers=self.auth_headers)
        mtime_after = os.stat(settings.TOUCH_ME_TO_RELOAD).st_mtime

        self.assertNotEqual(mtime_before, mtime_after)

    def test_return_unauthorized(self):
        response = self.client.restart_server()
        self.assertUnauthorized(response)


class ServerPATCH(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.patch(ServerClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)


class ServerPUT(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.put(ServerClient.BASE_URL, data={})
        self.assertMethodNotAllowed(response)

if __name__ == '__main__':
    unittest.main()
