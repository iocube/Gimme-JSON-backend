import pymongo
import json
from settings import settings
from gimmejson import application
from flask.ext.script import Manager, Server
from app.database import database, connection


manager = Manager(application)
database_manager = Manager()

@database_manager.command
def createindexes():
    database[settings.MONGODB_COLLECTION_RESOURCE].create_index([('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)], unique=True)

@database_manager.command
def drop():
    connection.drop_database(settings.MONGODB_NAME)

@database_manager.command
def populate():
    f = open('fixtures/resources.json', 'r')
    resources = json.loads(f.read())
    f.close()
    database[settings.MONGODB_COLLECTION_RESOURCE].insert_many(resources)

manager.add_command("runserver", Server(use_debugger=True, use_reloader=True))
manager.add_command("database", database_manager)

if __name__ == '__main__':
    manager.run()
