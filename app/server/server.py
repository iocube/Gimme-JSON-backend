import os
from flask import Blueprint, request, Response
from app import utility
from app.http_status_codes import HTTP_OK
from settings import settings


blueprint = Blueprint('server', __name__)

@blueprint.route('/server', methods=['DELETE'])
@utility.crossdomain()
def server_reload():
    """
    Flask does not have method to reload server manually except for when
    source code of one of the modules is changed.

    To reload the server we'll update mtime for one of modules and that will trigger reload.

    This will work only if flask development server running with use_reloader=True.
    """
    os.utime(settings.TOUCH_ME_TO_RELOAD, None)
    return Response(status=HTTP_OK, mimetype='application/json')
