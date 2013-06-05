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
    auth.setup_auth()
    from rhaptos2.repo import views  # noqa

    return app


def dolog(lvl, msg, caller=None, statsd=None):
    """wrapper function purely for adding context to log stmts

    I am trying to keep this simple, no parsing of the stack etc.

    caller is the function passed when the dolog func is called.  We
    jsut grab its name extras is likely to hold a list of strings that
    are the buckets


    >>> dolog("ERROR", "whoops", os.path.isdir, ['a.b.c',])

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

    # create an extras dict, that holds curreent user, request and action notes
    if caller:
        calledby = "rhaptos2.loggedin." + str(caller.__name__)
    else:
        calledby = "rhaptos2.loggedin.unknown"

    if statsd:
        statsd.append(calledby)
    else:
        statsd = [calledby, ]

    try:
        request_id = g.request_id
    except:
        request_id = "no_request_id"

    try:
        user_id = g.userID
    except:
        user_id = "no_user_id"

    extra = {'statsd': statsd,
             'user_id': user_id,
             'request_id': request_id}

    try:
        _app.logger.log(goodlvl, msg, extra=extra)
    except Exception, e:
        print extra, msg, e


def set_up_logging(app):
    """Set up the logging within the application.

    """
    config = app.config

    # Define the logging handlers
    stream_handler = logging.StreamHandler()

    # Define the log formatting.
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s  "
                                  "- %(message)s")

    stream_handler.setFormatter(formatter)
    # Set the handlers on the application.
    for handler in (stream_handler,):
        app.logger.addHandler(handler)
