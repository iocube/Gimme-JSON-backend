import pymongo
from settings import settings


connection = pymongo.MongoClient('db', 27017)
database = connection[settings.MONGODB_NAME]
