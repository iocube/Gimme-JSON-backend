import pymongo
from settings import settings


connection = pymongo.MongoClient(settings.DATABASE_HOST, settings.DATABASE_PORT)
database = connection[settings.MONGODB_NAME]
