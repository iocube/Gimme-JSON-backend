import unittest

from app import database
from app.http_status_codes import *
from settings import settings
from tests.client import Client
import manage


class EndpointClient(Client):
    """
    Shortcut methods to work with 'endpoint' resource
    """
    BASE_URL = '/endpoint/'

    def create_endpoint(self, payload, headers=None):
        return self.post(EndpointClient.BASE_URL, data=payload, headers=headers)

    def delete_endpoint(self, endpoint_id, headers=None):
        return self.delete(EndpointClient.BASE_URL + endpoint_id + '/', headers=headers)

    def save_changes(self, endpoint_id, changes, headers=None):
        return self.patch(EndpointClient.BASE_URL + endpoint_id + '/', data=changes, headers=headers)

    def save(self, endpoint_id, payload, headers=None):
        return self.put(EndpointClient.BASE_URL + endpoint_id + '/', data=payload, headers=headers)

    def add_user(self, headers=None):
        return self.post('/user/', data={'username': 'admin', 'password': '12345678'}, headers=headers)

    def get_token(self, headers=None):
        response = self.post('/token/', data={'username': 'admin', 'password': '12345678'}, headers=headers)
        return response.json['token']


class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)

        # create all indexes
        manage.index()

        self.client = EndpointClient()
        self.payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }
        self.client.add_user()
        self.auth_token = self.client.get_token()
        self.auth_headers = {'Authorization': 'JWT {0}'.format(self.auth_token)}

    def tearDown(self):
        pass

    def assertOK(self, response):
        return self.assertEqual(response.status_code, HTTP_OK)

    def assertBadRequest(self, response):
        return self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def assertNotFound(self, response):
        return self.assertEqual(response.status_code, HTTP_NOT_FOUND)

    def assertUnauthorized(self, response):
        return self.assertEqual(response.status_code, HTTP_UNAUTHORIZED)


class EndpointGET(BaseTest):
    def test_get_endpoint_list(self):
        response = self.client.get(EndpointClient.BASE_URL, headers=self.auth_headers)

        self.assertEqual(response.status_code, HTTP_OK)

    def test_return_unauthorized(self):
        response = self.client.get(EndpointClient.BASE_URL)
        self.assertUnauthorized(response)


class EndpointPOST(BaseTest):
    def test_create_new_endpoint(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        self.assertOK(response)

    def test_allocate_id_for_endpoint(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        self.assertIn('_id', response.json)

    def test_return_error_if_endpoint_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_response_missing(self):
        payload = {
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('response', response.json)

    def test_return_error_if_duplicate_endpoints_and_methods(self):
        """
        should return error if such endpoint and method is already exist when creating new endpoint
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET",
              "POST"
            ]
        }

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertOK(response)

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_methods_are_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test"
        }

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('methods', response.json)

    def test_return_error_if_all_fields_missing(self):
        payload = {}

        response = self.client.create_endpoint(payload, headers=self.auth_headers)
        self.assertBadRequest(response)

        response = self.client.create_endpoint(None, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_endpoint(self.payload)
        self.assertUnauthorized(response)


class EndpointDELETE(BaseTest):
    def test_delete_endpoint(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        new_endpoint_id = response.json['_id']

        response = self.client.delete_endpoint(new_endpoint_id, headers=self.auth_headers)
        self.assertOK(response)

    def test_delete_unexistent_endpoint(self):
        response = self.client.delete_endpoint('571b7cfdeceefb4a395ef433', headers=self.auth_headers)
        self.assertNotFound(response)

    def test_return_unauthorized(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        new_endpoint_id = response.json['_id']

        response = self.client.delete_endpoint(new_endpoint_id, self.payload)
        self.assertUnauthorized(response)


class EndpointPATCH(BaseTest):
    def test_edit_all_fields(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        endpoint_id = response.json['_id']

        new_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Tel-Aviv\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "POST"
            ]
        }

        response = self.client.save_changes(endpoint_id, new_payload, headers=self.auth_headers)

        patched_endpoint = response.json
        new_payload['_id'] = patched_endpoint['_id']

        self.assertOK(response)
        self.assertEqual(patched_endpoint, new_payload)

    def test_return_error_if_duplicate_endpoints_and_methods(self):
        """
        should return error if such endpoint and methods already exist
        when trying to modify existing endpoint
        """
        payload_second = {
            "response": "{\"name\": \"Bob\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "GET"
            ]
        }

        self.client.create_endpoint(self.payload, headers=self.auth_headers)
        response = self.client.create_endpoint(payload_second, headers=self.auth_headers)

        endpoint_to_patch = response.json
        endpoint_id = endpoint_to_patch['_id']

        endpoint_to_patch['endpoint'] = '/api/v1/test'

        response = self.client.save_changes(endpoint_id, endpoint_to_patch, headers=self.auth_headers)

        self.assertBadRequest(response)
        self.assertIn('endpoint',  response.json)

    def test_return_error_if_patching_id(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        new_endpoint = response.json
        endpoint_id = new_endpoint['_id']

        patch_payload = {
            '_id': {'$oid': '571b7cfdeceefb4a395ef433'}
        }

        response = self.client.save_changes(endpoint_id, patch_payload, headers=self.auth_headers)

        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        endpoint_id = response.json['_id']

        patch_payload = {
            'endpoint': '/api/v1/test'
        }

        response = self.client.save_changes(endpoint_id, patch_payload)

        self.assertUnauthorized(response)


class EndpointPUT(BaseTest):
    def test_save_changes(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        new_endpoint_id = response.json['_id']

        self.payload['methods'] = ['POST']
        response = self.client.save(new_endpoint_id, self.payload, headers=self.auth_headers)
        self.assertEqual(response.json['methods'], ['POST'])

    def test_ignore_id_on_put(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        self.payload['methods'] = ['POST']
        self.payload['_id'] = response.json['_id']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)

        self.assertOK(response)

    def test_return_error_if_duplicate_endpoint_and_methods(self):
        another_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "POST"
            ]
        }

        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        self.assertOK(response)

        response = self.client.create_endpoint(another_payload, headers=self.auth_headers)
        new_endpoint_id = response.json['_id']
        self.assertOK(response)

        another_payload['methods'] = ['GET']
        response = self.client.save(new_endpoint_id, another_payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_all_fields_missing(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)

        empty_payload = {}
        response = self.client.save(response.json['_id'], empty_payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_response_missing(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        del self.payload['response']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_methods_missing(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        del self.payload['methods']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_endpoint_missing(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        del self.payload['endpoint']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_endpoint(self.payload, headers=self.auth_headers)
        del self.payload['endpoint']

        response = self.client.save(response.json['_id'], self.payload)

        self.assertUnauthorized(response)


if __name__ == '__main__':
    unittest.main()
