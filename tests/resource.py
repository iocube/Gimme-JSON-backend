import json
import unittest
from gimmejson import application
from app import database

# pythom -m tests.resource
class ResourceTest(unittest.TestCase):
    def setUp(self):
        self.client = application.test_client()

    def tearDown(self):
        pass

    def test_get_all_resources(self):
        response = self.client.get('/resource')
        all_resources = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
