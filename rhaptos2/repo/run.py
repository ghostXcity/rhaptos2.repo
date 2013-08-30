#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""run.py - Launch the repo app.

This is the suggested method for running a WSGI Server - we instantiate the repo
app, and pass it to the waitress server (To be replaced by gunicorn)::


  python run.py --config=../../testing.ini --devserver --jslocation=/path/to/atc


changes:

* 21 May 2013 - moving to avoid global app.  We have been calling get_app which
  looks at the global in __init__ I would rather use a push approach to giving
  individual modules config and the wsgiapp this will mean we can more easily
  run modules as standalone, more easily seperate out testing and fits my brain
  easier (this last is unlikely to apply to anyone else I admit!)

  currently views.py, __init__.py, run.py, auth.py have to have an wsgiapp in
  their global namespace

  By removing the @route approach, and placing that, before and after requests,
  and the oid setup, in the initialisation phase of run, only run will need a
  wsgiapp in the global namespace, although auth.py will find it easier / avoid
  refactor of the openid approaches.

"""
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)

from rhaptos2.repo import (make_app, sessioncache,
                           weblogging, backend)
from rhaptos2.repo.configuration import Configuration
from optparse import OptionParser
import os
from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser, make_static
from waitress import serve

########################################################


def main():
    opts, args = parse_args()
    config = Configuration.from_file(opts.conf)
    app = get_app(opts, args, config,
                  as_devserver=opts.devserver,
                  jslocation=opts.jslocation)
    wsgi_run(app, opts, args)


def get_app(opts, args, config, as_devserver=False, jslocation=None):
    """

    creates and sets up the app, *but does not run it through flask server unless told to*
    This intends to return a valid WSGI app to later be called by say gunicorn

    returns a Flask app.wsgi_app, which can be passed into wsgi chain

    """

    app = make_app(config)
    app.debug = True
    weblogging.configure_weblogging(config)
    sessioncache.set_config(config)
    ## We initialise the connection pool
    backend.setpool(config)


    
    if as_devserver:

        if not os.path.isdir(jslocation):
            raise IOError(
                "dir to serve static files (%s) does not exist" % jslocation)

        ### Creating a mapping of URLS to file locations
        ### TODO: simplify this - proabbly need change atc and this
        ### may want to consider a config list of dirs, or grab
        ### list of dirs from FS (at jslocation) at startup time
        sloc = jslocation
        stat = StaticURLParser(sloc)
        stat_config = StaticURLParser(os.path.join(sloc, "config"))
        stat_lib = StaticURLParser(os.path.join(sloc, "lib"))
        stat_bookish = StaticURLParser(os.path.join(sloc, "bookish"))
        stat_helpers = StaticURLParser(os.path.join(sloc, "helpers"))
        stat_node_modules = StaticURLParser(os.path.join(sloc, "node_modules"))

        ### give repo a simple response - /api/ will get rewritten
        ### todo: can I force URLMap not to adjust PATH info etc?
        mymaps = {"/": app.wsgi_app,
                  "/js/": stat,
                  "/js/config/": stat_config,
                  "/js/lib/": stat_lib,
                  "/js/bookish/": stat_bookish,
                  "/js/helpers/": stat_helpers,
                  "/js/node_modules/": stat_node_modules}

        urlmap = URLMap()
        urlmap.update(mymaps)
        wrappedapp = urlmap

    else:  # /not devserver, production run.
        wrappedapp = app.wsgi_app

    return wrappedapp


def wsgi_run(app, opts, args):
    """ """

    serve(app,
          host=opts.host,
          port=opts.port
          )


def parse_args():

    """

    dev server
       We have decided to put several wsgi functions into the options for the repo
       This will enable one python server to run several portions of the whole "ecosystem"
       such as the /upload/ server.

    """
    parser = OptionParser()
    parser.add_option("--host", dest="host",
                      default="0.0.0.0",
                      help="hostname to listen on")

    parser.add_option("--port", dest="port",
                      default="8000",
                      help="port to listen on", type="int")

    parser.add_option("--debug", dest="debug", action="store_true",
                      help="debug on.", default=False)

    parser.add_option("--config", dest="conf",
                      help="Path to config file.")

    parser.add_option("--devserver", dest="devserver",
                      action="store_true", default=False,
                      help="Enable development only switches, incl serving static files")

    parser.add_option("--jslocation", dest="jslocation",
                      help="Path to atc static files, served for testing purposes")

    parser.add_option("--upload", dest="upload",
                      action="store_true", default=False,
                      help="Toggle to enable /upload/ - will accept and return binary files. Not yet implemented")

    (options, args) = parser.parse_args()
    return (options, args)

def show_conf():
    """
    """
    opts, args = parse_args()
    config = Configuration.from_file(opts.conf)
    return config
   
def initialize_database():
    """Initialize the database tables."""
    opts, args = parse_args()
    config = Configuration.from_file(opts.conf)

    from rhaptos2.repo.backend import initdb
    initdb(config)
    

    
if __name__ == '__main__':
    main()
