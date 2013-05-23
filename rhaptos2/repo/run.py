#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""
run.py - Launch the repo app.

This is the suggested method for running a WSGI Server - we instantiate the repo
app, and pass it to the waitress server (To be replaced by gunicorn)::

  python run.py --config=../../testing.ini --devserver --jslocation=/path/to/atc


changes:

* 21 May 2013 - moving to avoid global app.
  We have been calling get_app which looks at the global in __init__
  I would rather use a push approach to giving individual modules config and the wsgiapp
  this will mean we can more easily run modules as standalone, more easily seperate out testing
  and fits my brain easier (this last is unlikely to apply to anyone else I admit!)

  currently views.py, __init__.py, run.py, auth.py have to have an wsgiapp in their global namespace

  By removing the @route approach, and placing that, before and after requests, and the oid setup,
  in the initialisation phase of run, only run will need a wsgiapp in the global namespace, although auth.py will
  find it easier / avoid refactor of the openid approaches.


app.add_url_rule("/", view_func=index)
app.add_url_rule("/me/", view_func=whoamiGET, methods=['GET'])
app.add_url_rule("/workspace/", view_func=workspaceGET, methods=['GET'])
app.add_url_rule("/keywords/", view_func=keywords, methods=['GET',])
app.add_url_rule("/version/", view_func=versionGET, methods=['GET',])
app.add_url_rule("/admin/config", view_func=admin_config, methods=['GET',])
app.add_url_rule("/autosession", view_func=auto_session, methods=['GET',])
app.add_url_rule("/images/openid-providers-en.png", view_func=temp_openid_image_url, methods=['GET',])
app.add_url_rule("/login", view_func=login, methods=['GET', 'POST'])
### This needs oid.loginhandler function applied ...@auth.oid.loginhandler
app.add_url_rule("/logout", view_func=logout, methods=['GET',])
app.add_url_rule('/persona/logout/', view_func=logoutpersona, methods=['POST',])
app.add_url_rule("/persona/login/", view_func=loginpersona, methods=['POST',])

app.add_url_rule("/folder/", view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'folderuri': ''})
app.add_url_rule('/folder/<path:folderuri>', view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'])

app.add_url_rule("/collection/", view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'collectionuri': ''})
app.add_url_rule('/collection/<path:collectionuri>', view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'])

app.add_url_rule("/module/", view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'moduleuri': ''})
app.add_url_rule('/module/<path:moduleuri>', view_func=folder_router, methods=['GET', 'POST', 'PUT', 'DELETE'])




"""

from rhaptos2.repo import make_app, sessioncache
from rhaptos2.repo.configuration import Configuration
from optparse import OptionParser
import os
from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser, make_static
from waitress import serve


def main():
    opts, args = parse_args()
    config = Configuration.from_file(opts.conf)
    app = get_app(opts, args, config, 
                  as_standalone = opts.devserver, 
                  with_testuser = opts.testuser)

    wsgi_run(app, opts, args)


def get_app(opts, args, config, as_standalone = False, with_testuser = False):
    """
    creates and sets up the app, *but does not run it through flask server unless told to*
    This intends to return a valid WSGI app to later be called by say gunicorn

    todo: I would like to use @pumazi approach of only importing _standalone server as needed

    returns a Flask app.wsgi_app, which can be passed into wsgi chain

    """

    app = make_app(config)
    app.debug = True
    sessioncache.set_config(config)
    
    if as_standalone:

        if not os.path.isdir(opts.jslocation):
            raise IOError(
                "dir to serve static files (%s) does not exist" % opts.jslocation)

        ### Creating a mapping of URLS to file locations
        ### TODO: simplify this - proabbly need change atc and this
        ### may want to consider a config list of dirs, or grab
        ### list of dirs from FS (at jslocation) at startup time
        sloc = opts.jslocation
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
	# Need a fake user for testing, especially in the standalone case
        wrappedapp = urlmap
    else:
        wrappedapp = app.wsgi_app

    if with_testuser:
        wrappedapp = AddTestUser(wrappedapp)

    return wrappedapp

class AddTestUser(object):
    """
    We are faking a user header to avoid onerous logins via openid for test situations
    """
   
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        environ['HTTP_X-REMOTEAUTHID'] = 'https://paulbrian.myopenid.com'
        
        # Call the wrapped application onwards
        return self.app(environ, start_response)
        

def wsgi_run(app, opts, args):
    """ """

    serve(app,
          host=opts.host,
          port=opts.port
    )


def parse_args():
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
                      help="run as devserver.")
    parser.add_option("--testuser", dest="testuser",
                      action="store_true", default=False,
                      help="Add a fake openid authenticated testuser")
    parser.add_option("--jslocation", dest="jslocation",
                      help="Path to config file.")

    (options, args) = parser.parse_args()
    return (options, args)


def initialize_database():
    """Initialize the database tables."""
    opts, args = parse_args()
    config = Configuration.from_file(opts.conf)

    from rhaptos2.repo.backend import initdb
    initdb(config)
    

if __name__ == '__main__':
    main()
