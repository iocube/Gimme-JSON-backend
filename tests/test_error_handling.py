import unittest
from app.http_status_codes import HTTP_NOT_FOUND
from client import Client

class ApplicationErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def assertNotFound(self, response):
        return self.assertEqual(response.status_code, HTTP_NOT_FOUND)

    def assertJSONResponse(self, response):
        return self.assertIsInstance(response.json, dict)

    def assertStatusIs(self, response, status_code):
        return self.assertEqual(response.status_code, status_code)

    def test_return_not_found(self):
        response = self.client.get('/unknown')
        self.assertNotFound(response)

    def test_return_jsonified_error_if_not_found(self):
        response = self.client.get('/unknown')
        self.assertJSONResponse(response)

    def test_return_404_code(self):
        response = self.client.get('/unknown')
        self.assertNotFound(response)
