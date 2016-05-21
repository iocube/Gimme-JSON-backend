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

    def create_resource(self, payload):
        return self.post(ResourceClient.BASE_URL, data=payload)

    def delete_resource(self, resource_id):
        return self.delete(ResourceClient.BASE_URL + resource_id + '/')

    def save_changes(self, resource_id, changes):
        return self.patch(ResourceClient.BASE_URL + resource_id + '/', data=changes)

    def save(self, resource_id, payload):
        return self.put(ResourceClient.BASE_URL + resource_id + '/', data=payload)


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

    def tearDown(self):
        pass

    def assertOK(self, response):
        return self.assertEqual(response.status_code, HTTP_OK)

    def assertBadRequest(self, response):
        return self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def assertNotFound(self, response):
        return self.assertEqual(response.status_code, HTTP_NOT_FOUND)


class ResourceGET(BaseTest):
    def test_get_resources_list(self):
        response = self.client.get('/resource/')

        self.assertEqual(response.status_code, HTTP_OK)


class ResourcePOST(BaseTest):
    def test_create_new_resource(self):
        response = self.client.create_resource(self.payload)
        self.assertOK(response)

    def test_allocate_id_for_resource(self):
        response = self.client.create_resource(self.payload)
        self.assertIn('_id', response.json)

    def test_return_error_if_endpoint_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_resource(payload)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_response_missing(self):
        payload = {
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.create_resource(payload)
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

        response = self.client.create_resource(payload)
        self.assertOK(response)

        response = self.client.create_resource(payload)
        self.assertBadRequest(response)
        self.assertIn('endpoint', response.json)

    def test_return_error_if_methods_are_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test"
        }

        response = self.client.create_resource(payload)
        self.assertBadRequest(response)
        self.assertIn('methods', response.json)

    def test_return_error_if_all_fields_missing(self):
        payload = {}

        response = self.client.create_resource(payload)
        self.assertBadRequest(response)

        response = self.client.create_resource(None)
        self.assertBadRequest(response)


class ResourceDELETE(BaseTest):
    def test_delete_resource(self):
        response = self.client.create_resource(self.payload)
        new_resource_id = response.json['_id']

        response = self.client.delete_resource(new_resource_id)
        self.assertOK(response)

    def test_delete_unexistent_resource(self):
        response = self.client.delete_resource('571b7cfdeceefb4a395ef433')
        self.assertNotFound(response)


class ResourcePATCH(BaseTest):
    def test_edit_all_fields(self):
        response = self.client.create_resource(self.payload)
        resource_id = response.json['_id']

        new_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Tel-Aviv\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "POST"
            ]
        }

        response = self.client.save_changes(resource_id, new_payload)

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

        self.client.create_resource(self.payload)
        response = self.client.create_resource(payload_second)

        resource_to_patch = response.json
        resource_id = resource_to_patch['_id']

        resource_to_patch['endpoint'] = '/api/v1/test'

        response = self.client.save_changes(resource_id, resource_to_patch)

        self.assertBadRequest(response)
        self.assertIn('endpoint',  response.json)

    def test_return_error_if_patching_id(self):
        response = self.client.create_resource(self.payload)
        new_resource = response.json
        resource_id = new_resource['_id']

        patch_payload = {
            '_id': {'$oid': '571b7cfdeceefb4a395ef433'}
        }

        response = self.client.save_changes(resource_id, patch_payload)

        self.assertBadRequest(response)


class ResourcePUT(BaseTest):
    def test_save_changes(self):
        response = self.client.create_resource(self.payload)
        new_resource_id = response.json['_id']

        self.payload['methods'] = ['POST']
        response = self.client.save(new_resource_id, self.payload)
        self.assertEqual(response.json['methods'], ['POST'])

    def test_ignore_id_on_put(self):
        response = self.client.create_resource(self.payload)
        self.payload['methods'] = ['POST']
        self.payload['_id'] = response.json['_id']

        response = self.client.save(response.json['_id'], self.payload)

        self.assertOK(response)

    def test_return_error_if_duplicate_endpoint_and_methods(self):
        another_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "POST"
            ]
        }

        response = self.client.create_resource(self.payload)
        self.assertOK(response)

        response = self.client.create_resource(another_payload)
        new_resource_id = response.json['_id']
        self.assertOK(response)

        another_payload['methods'] = ['GET']
        response = self.client.save(new_resource_id, another_payload)
        self.assertBadRequest(response)

    def test_return_error_if_all_fields_missing(self):
        response = self.client.create_resource(self.payload)

        empty_payload = {}
        response = self.client.save(response.json['_id'], empty_payload)
        self.assertBadRequest(response)

    def test_return_error_if_response_missing(self):
        response = self.client.create_resource(self.payload)
        del self.payload['response']

        response = self.client.save(response.json['_id'], self.payload)
        self.assertBadRequest(response)

    def test_return_error_if_methods_missing(self):
        response = self.client.create_resource(self.payload)
        del self.payload['methods']

        response = self.client.save(response.json['_id'], self.payload)
        self.assertBadRequest(response)

    def test_return_error_if_endpoint_missing(self):
        response = self.client.create_resource(self.payload)
        del self.payload['endpoint']

        response = self.client.save(response.json['_id'], self.payload)
        self.assertBadRequest(response)

if __name__ == '__main__':
    unittest.main()
