import pymongo
from settings import settings


connection = intpymongo.MongoClient(settings.DATABASE_HOST, int(settings.DATABASE_PORT))
database = connection[settings.MONGODB_NAME]
