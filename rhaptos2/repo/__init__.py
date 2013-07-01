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
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)
import os

from flask import Flask, g
import pkg_resources
import socket


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

    FIXME - tidy this up!
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
    app.add_url_rule(
        "/tempsession", view_func=views.temp_session, methods=['GET', ])

    app.add_url_rule("/valid", view_func=auth.valid, methods=['GET'])
    app.add_url_rule("/logout", view_func=auth.logout, methods=['GET', ])
    app.add_url_rule("/home", view_func=views.home, methods=['GET', ])

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

    The ``as_standalone`` parameter (toggled by `--devserver` in commandline) is
    used to tell the factory to serve the static Authoring Tools Client (ATC)
    client JavaScript code from a directory. In a deployed situation this would
    normally be configured and served by the webserver.

    """
    app = Flask(__name__)
    app.config.update(config)
    app = assign_routing_rules(app)

    # Try to set up logging. If not connected to a network this throws
    # "socket.gaierror: [Errno 8] nodename nor servname provided, or not known"
    # Silences too much, tried to be specific.
    try:
        set_up_logging(app)
    except socket.gaierror, se:
        pass
    except Exception, e:
        raise e

    # Set the application
    app = set_app(app)

    return app


def set_up_logging(app):
    """Set up the logging within the application.

    We have three logging outputs - console, filesystem and syslog
    syslog is only expected to exist for production purposes.
    console by default logs only errors and is a convenience for developoers
    filesystem is for digging deeper.

    They are controlled via the following in .ini files::

        loglevel = DEBUG
        use_logging = Y
        log_to_console = Y

        log_to_filesystem = Y
        local_log_dir = /opt/cnx/log/

        log_to_syslog = Y
        syslogfile = /dev/log


    """
    config = app.config

    default_formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s:%(message)s")

    ### root logger - used everywhere *except*
    ### log messages sent during configuration collection.
    root = logging.getLogger(__name__)
    root.setLevel(config['globals']['loglevel'])

    ### console output - turn off in config, simplified output.
    if config['globals']['log_to_console'] == 'Y':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter("%(levelname)s : %(message)s")
        root.addHandler(console_handler)

    ## write to syslog - defaults to INFO
    if config['globals']['log_to_syslog'] == 'Y':
        syslog_handler = logging.handlers.SysLogHandler(
            address=config['globals']['syslogfile'])
        syslog_handler.setLevel(logging.INFO)
        syslog_handler.setFormatter(default_formatter)
        root.addHandler(syslog_handler)

    ### local file loggers for development
    ### eventlog records everything, errorlog just for errors
    if config['globals']['log_to_filesystem'] == 'Y':

        eventlogpath = os.path.join(config['globals']['local_log_dir'],
                                    "repo-error.log")

        errlogpath = os.path.join(config['globals']['local_log_dir'],
                                  "repo-error.log")

        error_handler = logging.FileHandler(errlogpath, "a")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(default_formatter)

        event_handler = logging.FileHandler(eventlogpath, "a")
        event_handler.setLevel(logging.INFO)
        event_handler.setFormatter(default_formatter)

        root.addHandler(error_handler)
        root.addHandler(event_handler)

    root.info("logger set up on %s as %s" % (__name__, str(root)))
