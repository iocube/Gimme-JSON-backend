import unittest
import pymongo
from app import database
from app.http_status_codes import *
from settings import settings
from client import Client


class ResourceClient(Client):
    """
    Shortcut methods to work with Resource API.
    """
    BASE_URL = '/resource/'

    def create_resource(self, payload, headers=None):
        return self.post(ResourceClient.BASE_URL, data=payload, headers=headers)

    def delete_resource(self, resource_id, headers=None):
        return self.delete(ResourceClient.BASE_URL + resource_id + '/', headers=headers)

    def save_changes(self, resource_id, changes, headers=None):
        return self.patch(ResourceClient.BASE_URL + resource_id + '/', data=changes, headers=headers)

    def save(self, resource_id, payload, headers=None):
        return self.put(ResourceClient.BASE_URL + resource_id + '/', data=payload, headers=headers)

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
        self.client = ResourceClient()
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


class ResourceGET(BaseTest):
    def test_get_resources_list(self):
        response = self.client.get(ResourceClient.BASE_URL, headers=self.auth_headers)

        self.assertEqual(response.status_code, HTTP_OK)

    def test_return_unauthorized(self):
        response = self.client.get(ResourceClient.BASE_URL)
        self.assertUnauthorized(response)


class ResourcePOST(BaseTest):
    def test_create_new_resource(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        self.assertOK(response)

    def test_allocate_id_for_resource(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        self.assertIn('_id', response.json)

    def test_return_error_if_endpoint_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_response_missing(self):
        payload = {
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('response', response.json)

    def test_return_error_if_duplicate_endpoints_and_methods(self):
        """
        should return error if such endpoint and method is already exist when creating new resource
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET",
              "POST"
            ]
        }

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertOK(response)

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_methods_are_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test"
        }

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertBadRequest(response)
        self.assertIn('methods', response.json)

    def test_return_error_if_all_fields_missing(self):
        payload = {}

        response = self.client.create_resource(payload, headers=self.auth_headers)
        self.assertBadRequest(response)

        response = self.client.create_resource(None, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_resource(self.payload)
        self.assertUnauthorized(response)


class ResourceDELETE(BaseTest):
    def test_delete_resource(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        new_resource_id = response.json['_id']

        response = self.client.delete_resource(new_resource_id, headers=self.auth_headers)
        self.assertOK(response)

    def test_delete_unexistent_resource(self):
        response = self.client.delete_resource('571b7cfdeceefb4a395ef433', headers=self.auth_headers)
        self.assertNotFound(response)

    def test_return_unauthorized(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        new_resource_id = response.json['_id']

        response = self.client.delete_resource(new_resource_id, self.payload)
        self.assertUnauthorized(response)


class ResourcePATCH(BaseTest):
    def test_edit_all_fields(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        resource_id = response.json['_id']

        new_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Tel-Aviv\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "POST"
            ]
        }

        response = self.client.save_changes(resource_id, new_payload, headers=self.auth_headers)

        patched_resource = response.json
        new_payload['_id'] = patched_resource['_id']

        self.assertOK(response)
        self.assertEqual(patched_resource, new_payload)

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

        self.client.create_resource(self.payload, headers=self.auth_headers)
        response = self.client.create_resource(payload_second, headers=self.auth_headers)

        resource_to_patch = response.json
        resource_id = resource_to_patch['_id']

        resource_to_patch['endpoint'] = '/api/v1/test'

        response = self.client.save_changes(resource_id, resource_to_patch, headers=self.auth_headers)

        self.assertBadRequest(response)
        self.assertIn('endpoint',  response.json)

    def test_return_error_if_patching_id(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        new_resource = response.json
        resource_id = new_resource['_id']

        patch_payload = {
            '_id': {'$oid': '571b7cfdeceefb4a395ef433'}
        }

        response = self.client.save_changes(resource_id, patch_payload, headers=self.auth_headers)

        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        resource_id = response.json['_id']

        patch_payload = {
            'endpoint': '/api/v1/test'
        }

        response = self.client.save_changes(resource_id, patch_payload)

        self.assertUnauthorized(response)


class ResourcePUT(BaseTest):
    def test_save_changes(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        new_resource_id = response.json['_id']

        self.payload['methods'] = ['POST']
        response = self.client.save(new_resource_id, self.payload, headers=self.auth_headers)
        self.assertEqual(response.json['methods'], ['POST'])

    def test_ignore_id_on_put(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
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

        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        self.assertOK(response)

        response = self.client.create_resource(another_payload, headers=self.auth_headers)
        new_resource_id = response.json['_id']
        self.assertOK(response)

        another_payload['methods'] = ['GET']
        response = self.client.save(new_resource_id, another_payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_all_fields_missing(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)

        empty_payload = {}
        response = self.client.save(response.json['_id'], empty_payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_response_missing(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        del self.payload['response']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_methods_missing(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        del self.payload['methods']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_error_if_endpoint_missing(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        del self.payload['endpoint']

        response = self.client.save(response.json['_id'], self.payload, headers=self.auth_headers)
        self.assertBadRequest(response)

    def test_return_unauthorized(self):
        response = self.client.create_resource(self.payload, headers=self.auth_headers)
        del self.payload['endpoint']

        response = self.client.save(response.json['_id'], self.payload)

        self.assertUnauthorized(response)


if __name__ == '__main__':
    unittest.main()
