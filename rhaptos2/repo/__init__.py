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
import socket
import logging

import pkg_resources
from flask import Flask, g


__version__ = pkg_resources.require("rhaptos2.repo")[0].version
lgr = logging.getLogger(__name__)

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

    
    ###
    app.add_url_rule('/logging', view_func=views.logging_endpoint,
                     methods=['POST'])
    ###

    app.before_request(views.requestid)
    app.after_request(views.call_after_request_callbacks)
    return app


def make_app(config):
    """Application factory"""
    app = Flask(__name__)
    app.config.update(config)
    # Set the application
    app = set_app(app)
    app = assign_routing_rules(app)

    # Try to set up logging. If not connected to a network this throws
    # "socket.gaierror: [Errno 8] nodename nor servname provided, or not known"
    # Silences too much, tried to be specific.
    try:
        set_up_logging(app.config)
    except socket.gaierror, se:
        pass
    except Exception, e:
        raise e

    return app


def set_up_logging(config):
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
                          address=config['globals']['syslogfile'],
                          facility=int(config['globals']['syslogfacility']),
                          )
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
