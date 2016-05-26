import os
from app import decorators
from settings import settings


@decorators.crossdomain()
@decorators.to_json
@decorators.jwt_auth_required
def restart():
    """
    Flask does not have method to reload server manually except for when
    source code of one of the modules is changed.

    To reload the server we'll update mtime for one of modules and that will trigger reload.

    This will work only if flask development server running with use_reloader=True.
    """
    os.utime(settings.TOUCH_ME_TO_RELOAD, None)
    return {}
