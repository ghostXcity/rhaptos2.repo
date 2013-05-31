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
tests - designed to use WebTest from paste.

ToDo:
at the moment we control every id and session id
Write tests that exercise the system without imposing the ids, so we can run tests
again without hitting PK errors or clearing dbase.



The DisconnectionError:

I was seeing a Client has disconnected error, which I traced to the readinto function of
request.py. This was a red herring it seems, as the cause of the error was
trying to read the body_file object (IOBase) a *second* time - once to read it when sending the request,
and once to read it in restrest.

The setting of the seek for the IO Object seemed too deep in the mire for me, so I resorted to simply
genrating a request object, copying it and *then* executing the request.  Seems to work fine. 

"""


import decl, restrest
from rhaptos2.repo import (make_app, backend,
                           sessioncache, dolog)
from webtest import TestApp, TestRequest
from wsgiproxy.app import WSGIProxyApp
from optparse import OptionParser
import urlparse
import requests
import json
from rhaptos2.repo.configuration import (  # noqa
    Configuration
)



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
                    "SERVER_PROTOCOL": "HTTP/1.1"
                    }
    d = {}
    d.update(wsgi_specific_headers)
    d.update(HTTP_HEADERS)
    return d


###### CONSTANTS FOR TESTING.
moduleuri = "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126"
collectionuri = "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"
folderuri = "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707"

userhost = "http://127.0.0.1:8000/"
### THis header is where we put the authenticated ID

### session IDs - need to link to fixed auth.py
def get_autosession():
    """
    """
    resp = requests.get(userhost + "/autosession")
    sessionid = resp.cookies['cnxsessionid']
    return str(sessionid)
    
RWUSERSESSIONID = "00000000-0000-0000-0000-000000000000"
ROUSERSESSIONID = "00000000-0000-0000-0000-000000000001"
BADUSERSESSIONID = "00000000-0000-0000-0000-000000000002"

#RWUSERSESSIONID = get_autosession()
#ROUSERSESSIONID = RWUSERSESSIONID
#BADUSERSESSIONID = RWUSERSESSIONID


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
         {"POST": urlparse.urljoin(userhost, "module/"),
          "GET": urlparse.urljoin(userhost, "module/%(id_)s"),
          "PUT": urlparse.urljoin(userhost, "module/%(id_)s"),
          "DELETE": urlparse.urljoin(userhost, "module/%(id_)s"),
          },

          'collection':
         {"POST": urlparse.urljoin(userhost, "collection/"),
          "GET": urlparse.urljoin(userhost, "collection/%(id_)s"),
          "PUT": urlparse.urljoin(userhost, "collection/%(id_)s"),
          "DELETE": urlparse.urljoin(userhost, "collection/%(id_)s"),
          },

          'folder':
         {"POST": urlparse.urljoin(userhost, "folder/"),
          "GET": urlparse.urljoin(userhost, "folder/%(id_)s"),
          "PUT": urlparse.urljoin(userhost, "folder/%(id_)s"),
          "DELETE": urlparse.urljoin(userhost, "folder/%(id_)s"),
          },

          'module_acl':
         {"POST": urlparse.urljoin(userhost, "module/%(id_)s/acl/"),
          "GET": urlparse.urljoin(userhost, "module/%(id_)s/acl/"),
          "PUT": urlparse.urljoin(userhost, "module/%(id_)s/acl/"),
          "DELETE": urlparse.urljoin(userhost, "module/%(id_)s/acl/"),
          },

          'collection_acl':
         {"POST": urlparse.urljoin(userhost, "collection/%(id_)s/acl/"),
          "GET": urlparse.urljoin(userhost, "collection/%(id_)s/acl/"),
          "PUT": urlparse.urljoin(userhost, "collection/%(id_)s/acl/"),
          "DELETE": urlparse.urljoin(userhost, "collection/%(id_)s/acl/"),
          },

          'folder_acl':
         {"POST": urlparse.urljoin(userhost, "folder/%(id_)s/"),
          "GET": urlparse.urljoin(userhost, "folder/%(id_)s/acl/"),
          "PUT": urlparse.urljoin(userhost, "folder/%(id_)s/acl/"),
          "DELETE": urlparse.urljoin(userhost, "folder/%(id_)s/acl/"),
          },

          'workspace':
         {"GET": urlparse.urljoin(userhost, "workspace/"),
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

    >>> get_url("collection_acl", id_="xxx", method="PUT")
    'http://localhost:8000/collection/xxx/acl/'

    >>> get_url("folder_acl", id_="xxx", method="PUT")
    'http://localhost:8000/folder/xxx/acl/'

    >>> get_url("module", id_="xxx", method="DELETE")
    'http://localhost:8000/module/xxx'

    >>> get_url("collection_acl", id_="xxx", method="DELETE")
    'http://localhost:8000/collection/xxx/acl/'

    >>> get_url("folder_acl", id_="xxx", method="DELETE")
    'http://localhost:8000/folder/xxx/acl/'

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
    req = TestRequest.blank(URL, method="POST",
                            body=data_as_json,
                            headers=headerd)
    req.content_type="application/json"
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
    req.content_type="application/json"
    reqcp = req.copy()
    resp =  wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    ###

    return resp


def test_post_module():
    resp = wapp_post(TESTAPP,
                     "module",
                     decl.declarationdict['module'],
                     RWUSERSESSIONID)
    returned_module_uri = resp.json['id']
    assert returned_module_uri == moduleuri
    #capture_conversation(resp)
    


def test_put_module():
    data = decl.declarationdict['module']
    data['acl'] = ['cnxuser:00000000-0000-0000-0000-000000000101',
                   'cnxuser:00000000-0000-0000-0000-000000000111']
    data['body'] = "<p> Shortened body in test_put_module"
    resp = wapp_put(TESTAPP, "module", data, RWUSERSESSIONID, moduleuri)
    assert 'cnxuser:00000000-0000-0000-0000-000000000101' in resp.json['acl'] 
###
    
    
def test_post_folder():
    resp = wapp_post(TESTAPP, "folder", decl.declarationdict[
                     'folder'], RWUSERSESSIONID)
    returned_folder_uri = resp.json['id']
    assert returned_folder_uri == folderuri
    

def test_put_folder():
    data = decl.declarationdict['folder']
    data['acl'] = ['cnxuser:00000000-0000-0000-0000-000000000101',
                   'cnxuser:00000000-0000-0000-0000-000000000111']
    data['body'] = ["cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126",
                    "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41127"]
    resp = wapp_put(TESTAPP, "folder", data, RWUSERSESSIONID, folderuri)
    assert "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126" ==\
           resp.json['body'][0]['id']

#    {u'body': [{u'title': u'Introduction', u'mediaType': u'application/vnd.org.cnx.module', u'id': u'cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126'}], 

def test_get_folder():
    resp = wapp_get(TESTAPP, "folder", "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707", RWUSERSESSIONID, None)
    assert resp.json['id'] == "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707"
    

def test_post_collection():
    data = decl.declarationdict['collection']
    resp = wapp_post(TESTAPP, "collection", data, RWUSERSESSIONID)
    returned_collection_uri = resp.json['id']
    assert returned_collection_uri == collectionuri


def test_put_collection():
    data = decl.declarationdict['collection_small']
    data['acl'] = ['cnxuser:00000000-0000-0000-0000-000000000101',
                   'cnxuser:00000000-0000-0000-0000-000000000111']
    resp = wapp_put(TESTAPP, "collection", data, RWUSERSESSIONID, collectionuri)
    assert resp.json['body'].find('href="cnxmodule:d3911c28') > -1

def test_get_collection():
    resp = wapp_get(TESTAPP, "collection",
                    "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"
                    , RWUSERSESSIONID, None)
    assert resp.json['id'] == "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7"
    
def ntest_put_collection_rouser():
    data = decl.declarationdict['collection']
    data['body'] = ["cnxmodule:SHOULDNEVERHITDB0", ]
    resp = wapp_put(TESTAPP, "collection", data, ROUSERSESSIONID, collectionuri)
    assert resp.status_int == 403


def ntest_put_collection_baduser():
    data = decl.declarationdict['collection']
    data['body'] = ["cnxmodule:SHOULDNEVERHITDB1", ]
    resp = wapp_put(TESTAPP, "collection", data, ROUSERSESSIONID, collectionuri)
    assert resp.status_int == 403

def test_dateModifiedStamp():
    data = decl.declarationdict['module']
    data['body'] = "Declaration test text"
    resp = wapp_put(TESTAPP, "module", data, RWUSERSESSIONID, moduleuri)
    assert resp.json['dateLastModifiedUTC'] != resp.json['dateCreatedUTC']
    
def ntest_put_module_rouser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP, "module", data, ROUSERSESSIONID, moduleuri)
    assert resp.status_int == 403


def ntest_put_module_baduser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP, "module", data, BADUSERSESSIONID, moduleuri)
    assert resp.status_int == 403




def ntest_put_folder_ro():
    data = decl.declarationdict['folder']
    data['body'] = ["THIS IS TEST", ]
    resp = wapp_put(TESTAPP, "folder", data, ROUSERSESSIONID, folderuri)
    assert resp.status_int == 403


def ntest_put_folder_bad():
    data = decl.declarationdict['folder']
    data['body'] = ["BADUSER", ]
    resp = wapp_put(TESTAPP, "folder", data, BADUSERSESSIONID, folderuri)
    assert resp.status_int == 403


def ntest_put_module_acl():
    data = decl.acllist
    resp = wapp_put(TESTAPP, "module_acl", data, RWUSERSESSIONID, moduleuri)
    assert resp.status_int == 200


    
def ntest_read_module_rouser():
    resp = wapp_get(TESTAPP, "module", moduleuri, ROUSERSESSIONID)
    assert resp.status_int == 200

def test_read_folder_gooduser():
    resp = wapp_get(TESTAPP, "folder", folderuri, RWUSERSESSIONID)
    assert resp.status_int == 200


def ntest_read_module_baduser():
    resp = wapp_get(TESTAPP, "module", moduleuri, BADUSERSESSIONID)
    assert resp.status_int == 403
    
    
def test_get_workspace_good():
    resp = wapp_get(TESTAPP, "workspace", None, RWUSERSESSIONID)
    assert len(resp.json) == 3   
    assert resp.status_int == 200

    
    
###############    

def ntest_delete_module_baduser():
    resp = wapp_delete(TESTAPP, "module", moduleuri, BADUSERSESSIONID)
    assert resp.status_int == 403


def ntest_delete_module_rouser():
    resp = wapp_delete(TESTAPP, "module", moduleuri, ROUSERSESSIONID)
    assert resp.status_int == 403

def test_delete_module_good():
    resp = wapp_delete(TESTAPP, "module", moduleuri, RWUSERSESSIONID)
    assert resp.status_int == 200

###
    
def ntest_delete_collection_baduser():
    resp = wapp_delete(TESTAPP, "collection", collectionuri, BADUSERSESSIONID)
    assert resp.status_int == 403


def ntest_delete_collection_rouser():
    resp = wapp_delete(TESTAPP, "collection", collectionuri, ROUSERSESSIONID)
    assert resp.status_int == 403


def test_delete_collection_good():
    resp = wapp_delete(TESTAPP, "collection", collectionuri, RWUSERSESSIONID)
    assert resp.status_int == 200

###
    
def ntest_delete_folder_baduser():
    resp = wapp_delete(TESTAPP, "folder", folderuri, BADUSERSESSIONID)
    assert resp.status_int == 403


def ntest_delete_folder_rouser():
    resp = wapp_delete(TESTAPP, "folder", folderuri, ROUSERSESSIONID)
    assert resp.status_int == 403


def test_delete_folder_good():
    resp = wapp_delete(TESTAPP, "folder", folderuri, RWUSERSESSIONID)
    assert resp.status_int == 200

def ntest_whoami():
    resp = wapp_get(TESTAPP, "-", None,
                    RWUSERSESSIONID,
                    URL="http://localhost:8000/me/"
    )
    assert resp.status_int == 200
    assert resp.json["name"] == "PaulRW" 
    assert resp.json["id"] == "cnxuser:75e06194-baee-4395-8e1a-566b656f6920" 

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
    #del config[defaultsection]
    return config


def setup():
    global TESTCONFIG
    global TESTAPP

    # using nose-testconfig we obtain the config dict passed in through the
    # nosetests command line
    from testconfig import config
    ## now "convert" to app-style dict
    TESTCONFIG = convert_config(config)
    initdb(TESTCONFIG)

    dolog("INFO", "WHAT THE HELL IS GOING ON WITH CONF %s %s" % (str(config), str(TESTCONFIG)))
    if 'HTTPPROXY' in config.keys():
        app = WSGIProxyApp(config['HTTPPROXY'])
        TESTAPP = TestApp(app, extra_environ={'REMOTE_ADDR': '1.2.3.4'})
    else:
        app = make_app(TESTCONFIG)
        app.debug = True
        sessioncache.set_config(config)
        TESTAPP = TestApp(app.wsgi_app)



    print "cookies", TESTAPP.cookies 

def cleardown(config):
    backend.clean_dbase(config)


def initdb(config):
    backend.initdb(config)
    ### kind of useless as have not instantiated the models yet.


    
if __name__ == '__main__':
    import doctest
    doctest.testmod()

