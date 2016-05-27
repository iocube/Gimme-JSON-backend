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
    database[settings.MONGODB_COLLECTION_ENDPOINT].create_index(
        [('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)],
        unique=True
    )


@database_manager.command
def drop():
    connection.drop_database(settings.MONGODB_NAME)


@database_manager.command
def populate():
    f = open('fixtures/endpoints.json', 'r')
    endpoints = json.loads(f.read())
    f.close()
    database[settings.MONGODB_COLLECTION_ENDPOINT].insert_many(endpoints)


@manager.option('-m', '--module', dest='module_name')
@manager.option('-c', '--class', dest='class_name')
@manager.option('-t', '--testname', dest='test_name')
def test(module_name=None, class_name=None, test_name=None):
    """
    Run tests.
    NOTE: modules have to be prefixed with 'test_'.
    """
    if module_name and (not class_name and not test_name):
        # equivalent to running $ python -m <package>.<module>
        subprocess.call(
            ['python', '-m', 'tests.{m}'.format(m=module_name)]
        )
    elif module_name and class_name and not test_name:
        # equivalent to running $ python -m <package>.<module> <class>
        subprocess.call(
            ['python', '-m', 'tests.{m}'.format(m=module_name), '{c}'.format(c=class_name)]
        )
    elif module_name and class_name and test_name:
        # equivalent to running $ python -m <package>.<module> <class>.<test>
        subprocess.call(
            ['python', '-m', 'tests.{m}'.format(m=module_name), '{c}.{t}'.format(c=class_name, t=test_name)]
        )
    else:
        # run all tests
        subprocess.call(['python', '-m', 'unittest', 'discover', '-s', 'tests'])


APPLICATION_PACKAGE = 'app'
@manager.command
def coverage():
    """
    Generate coverage.
    """
    # package name to generate the cover for

    coverage_run = 'coverage run --source {package} -m unittest discover -s tests'
    subprocess.call(coverage_run.format(package=APPLICATION_PACKAGE).split())
    subprocess.call(['coverage', 'html'])


@manager.command
def generatesecret():
    import string
    from app import util

    all_characters = string.ascii_lowercase + \
                     string.ascii_uppercase + \
                     string.digits + \
                     string.punctuation

    return util.generate_string(all_characters, length=32)


@manager.command
def showroutes():
    from urllib.parse import unquote
    from flask import url_for

    output = []
    for rule in application.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, _external=True, **options)
        line = unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)

manager.add_command("runserver", Server(use_debugger=True, use_reloader=True))
manager.add_command("database", database_manager)

if __name__ == '__main__':
    manager.run()
