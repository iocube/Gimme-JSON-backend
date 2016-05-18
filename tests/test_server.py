import os
import unittest
import pymongo

from app import database
from client import Client
from app.http_status_codes import HTTP_OK, HTTP_BAD_REQUEST
from settings import settings


class ServerClient(Client):
    BASE_URL = '/server/'

    def restart_server(self):
        return self.client.delete(ServerClient.BASE_URL)

class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)
        database.database[settings.MONGODB_COLLECTION_RESOURCE].create_index([('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)], unique=True)
        self.client = ServerClient()

    def tearDown(self):
        pass

class ServerDELETE(BaseTest):
    def test_request_server_restart(self):
        response = self.client.restart_server()
        self.assertEqual(response.status_code, HTTP_OK)

    def test_touch_to_reload(self):
        mtime_before = os.stat(settings.TOUCH_ME_TO_RELOAD).st_mtime
        self.client.restart_server()
        mtime_after = os.stat(settings.TOUCH_ME_TO_RELOAD).st_mtime

        self.assertNotEqual(mtime_before, mtime_after)

if __name__ == '__main__':
    unittest.main()
