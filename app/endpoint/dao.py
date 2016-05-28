import pymongo

from settings import settings
from app.database import database
from app.dao import BaseDAO


class EndpointDAO(BaseDAO):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_ENDPOINT]

    def _index(self):
        self.collection.create_index(
            [('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)],
            unique=True
        )