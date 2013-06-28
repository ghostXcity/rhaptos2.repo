#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""tests - designed to use WebTest from paste.

ToDo:
at the moment we control every id and session id
Write tests that exercise the system without imposing the ids, so we can run tests
again without hitting PK errors or clearing dbase.



The DisconnectionError:

I was seeing a Client has disconnected error, which I traced to the readinto
function of request.py. This was a red herring it seems, as the cause of the
error was trying to read the body_file object (IOBase) a *second* time - once to
read it when sending the request, and once to read it in restrest.

The setting of the seek for the IO Object seemed too deep in the mire for me, so
I resorted to simply genrating a request object, copying it and *then* executing
the request.  Seems to work fine.

"""

import pprint
import logging
lgr = logging.getLogger(__name__)

import decl, restrest
from rhaptos2.repo import (make_app, backend,
                           sessioncache, dolog,
                           weblogging)
from webtest import TestApp, TestRequest
import cookielib

from wsgiproxy.app import WSGIProxyApp
from optparse import OptionParser
import urlparse
import requests
import json
from rhaptos2.repo.configuration import (  # noqa
    Configuration
)
from nose.tools import with_setup


    ########################################################################
    # module level setup for nosetests
    ########################################################################

TESTCONFIG = None
TESTAPP = None


def convert_config(config):
    """
    This is done to convert the "dict" from configuration into true dict.

    FIXME - this is ridiculous - just go back to one confd object
    """

    defaultsection = 'app'
    if defaultsection in config:
        for k in config[defaultsection]:
            config[k] = config[defaultsection][k]
    return config


def setup():
    global TESTCONFIG
    global TESTAPP

    ## Tests can alter decl. THis resets everything
    reload(decl)
    
    # using nose-testconfig we obtain the config dict passed in through the
    # nosetests command line
    from testconfig import config
    ## now "convert" to app-style dict
    TESTCONFIG = convert_config(config)
    initdb(TESTCONFIG)


    lgr.info("TESTCONFG: %s" % pprint.pformat(TESTCONFIG))
    lgr.info("config: %s" % pprint.pformat(config))
    cj = cookielib.CookieJar()
    
    if 'HTTPPROXY' in config.keys():
        app = WSGIProxyApp(config['HTTPPROXY'])
        TESTAPP = TestApp(app, extra_environ={'REMOTE_ADDR': '1.2.3.4'}, cookiejar=cj)
        set_constants(config['HTTPPROXY'], TESTAPP)                        
    else:
        app = make_app(TESTCONFIG)
        app.debug = True
        sessioncache.set_config(config)
        TESTAPP = TestApp(app.wsgi_app, cookiejar=cj)
        set_constants("", TESTAPP)                


        
def funcsetup():
    """
    once per test
    """
    reload(decl)

        
def cleardown(config):
    backend.clean_dbase(config)


def initdb(config):
    backend.initdb(config)


####################


def capture_conversation(webob_request, webob_response):
    """
    Given a request and response object, format them nicely in ReSt style
    and push to a tmp file for later use.

    restrest assumes you are sending in webob objects
    """
    rst = restrest.restrest(webob_request, webob_response, shortformat=False)
    fo = open("/tmp/output.rst", "a")
    fo.write(rst)
    fo.close()

def parse_args():
    parser = OptionParser()
    parser.add_option("--host", dest="host",
                      help="hostname to listen on")
    parser.add_option("--port", dest="port",
                      help="port to listen on", type="int")
    parser.add_option("--debug", dest="debug", action="store_true",
                      help="debug on.", default=False)

    parser.add_option("--conf", dest="conf",
                      help="Path to config file.")

    (options, args) = parser.parse_args()
    return (options, args)


def build_environ():
    """
    We are playing at a low level with WSGI - wanting to wrap repoze.
    http://www.python.org/dev/peps/pep-0333/

    To test manually we need to generate correct HTTP Headers
    """
    import StringIO
    request_fo = StringIO.StringIO()
    err_fo = StringIO.StringIO()

    # wsgi reqd keys and default valus
    wsgi_specific_headers = {"wsgi.version": (1, 0),
                             "wsgi.url_scheme": "http",
                             "wsgi.input": request_fo,
                             "wsgi.errors": err_fo,
                             "wsgi.multithread": False,
                             "wsgi.multiprocess": False,
                             "wsgi.run_once": False
                             }

    ### key = HEADER (RFCLOC, NOTNULL, validvalues)
    HTTP_HEADERS = {"REQUEST_METHOD": "GET",
                    "SCRIPT_NAME": "module",
                    "PATH_INFO": "/cnxmodule:1234/",
                    "QUERY_STRING": "",
                    "CONTENT_TYPE": "",
                    "CONTENT_LENGTH": "",
                    "SERVER_NAME": "1.2.3.4",
                    "SERVER_PORT": "80",
                    "SERVER_PROTOCOL": "HTTP/1.1",
                    }
    d = {}
    d.update(wsgi_specific_headers)
    d.update(HTTP_HEADERS)
    return d



### get a anonymous session - sessionid and userid
def get_anon_session(wapp):
    """
    connect to the wsgi server, through HTTP or webtest, and obtain
    a session and a user ID
    
    requests is a much easier api to use...
    
    """
    
    r1 = wapp.get("%s/autosession" % USERHOST)
    lgr.info(">>>>><<<<<" + str(r1))
    lgr.info("222>>>>><<<<<" + str(wapp.cookies))
    sessionid = wapp.cookies['cnxsessionid']


    r2 = wapp.get("%s/me" % USERHOST)
    r2 = r2.maybe_follow()
    user_id = r2.json['user_id']
    return (sessionid, user_id)


MODULEURI, COLLECTIONURI, FOLDERURI, developers, USERHOST, GOODUSERSESSIONID, GOODUSERID,\
    OTHERUSERSESSIONID, OTHERUSERID, BADUSERSESSIONID, BADUSERID = list((None,)*11)

USERHOST = "http://localhost:8000/"
def set_constants(httpproxy, wapp):

    global MODULEURI, COLLECTIONURI, FOLDERURI, developers, USERHOST, GOODUSERSESSIONID, GOODUSERID,\
    OTHERUSERSESSIONID, OTHERUSERID, BADUSERSESSIONID, BADUSERID
    
    ###### CONSTANTS FOR TESTING.
    MODULEURI = "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126"
    COLLECTIONURI = "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"
    FOLDERURI = "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707"

    USERHOST = httpproxy
    GOODUSERSESSIONID, GOODUSERID = get_anon_session(wapp)
    OTHERUSERSESSIONID, OTHERUSERID = get_anon_session(wapp)
    BADUSERSESSIONID, BADUSERID = get_anon_session(wapp)

    developers = {"GOODUSER":
                       {"name": "good user",
                       "uri": GOODUSERID,
                       "fakesessionid": GOODUSERSESSIONID
                       },
                  "OTHERUSER":
                      {"name": "other user",
                       "uri": OTHERUSERID,
                       "fakesessionid": OTHERUSERSESSIONID
                       },
                  "BADUSER":
                      {"name": "bad user",
                       "uri": BADUSERID, 
                       "fakesessionid": BADUSERSESSIONID
                       }
                      }

    lgr.info("Developers: %s" % developers)
    ########################

def get_cookie_hdr(fakesessionid):
    """
    We want to send in fake session cookies
    that resolve to known test users.
    We can choose which test user (ie can edit or not)
    buy passing in uuid of 0000's or 01 02

    """
    COOKIEHEADER = "Cookie"
    headerd = {COOKIEHEADER: "cnxsessionid=%s" % fakesessionid}
    return headerd


APIMAP = {'module':
         {"POST": urlparse.urljoin(USERHOST, "module/"),
          "GET": urlparse.urljoin(USERHOST, "module/%(id_)s"),
          "PUT": urlparse.urljoin(USERHOST, "module/%(id_)s"),
          "DELETE": urlparse.urljoin(USERHOST, "module/%(id_)s"),
          },

          'collection':
         {"POST": urlparse.urljoin(USERHOST, "collection/"),
          "GET": urlparse.urljoin(USERHOST, "collection/%(id_)s"),
          "PUT": urlparse.urljoin(USERHOST, "collection/%(id_)s"),
          "DELETE": urlparse.urljoin(USERHOST, "collection/%(id_)s"),
          },

          'folder':
         {"POST": urlparse.urljoin(USERHOST, "folder/"),
          "GET": urlparse.urljoin(USERHOST, "folder/%(id_)s"),
          "PUT": urlparse.urljoin(USERHOST, "folder/%(id_)s"),
          "DELETE": urlparse.urljoin(USERHOST, "folder/%(id_)s"),
          },

          'workspace':
         {"GET": urlparse.urljoin(USERHOST, "workspace/"),
          },

          'logging':
         {"POST": urlparse.urljoin(USERHOST, "logging"),
          },

          
          }


def get_url(resourcetype, id_=None, method=None):
    """ return the correct URL to call for various resource operations

    >>> get_url("collection", id_=None, method="POST")
    'http://localhost:8000/collection/'

    >>> get_url("folder", id_=None, method="POST")
    'http://localhost:8000/folder/'

    >>> get_url("module", method="POST")
    'http://localhost:8000/module/'

    >>> get_url("module", id_="xxx", method="GET")
    'http://localhost:8000/module/xxx'

 
    >>> get_url("collection", id_="xxx", method="GET")
    'http://localhost:8000/collection/xxx'

    >>> get_url("collection", id_="xxx", method="GET")
    'http://localhost:8000/collection/xxx'

    >>> get_url("folder", id_="xxx", method="GET")
    'http://localhost:8000/folder/xxx'

    >>> get_url("folder", id_="xxx", method="PUT")
    'http://localhost:8000/folder/xxx'

    >>> get_url("module", id_="xxx", method="PUT")
    'http://localhost:8000/module/xxx'

    >>> get_url("module", id_="xxx", method="DELETE")
    'http://localhost:8000/module/xxx'

    >>> get_url("workspace", id_=None, method="GET")
    'http://localhost:8000/workspace/'


    Its pretty simple api so far...

    .. todo::
       ensure urljoin is done well - urlparse version not really as expected...

    """
    # restype, id method
    ## what if invalid restype?
    baseurl = APIMAP[resourcetype][method]

    if baseurl.find("%") >= 0:
        url = baseurl % {"id_": id_}
    else:
        url = baseurl
    return url

##################
### Generic test routines, using a ``WebTest`` object and
### running appropriate GET / PUT etc on it
##################


def wapp_get(wapp, resourcetype, id_, test_session_id, URL=None):
    """ """
    ## bit specific exceotion here todo:: fix this whole wappget approach
    if URL is None:
        headerd = get_cookie_hdr(test_session_id)
        URL = get_url(resourcetype, id_=id_, method="GET")
    else:
        headerd = get_cookie_hdr(test_session_id)
    ###
    req = TestRequest.blank(URL, method="GET",
                            headers=headerd)
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp =  wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    ###
    return resp


def wapp_post(wapp, resourcetype, data, test_session_id):
    """

    We build the request as a blank and copy it to allow restrest to work

    """
    URL = get_url(resourcetype, id_=None, method="POST")

    headerd = get_cookie_hdr(test_session_id)
    ###
    data_as_json = json.dumps(data)

    
    lgr.info("URL: %s" % URL)
    lgr.info("body: %s" % data_as_json[:100])
    lgr.info("hdrs: %s" % headerd)    
    req = TestRequest.blank(URL, method="POST",
                            body=data_as_json,
                            headers=headerd)
    req.content_type="application/json; charset=utf-8"
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp =  wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    ###
    return resp


def wapp_delete(wapp, resourcetype, id_, test_session_id):
    """
    """
    URL = get_url(resourcetype, id_=id_, method="DELETE")
    headerd = get_cookie_hdr(test_session_id)

    req = TestRequest.blank(URL, method="DELETE",
                            headers=headerd)
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp =  wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    return resp


def wapp_put(wapp, resourcetype, data, test_session_id, id_=None):
    headerd = get_cookie_hdr(test_session_id)
    URL = get_url(resourcetype, method="PUT", id_=id_)

    ###
    data_as_json = json.dumps(data)
    req = TestRequest.blank(URL, method="PUT",
                            body=data_as_json,
                            headers=headerd)
    req.content_type="application/json; charset=utf-8"
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp =  wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    ###

    return resp


#############
## Individual tests - run in order appearing
## Each builds on previous changes to DBase
#############

@with_setup(funcsetup)
def test_show_env():
    """display whats what    """
    print "%s " % USERHOST
    
@with_setup(funcsetup)    
def test_post_module():
    resp = wapp_post(TESTAPP,
                     "module",
                     decl.declarationdict['module'],
                     GOODUSERSESSIONID)
    returned_module_uri = resp.json['id']
    assert returned_module_uri == MODULEURI

@with_setup(funcsetup)
def test_put_module():
    data = decl.declarationdict['module']
    data['acl'] = [developers['OTHERUSER']['uri'],]
    data['body'] = "<p> Shortened body in test_put_module"
    resp = wapp_put(TESTAPP, "module", data, GOODUSERSESSIONID, MODULEURI)
    assert developers['OTHERUSER']['uri'] in resp.json['acl']

    ### So, user 0002 (ross) is RW on this module

@with_setup(funcsetup)    
def test_put_module_by_otheruser():
    data = decl.declarationdict['module']
    data['body'] = "<p> OTHERUSERSESSIONID has set this"
    resp = wapp_put(TESTAPP, "module", data, OTHERUSERSESSIONID, MODULEURI)
    assert "OTHERUSERSESSIONID" in resp.json['body']

    ### So, user 0002 (ross) is allowed to put on this module

@with_setup(funcsetup)
def test_get_module():
    resp = wapp_get(TESTAPP, "module",
                    "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126",
                    GOODUSERSESSIONID)
    assert resp.status_int == 200

@with_setup(funcsetup)
def test_valid_fields_in_GET():
    """Are we getting back the editor and translator fields

    XXX: this should simply expand to be a jsonschema compliance test"""
    resp = wapp_get(TESTAPP, "module",
                    "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126",
                    GOODUSERSESSIONID)
    assert "translators" in resp.json.keys()
    assert "editors" in resp.json.keys()

    
    

@with_setup(funcsetup)
def test_post_folder():
    resp = wapp_post(TESTAPP, "folder", decl.declarationdict[
                     'folder'], GOODUSERSESSIONID)
    returned_folder_uri = resp.json['id']
    assert returned_folder_uri == FOLDERURI


@with_setup(funcsetup)
def test_put_folder():
    data = decl.declarationdict['folder']
    data['acl'] = [OTHERUSERSESSIONID,]
    data['body'] = ["cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126",
                    "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41127"]
    resp = wapp_put(TESTAPP, "folder", data, GOODUSERSESSIONID, FOLDERURI)
    assert "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126" ==\
           resp.json['body'][0]['id']

### Folders are returned as follows
#    {u'body': [{u'title': u'Introduction', u'mediaType': u'application/vnd.org.cnx.module', u'id': u'cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126'}],


@with_setup(funcsetup)
def test_get_folder():
    resp = wapp_get(TESTAPP, "folder", "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707", GOODUSERSESSIONID, None)
    assert resp.json['id'] == "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707"


@with_setup(funcsetup)
def test_post_collection():
    data = decl.declarationdict['collection']
    resp = wapp_post(TESTAPP, "collection", data, GOODUSERSESSIONID)
    returned_collection_uri = resp.json['id']
    assert returned_collection_uri == COLLECTIONURI


@with_setup(funcsetup)
def test_put_collection():
    data = decl.declarationdict['collection_small']
    data['acl'] = [OTHERUSERSESSIONID,]
    resp = wapp_put(TESTAPP, "collection", data, GOODUSERSESSIONID, COLLECTIONURI)
    assert resp.json['body'].find('href="cnxmodule:d3911c28') > -1


@with_setup(funcsetup)
def test_get_collection():
    resp = wapp_get(TESTAPP, "collection",
                    "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"
                    , GOODUSERSESSIONID, None)
    assert resp.json['id'] == "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"


@with_setup(funcsetup)
def test_put_collection_otheruser():
    data = decl.declarationdict['collection']
    data['body'] = ["cnxmodule:SHOULDNEVERHITDB0", ]
    resp = wapp_put(TESTAPP, "collection", data, BADUSERSESSIONID, COLLECTIONURI)
    assert resp.status_int == 403, resp.status_int


### Testing GAC 
@with_setup(funcsetup)
def test_put_googleanalytics_module():
    """
    """
    data = decl.declarationdict['module']
    gacval = """UA-12345678-1"""
    data['googleTrackingID'] = gacval
    resp = wapp_put(TESTAPP, "module", data, GOODUSERSESSIONID, MODULEURI)
    assert 'googleTrackingID' in resp.json.keys()
    assert resp.json['googleTrackingID'] == gacval


@with_setup(funcsetup)
def test_put_badgoogleanalytics_module():
    """
    """
    data = decl.declarationdict['module']
    gacval = """<script>evil</script>"""
    data['googleTrackingID'] = gacval
    resp = wapp_put(TESTAPP, "module", data, GOODUSERSESSIONID, MODULEURI)
    assert resp.status_int == 400
    #data['googleTrackingID'] = ""  ##this should be dealt with in setup...    

    

@with_setup(funcsetup)
def test_put_googleanalytics_collection():
    """
    """
    data = decl.declarationdict['collection']
    data['googleTrackingID'] = """UA-12345678-1"""
    resp = wapp_put(TESTAPP, "collection", data,
                    GOODUSERSESSIONID, COLLECTIONURI)
    assert 'googleTrackingID' in resp.json.keys()

###            

@with_setup(funcsetup)
def test_dateModifiedStamp():
    data = decl.declarationdict['module']
    data['body'] = "Declaration test text"

    lgr.info(data)
    resp = wapp_put(TESTAPP, "module", data, GOODUSERSESSIONID, MODULEURI)
    assert resp.status_int == 200
    assert resp.json['dateLastModifiedUTC'] != resp.json['dateCreatedUTC']

@with_setup(funcsetup)
def test_put_module_rouser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP, "module", data, BADUSERSESSIONID, MODULEURI)
    assert resp.status_int == 403, resp.status_int

def ntest_put_module_baduser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP, "module", data, BADUSERSESSIONID, MODULEURI)
    assert resp.status_int == 403, resp.status_int

@with_setup(funcsetup)
def test_put_folder_ro():
    data = decl.declarationdict['folder']
    data['body'] = ["THIS IS TEST", ]
    resp = wapp_put(TESTAPP, "folder", data, BADUSERSESSIONID, FOLDERURI)
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_read_module_rouser():
    resp = wapp_get(TESTAPP, "module", MODULEURI, OTHERUSERSESSIONID)
    assert resp.status_int == 200, resp.status_int


@with_setup(funcsetup)
def test_read_folder_gooduser():
    resp = wapp_get(TESTAPP, "folder", FOLDERURI, GOODUSERSESSIONID)
    assert resp.status_int == 200, resp.status_int


@with_setup(funcsetup)
def test_read_module_baduser():
    resp = wapp_get(TESTAPP, "module", MODULEURI, BADUSERSESSIONID)
    assert resp.status_int == 403, resp.status_int



@with_setup(funcsetup)
def test_get_workspace_good():
    resp = wapp_get(TESTAPP, "workspace", None, GOODUSERSESSIONID)
    assert len(resp.json) == 3
    assert resp.status_int == 200, resp.status_int



###############


@with_setup(funcsetup)
def test_delete_module_baduser():
    resp = wapp_delete(TESTAPP, "module", MODULEURI, BADUSERSESSIONID)
    assert resp.status_int == 403, resp.status_int



@with_setup(funcsetup)
def test_delete_module_good():
    resp = wapp_delete(TESTAPP, "module", MODULEURI, GOODUSERSESSIONID)
    assert resp.status_int == 200, resp.status_int

###


@with_setup(funcsetup)
def test_delete_collection_baduser():
    resp = wapp_delete(TESTAPP, "collection", COLLECTIONURI, BADUSERSESSIONID)
    assert resp.status_int == 403, resp.status_int



@with_setup(funcsetup)
def test_delete_collection_good():
    resp = wapp_delete(TESTAPP, "collection", COLLECTIONURI, GOODUSERSESSIONID)
    assert resp.status_int == 200, resp.status_int

###


@with_setup(funcsetup)
def test_delete_folder_baduser():
    resp = wapp_delete(TESTAPP, "folder", FOLDERURI, BADUSERSESSIONID)
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_delete_folder_good():
    resp = wapp_delete(TESTAPP, "folder", FOLDERURI, GOODUSERSESSIONID)
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_whoami():
    resp = wapp_get(TESTAPP, "-", None,
                    GOODUSERSESSIONID,
                    URL="http://localhost:8000/me/"
    )
    assert resp.status_int == 200
    assert resp.json["user_id"] == GOODUSERID


if __name__ == '__main__':
    import doctest
    doctest.testmod()
