# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""\
This is an unpublished (or editable) repository implementation for working
with educational content. This web application allows for the storage,
retrieval and modification of works in progress.

The WSGI application factory is importable as ``make_app``.

To acquire the application from anywhere in this package or extra packages,
use the ``get_app`` function.
"""
import os
import sys
import socket
import logging
import ConfigParser
from logging.config import fileConfig

import pkg_resources
from flask import Flask, g


__all__ = ('get_app', 'set_app', 'make_app',)
__version__ = pkg_resources.require("rhaptos2.repo")[0].version

logger = logging.getLogger(__name__)
here = os.path.abspath(os.path.dirname(__file__))
CONFIG_KEY__LOGGING_CONFIG = 'logging-config'
DEFAULT_LOGGING_CONFIG_FILEPATH = os.path.join(here, 'default-logging.ini')

# XXX Remove when all references have been eliminated.
APPTYPE = 'rhaptos2repo'
VERSION = __version__


_app = None

def get_app():
    """Get the application object"""
    global _app
    return _app

def set_app(app):
    """Set the global application object"""
    global _app
    _app = app
    return _app


def assign_routing_rules(app):
    """

    In short, have wsgi app created in a factory, *after* import time.
    Avoid having to have a wsgi / flask app in global namespace of views.
    We need to replace decorators that assume app already exists at import (or decorator first call time)

    FIXME - tidy this up!
    """
    from rhaptos2.repo import views
    from rhaptos2.repo import auth

    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/bootstrap/", view_func=views.bootstrap)
    app.add_url_rule("/me/", view_func=views.whoamiGET, methods=['GET'])
    app.add_url_rule(
        "/workspace/", view_func=views.workspaceGET, methods=['GET'])
    app.add_url_rule("/keywords/", view_func=views.keywords, methods=['GET', ])
    app.add_url_rule(
        "/version/", view_func=views.versionGET, methods=['GET', ])
    app.add_url_rule(
        "/autosession", view_func=views.auto_session, methods=['GET', ])
    app.add_url_rule(
        "/tempsession", view_func=views.temp_session, methods=['GET', ])

    app.add_url_rule("/valid", view_func=auth.valid, methods=['GET'])
    app.add_url_rule("/login", view_func=auth.login, methods=['GET'])
    app.add_url_rule("/logout", view_func=auth.logout, methods=['GET', ])

    app.add_url_rule("/folder/", view_func=views.folder_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'], defaults={'folderuri': ''})
    app.add_url_rule('/folder/<path:folderuri>', view_func=views.folder_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'])

    app.add_url_rule("/content/", view_func=views.content_router,
                     methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'uid': ''})
    app.add_url_rule("/content/<path:uid>", view_func=views.content_router,
                     methods=['GET', 'POST', 'PUT', 'DELETE'])

    app.before_request(views.requestid)
    app.after_request(views.call_after_request_callbacks)
    return app


def make_app(config):
    """Application factory"""
    # Initialize logging before doing anything.
    try:
        fileConfig(config[CONFIG_KEY__LOGGING_CONFIG])
    except KeyError:
        # Configuration was not specified, using default.
        fileConfig(DEFAULT_LOGGING_CONFIG_FILEPATH)
    except ConfigParser.NoSectionError as exception:
        import traceback
        traceback.print_exc()
        raise RuntimeError("Logging configuration was specified in the '{}', "
                           "but the configuration file is either not found "
                           "or is missing sections. See also, "
                           "previous traceback above this one." \
                           .format(CONFIG_KEY__LOGGING_CONFIG))

    app = Flask(__name__)
    app.config.update(config)
    # Set the application
    app = set_app(app)
    app = assign_routing_rules(app)

    # XXX Shouldn't the sessioncache module reference the application
    #     configuration rather than trying to work with it's own?
    from . import sessioncache
    sessioncache.set_config(config)

    return app
