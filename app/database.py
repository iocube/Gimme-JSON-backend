import pymongo
from settings import settings


connection = pymongo.MongoClient(settings.DATABASE_HOST)
database = connection[settings.MONGODB_NAME]
