import json
import unittest
import pymongo
from gimmejson import application
from app import database
from app.http_status_codes import HTTP_OK, HTTP_BAD_REQUEST
from settings import settings

class Client(object):
    def __init__(self):
        self.client = application.test_client()

    def get(self, *args, **kwargs):
        return self._http_call(self.client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._http_call(self.client.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._http_call(self.client.put, *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._http_call(self.client.patch, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._http_call(self.client.delete, *args, **kwargs)

    def _http_call(self, method_func, *args, **kwargs):
        if kwargs.has_key('data'):
            kwargs['data'] = json.dumps(kwargs['data'])
            kwargs['content_type'] = 'application/json'
            response = method_func(*args, **kwargs)
        else:
            response = method_func(*args, **kwargs)
        response.json = json.loads(response.get_data())
        return response

class BaseTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)
        database.database[settings.MONGODB_COLLECTION_RESOURCE].create_index([('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)], unique=True)
        self.client = Client()

    def tearDown(self):
        pass

class ResourceGET(BaseTest):
    def test_get_resources_list(self):
        response = self.client.get('/resource')
        all_resources = response.json

        self.assertEqual(response.status_code, HTTP_OK)

class ResourcePOST(BaseTest):
    def test_create_new_resource(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource = response.json
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertTrue(new_resource.has_key('_id'))

    def test_return_error_if_endpoint_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource = response.json
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(new_resource.has_key('endpoint'))

    def test_return_error_if_response_missing(self):
        payload = {
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        error = response.json

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(error.has_key('response'))

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

        response = self.client.post('/resource', data=payload)
        self.assertEqual(response.status_code, HTTP_OK)

        response = self.client.post('/resource', data=payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        error = response.json
        self.assertTrue(error.has_key('endpoint'))

    def test_return_error_if_methods_are_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test"
        }

        response = self.client.post('/resource', data=payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        error = response.json
        self.assertTrue(error.has_key('methods'))

    def test_return_error_if_all_fields_missing(self):
        payload = {}

        response = self.client.post('/resource', data=payload)
        error = response.json

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        response = self.client.post('/resource', data=None)

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

class ResourceDELETE(BaseTest):
    def test_delete_resource(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource = response.json
        new_resource_id = new_resource['_id']['$oid']
        response = self.client.delete('/resource/' + new_resource_id)
        self.assertEqual(response.status_code, HTTP_OK)

    def test_delete_unexistent_resource(self):
        response = self.client.delete('/resource/' + '571b7cfdeceefb4a395ef433')
        self.assertTrue(response.status_code, HTTP_BAD_REQUEST)

class ResourcePATCH(BaseTest):
    def test_edit_all_fields(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource = response.json
        resource_id = new_resource['_id']['$oid']

        new_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Tel-Aviv\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "POST"
            ]
        }

        response = self.client.patch('/resource/' + resource_id, data=new_payload)
        patched_resource = response.json
        new_payload['_id'] = patched_resource['_id']

        self.assertEqual(response.status_code, HTTP_OK)
        self.assertEqual(patched_resource, new_payload)

    def test_return_error_if_duplicate_endpoints_and_methods(self):
        """
        should return error if such endpoint and methods already exist
        when trying to modify existing endpoint
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        payload_second = {
            "response": "{\"name\": \"Bob\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "GET"
            ]
        }

        self.client.post('/resource', data=payload)
        response = self.client.post('/resource', data=payload_second)

        resource_to_patch = response.json
        resource_id = resource_to_patch['_id']['$oid']

        resource_to_patch['endpoint'] = '/api/v1/test'

        response = self.client.patch('/resource/' + resource_id, data=resource_to_patch)
        error = response.json

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(error.has_key('endpoint'))

    def test_return_error_if_patching_id(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource = response.json
        resource_id = new_resource['_id']['$oid']

        patch_payload = {
            '_id': {'$oid': '571b7cfdeceefb4a395ef433'}
        }

        response = self.client.patch('/resource/' + resource_id, data=patch_payload)

        self.assertTrue(response.status_code, HTTP_BAD_REQUEST)

class ResourcePUT(BaseTest):
    def test_save_changes(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']

        payload['methods'] = ['POST']
        response = self.client.put('/resource/' + new_resource_id, data=payload)
        updated_resource = response.json
        self.assertEqual(updated_resource['methods'], ['POST'])

    def test_ignore_id_on_put(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json
        payload['methods'] = ['POST']
        payload['_id'] = new_resource_id

        response = self.client.put('/resource/' + new_resource_id['_id']['$oid'], data=payload)

        self.assertEqual(response.status_code, HTTP_OK)

    def test_return_error_if_duplicate_endpoint_and_methods(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        another_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "POST"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']
        self.assertEqual(response.status_code, HTTP_OK)

        response = self.client.post('/resource', data=another_payload)
        new_resource_id = response.json['_id']['$oid']
        self.assertEqual(response.status_code, HTTP_OK)

        another_payload['methods'] = ['GET']
        response = self.client.put('/resource/' + new_resource_id, data=another_payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_all_fields_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']

        empty_payload = {}
        response = self.client.put('/resource/' + new_resource_id, data=empty_payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_response_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']

        del payload['response']
        response = self.client.put('/resource/' + new_resource_id, data=payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_methods_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']

        del payload['methods']
        response = self.client.put('/resource/' + new_resource_id, data=payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_endpoint_missing(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=payload)
        new_resource_id = response.json['_id']['$oid']

        del payload['endpoint']
        response = self.client.put('/resource/' + new_resource_id, data=payload)
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

if __name__ == '__main__':
    unittest.main()
