import pymongo

from app.database import database
from app.dao import BaseDAO


class EndpointDAO(BaseDAO):
    def __init__(self):
        self.collection = database.endpoints

    def _index(self):
        self.collection.create_index(
            [('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)],
            unique=True
        )
