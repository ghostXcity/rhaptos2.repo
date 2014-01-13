# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Commandline utilities

Contains commandline utilities for initializing the database
(``initialize_database``) and an application for use with PasteDeploy.
"""
import os
import argparse

from rhaptos2.repo import make_app
from rhaptos2.repo.configuration import Configuration


__all__ = ('initialize_database', 'paste_app_factory',)


def paste_app_factory(global_config, **local_config):
    """Makes a WSGI application (in Flask this is ``app.wsgi_app``)
    and wraps it to serve the static web files.
    """
    try:
        config_filepath = local_config['config']
    except KeyError:
        raise RuntimeError("You must supply a reference as 'config' in "
                           "the paste ini configuration file "
                           "to the configuration ini file "
                           "used by this application.")
    config = Configuration.from_file(config_filepath)
    app = make_app(config)
    # TODO This should be assigned in the app factory.
    app.debug = True
    return app


def initialize_database(argv=None):
    """Initialize the database tables."""
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help="configuration file")
    args = parser.parse_args(argv)
    config = Configuration.from_file(args.config)

    make_app(config)
    from rhaptos2.repo.backend import initdb
    initdb(config)

    from rhaptos2.repo.sessioncache import set_config, initdb as sessinitdb
    set_config(config)
    sessinitdb()
