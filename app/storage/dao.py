from app.database import database
from app.dao import BaseDAO


class StorageDAO(BaseDAO):
    def __init__(self):
        self.collection = database.storage