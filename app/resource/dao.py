from settings import settings
from app.database import database
from app.dao import BaseDAO


class ResourceDAO(BaseDAO):
    def __init__(self):
        self.collection = database[settings.MONGODB_COLLECTION_RESOURCE]
