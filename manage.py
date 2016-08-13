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
def index():
    from app.endpoint.dao import EndpointDAO
    from app.user.dao import UserDAO

    endpoint = EndpointDAO()
    endpoint._index()

    user = UserDAO()
    user._index()

@database_manager.command
def drop():
    connection.drop_database(settings.MONGODB_NAME)


@database_manager.command
def populate():
    f = open('fixtures/endpoints.json', 'r')
    endpoints = json.loads(f.read())
    f.close()
    database.endpoints.insert_many(endpoints)


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

@manager.command
def newresource(pkg_name):
    import os
    import shutil
    from jinja2 import Template

    pkg_dst_folder = '{dst}/{pkg}'.format(dst='app/', pkg=pkg_name)
    pkg_template_folder = 'management/package'

    shutil.copytree(pkg_template_folder, pkg_dst_folder)
    os.chdir(pkg_dst_folder)
    module_list = filter(lambda filename: filename.endswith('.module'), os.listdir())

    for each in module_list:
        f = open(each, 'r')
        module_content = f.read()
        f.close()

        f = open(each, 'w')
        template = Template(module_content)
        rendered = template.render(pkg=pkg_name)
        f.write(rendered)
        f.close()

        os.rename(each, each.replace('.module', '.py'))


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    application.wsgi_app = ProfilerMiddleware(
        application.wsgi_app,
        restrictions=[length],
        profile_dir=profile_dir)
    application.run()


manager.add_command("runserver", Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=True))
manager.add_command("database", database_manager)

if __name__ == '__main__':
    manager.run()
