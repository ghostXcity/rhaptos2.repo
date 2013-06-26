#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""Rhaptos Repo profile web application

The application is initialized using the application factory (`make_app`).

To acquire the application from anywhere in this package or extra packages,
use the `get_app` function.

"""
import logging
from flask import Flask, g
from rhaptos2.repo import log
import pkg_resources
import logging
from logging import FileHandler, StreamHandler


__version__ = pkg_resources.require("rhaptos2.repo")[0].version

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

    """
    from rhaptos2.repo import views
    from rhaptos2.repo import auth

    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/me/", view_func=views.whoamiGET, methods=['GET'])
    app.add_url_rule(
        "/workspace/", view_func=views.workspaceGET, methods=['GET'])
    app.add_url_rule("/keywords/", view_func=views.keywords, methods=['GET', ])
    app.add_url_rule(
        "/version/", view_func=views.versionGET, methods=['GET', ])
    app.add_url_rule(
        "/autosession", view_func=views.auto_session, methods=['GET', ])
    app.add_url_rule("/valid", view_func=auth.valid, methods=['GET'])
    app.add_url_rule("/logout", view_func=auth.logout, methods=['GET', ])

    app.add_url_rule("/folder/", view_func=views.folder_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'], defaults={'folderuri': ''})
    app.add_url_rule('/folder/<path:folderuri>', view_func=views.folder_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'])

    app.add_url_rule("/collection/", view_func=views.collection_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'], defaults={'collectionuri': ''})
    app.add_url_rule('/collection/<path:collectionuri>', view_func=views.collection_router, methods=[
                     'GET', 'POST', 'PUT', 'DELETE'])

    app.add_url_rule("/module/", view_func=views.module_router,
                     methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'moduleuri': ''})
    app.add_url_rule('/module/<path:moduleuri>', view_func=views.module_router,
                     methods=['GET', 'POST', 'PUT', 'DELETE'])

    app.before_request(views.requestid)
    app.after_request(views.call_after_request_callbacks)
    return app


def make_app(config, as_standalone=False):
    """WSGI application factory
    The ``as_standalone`` parameter is used to tell the factory to serve the
    static Authoring Tools Client (ATC) client JavaScript code from a
    directory. In a deployed situation this would normally be configured
    and served by the webserver.

    """
    app = Flask(__name__)
    app.config.update(config)
    app = assign_routing_rules(app)

    # Try to set up logging. If not connected to a network this throws
    # "socket.gaierror: [Errno 8] nodename nor servname provided, or not known"
    try:
        set_up_logging(app)
    except:
        pass

    # Set the application
    app = set_app(app)

    # Initialize the views
    # This import circular avoidinace trick is horrible
    # I will review log and import process and want to put it all in a single
    # setup in run.
    from rhaptos2.repo import auth  # noqa
    from rhaptos2.repo import views  # noqa

    return app


def dolog(lvl, msg, caller=None, statsd=None):
    """
    reducing logging to minimum
    """
    lvls = {
       "CRITICAL": 50,
       "ERROR": 40,
       "WARNING": 30,
       "INFO": 20,
       "DEBUG": 10,
       "NOTSET": 0
    }
    try:
        goodlvl = lvls[lvl]
    except:
        goodlvl = 20  # !!!
    _lgr.log(goodlvl, msg)
    


def set_up_logging(app):
    """Set up the logging within the application.

    """
    config = app.config

    default_formatter = logging.Formatter(\
       "%(asctime)s:%(levelname)s:%(name)s:%(message)s")

    console_handler = StreamHandler()
    console_handler.setFormatter(default_formatter)

    error_handler = FileHandler("repo-error.log", "a")
    error_handler.setLevel(logging.INFO)
    error_handler.setFormatter(default_formatter)

    flask_error_handler = FileHandler("flask-error.log", "a")
    flask_error_handler.setLevel(logging.INFO)
    flask_error_handler.setFormatter(default_formatter)

    
    root = logging.getLogger(__name__)
    root.addHandler(console_handler)
    root.addHandler(error_handler)
    root.setLevel(logging.INFO)

    root.info("logger set up on %s" % __name__)
    
    app.logger.addHandler(flask_error_handler)
    app.logger.info("Flask-logger will output to %s" % "flask-error.log")
