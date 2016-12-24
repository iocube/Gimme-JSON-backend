from pymongo import ReturnDocument
from bson.objectid import ObjectId


class BaseDAO(object):
    def __init__(self):
        self.collection = None

    def get_by_id(self, document_id):
        id_to_find = document_id

        if ObjectId.is_valid(document_id):
            id_to_find = ObjectId(id_to_find)

        return self.collection.find_one({'_id': id_to_find})

    def get_all(self):
        return self.collection.find()

    def create(self, **kwargs):
        document = kwargs
        allocated_id = self.collection.insert_one(document).inserted_id
        document['_id'] = allocated_id
        return document

    def delete(self, document_id):
        if ObjectId.is_valid(document_id):
            return self.collection.find_one_and_delete({'_id': ObjectId(document_id)})

        return self.collection.find_one_and_delete({'_id': document_id})

    def save(self, document_id, updated_document):
        return self.collection.find_one_and_replace(
            {'_id': ObjectId(document_id)},
            updated_document,
            return_document=ReturnDocument.AFTER
        )

    def update(self, document_id, partial_document):
        return self.collection.find_one_and_update(
            {'_id': ObjectId(document_id)},
            {'$set': partial_document},
            return_document=ReturnDocument.AFTER
        )
