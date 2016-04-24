from settings import settings
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult
from bson import json_util
from app.database import database
from bson.objectid import ObjectId

class ModelResult(object):
    def __init__(self, result):
        self.result = result

    def to_json(self):
        if isinstance(self.result, InsertOneResult):
            return json_util.dumps(self.result.inserted_id)
        return json_util.dumps(self.result)

    def original(self):
        return self.result

class ResourceModel(object):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_RESOURCE]

    def get_all_resources(self):
        return ModelResult(self.collection.find())

    def create(self, endpoint, methods, response, query_params):
        # TODO: endpoint can not be defined with same methods twice
        return ModelResult(self.collection.insert_one({'endpoint': endpoint, 'methods': methods, 'response': response, 'queryParams': query_params}))

    def delete(self, resource_id):
        return self.collection.find_one_and_delete({'_id': ObjectId(resource_id)})

    def patch(self, resource_id, properties):
        properties = {'$set': properties}
        return ModelResult(self.collection.find_one_and_update({'_id': ObjectId(resource_id)}, properties, return_document=ReturnDocument.AFTER))
