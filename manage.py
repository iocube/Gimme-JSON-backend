import pymongo
import json
import subprocess

from settings import settings
from gimmejson import application
from flask.ext.script import Manager, Server
from app.database import database, connection


manager = Manager(application)
database_manager = Manager()
tests_manager = Manager()

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

@manager.option('-m', '--module', dest='module_name')
@manager.option('-c', '--class', dest='class_name')
@manager.option('-s', '--singletest', dest='test_name')
def test(module_name=None, class_name=None, test_name=None):
    """
    Run tests.
    NOTE: modules have to be prefixed with 'test_'.
    """
    if module_name and (not class_name and not test_name):
        # equivalent to running $ python -m <package>.<module>
        subprocess.call(['python', '-m', 'tests.{m}'.format(m=module_name)])
    elif module_name and class_name and not test_name:
        # equivalent to running $ python -m <package>.<module> <class>
        subprocess.call(['python', '-m', 'tests.{m}'.format(m=module_name), '{c}'.format(c=class_name)])
    elif module_name and class_name and test_name:
        # equivalent to running $ python -m <package>.<module> <class>.<test>
        subprocess.call(['python', '-m', 'tests.{m}'.format(m=module_name), '{c}.{t}'.format(c=class_name, t=test_name)])
    else:
        # run all tests
        subprocess.call(['python', '-m', 'unittest', 'discover', '-s', 'tests'])

@manager.command
def coverage():
    """
    Generate coverage.
    """
    # package name to generate the cover for
    APPLICATION_PACKAGE = 'app'

    subprocess.call('coverage run --source {package} -m unittest discover -s tests'.format(package=APPLICATION_PACKAGE).split())
    subprocess.call(['coverage', 'html'])

manager.add_command("runserver", Server(use_debugger=True, use_reloader=True))
manager.add_command("database", database_manager)

if __name__ == '__main__':
    manager.run()
