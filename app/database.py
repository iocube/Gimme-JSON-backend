import pymongo
import settings


connection = pymongo.MongoClient()
database = connection[settings.MONGODB_NAME]
