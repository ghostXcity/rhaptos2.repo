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

Basics: webtest is a wsgi filter from paster that will accept a wsgi application
and *spit out the HTTP calls it would have sent if it was in a HTTP server*

Thus we can run our application in the webtest rig, and locally see what it does,  or we can invert it, run the application in the rig, capture the HTTP request
and pipe that to a real server.  With proper threading, we can do this as a performance test too.

So it may seem a bit complex, but its not that insane


ToDo:

* split the test library and the test defintions out a bit
* make thread safe
* group tests in better ways than order-in-module



"""

import pprint
import logging
### logging is hard to get working with nose, so just dump
import sys
err = sys.stderr

import decl
import restrest
from rhaptos2.repo import (make_app, backend,
                           sessioncache,
                           )
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


    ####################
    ## Tools - some duplication here


def validate_uuid_format(uuidstr):
    """
    Given a string, try to ensure it is of type UUID.


    >>> validate_uuid_format("75e06194-baee-4395-8e1a-566b656f6920")
    True
    >>> validate_uuid_format("cnxmodule:75e06194-baee-4395-8e1a-566b656f6920")
    True
    >>> validate_uuid_format("FooBar")
    False

    """
    try:
        urn, uid = uuidstr.split(":")
    except:
        uid = uuidstr
    try:
        l = uid.split("-")
    except:
        return False

    res = [len(item) for item in l]
    if not res == [8, 4, 4, 4, 12]:
        return False
    else:
        return True


    ########################################################################
    # module level setup for nosetests
    ########################################################################

### globals - not thread safe and done only for expediency.
developers = None
RECORDTRAIL = {}
USERHOST = None

TESTCONFIG = None
TESTAPP = None

#############


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
    cj = cookielib.CookieJar()

    ### Are we running by generating HTTP to fire at webserver
    ### or are we testing wsgi calls?
    if 'HTTPPROXY' in config.keys():
        app = WSGIProxyApp(config['HTTPPROXY'])
        app.debug = True
        TESTAPP = TestApp(app, extra_environ={
                          'REMOTE_ADDR': '1.2.3.4'}, cookiejar=cj)
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


### get a anonymous session - sessionid and userid
def get_anon_session(wapp):
    """
    connect to the wsgi server, through HTTP or webtest, and obtain
    a session and a user ID

    requests is a much easier api to use...

    """

    r1 = wapp.get("%s/autosession" % USERHOST)
    sessionid = wapp.cookies['cnxsessionid']

    r2 = wapp.get("%s/me" % USERHOST)
    r2 = r2.maybe_follow()
    user_id = r2.json['user_id']
    return (sessionid, user_id)


def set_constants(httpproxy, wapp):
    """
    allow setup to 'reset' constants.

    Clearly a neater solution is needed
    """
    global developers, USERHOST

    USERHOST = httpproxy
    GOODUSERSESSIONID, GOODUSERID = get_anon_session(wapp)
    OTHERUSERSESSIONID, OTHERUSERID = get_anon_session(wapp)
    BADUSERSESSIONID, BADUSERID = get_anon_session(wapp)

    developers = {"GOODUSER":
                 {"name": "good user",
                  "uri": GOODUSERID,
                  "sessionid": GOODUSERSESSIONID
                  },
                  "OTHERUSER":
                 {"name": "other user",
                  "uri": OTHERUSERID,
                  "sessionid": OTHERUSERSESSIONID
                  },
                  "BADUSER":
                 {"name": "bad user",
                  "uri": BADUSERID,
                  "sessionid": BADUSERSESSIONID
                  }
                      }

    err.write("\n"+"Developers: %s" % developers)
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


APIMAP = {'content':
         {"POST": urlparse.urljoin(USERHOST, "/content/"),
          "GET": urlparse.urljoin(USERHOST, "/content/%(id_)s"),
          "PUT": urlparse.urljoin(USERHOST, "/content/%(id_)s"),
          "DELETE": urlparse.urljoin(USERHOST, "/content/%(id_)s"),
          },

          'workspace':
         {"GET": urlparse.urljoin(USERHOST, "/workspace/"),
          },

          'logging':
         {"POST": urlparse.urljoin(USERHOST, "/logging"),
          },


          }


def get_url(resourcetype, id_=None, method=None):
    """ return the correct URL to call for various resource operations

    >>> get_url("content", id_=None, method="GET")
    'http://localhost:8000/content/'

    >>> get_url("content", id_=111, method="GET")
    'http://localhost:8000/content/111'

    >>> get_url("workspace", id_=None, method="GET")
    'http://localhost:8000/workspace/'

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
    return str(url)  # Ensure urls are "native strings" complies with PEP-333 and stops webob moaning.

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
    resp = wapp.do_request(req, status="*", expect_errors=True)
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

    err.write("\n"+"URL: %s" % URL)
    err.write("\n"+"body: %s" % data_as_json[:100])
    err.write("\n"+"hdrs: %s" % headerd)
    req = TestRequest.blank(URL, method="POST",
                            body=data_as_json,
                            headers=headerd)
    req.content_type = "application/json; charset=utf-8"
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp = wapp.do_request(req, status="*", expect_errors=True)
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
    resp = wapp.do_request(req, status="*", expect_errors=True)
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
    req.content_type = "application/json; charset=utf-8"
    for k, v in wapp.extra_environ.items():
        req.environ.setdefault(k, v)
    reqcp = req.copy()
    resp = wapp.do_request(req, status="*", expect_errors=True)
    capture_conversation(reqcp, resp)
    ###

    return resp


########################################################################################
## Individual tests - run in order appearing
## Each builds on previous changes to DBase
#############


@with_setup(funcsetup)
def test_show_env():
    """display whats what    """
    err.write("\n"+"est_show_env: HTTP_HOST:%s RECORDTRAIL: %s "
              % (USERHOST, RECORDTRAIL))
    assert 1 == 1


@with_setup(funcsetup)
def test_post_module():

    data = decl.declarationdict['module']
    resp = wapp_post(TESTAPP,
                     "content",
                     data,
                     developers['GOODUSER']['sessionid'])
    assert resp.status_code == 200
    returned_module_uri = resp.json['id']
    err.write("\n"+"test_post_module-> %s" % returned_module_uri)
    assert validate_uuid_format(returned_module_uri) == True
    RECORDTRAIL['module_uid'] = returned_module_uri
    err.write("\n"+"test_post_module-> RECORDTRAIL: %s" % RECORDTRAIL)


@with_setup(funcsetup)
def test_post_folder():
    fldr = decl.declarationdict['folder']
    fldr['body'].append(RECORDTRAIL['module_uid'])
    resp = wapp_post(TESTAPP, "content",
                     fldr,
                     developers['GOODUSER']['sessionid'])
    returned_folder_uri = resp.json['id']
    RECORDTRAIL['folder_uid'] = returned_folder_uri
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_post_collection():
    data = decl.declarationdict['collection']
    resp = wapp_post(TESTAPP, "content", data, developers[
                     'GOODUSER']['sessionid'])
    returned_collection_uri = resp.json['id']
    RECORDTRAIL['collection_uid'] = returned_collection_uri
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_put_module():
    err.write("\n"+"test_put_module-> RECORDTRAIL: %s" % RECORDTRAIL)
    data = decl.declarationdict['module']
    data['body'] = "<p> Shortened body in test_put_module"
    data['id_'] = RECORDTRAIL['module_uid']
    err.write("\n"+"test_put_module-> ")
    resp = wapp_put(TESTAPP, "content", data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    err.write("\n"+"test_put_module: %s" % data['id_'])
    assert "Short" in resp.json['body']


@with_setup(funcsetup)
def test_put_module_acls():
    err.write("\n"+"test_put_module-> RECORDTRAIL: %s" % RECORDTRAIL)
    data = decl.declarationdict['module']
    data['acl'] = [developers['OTHERUSER']['uri'], ]
    data['body'] = "<p> This should have new acl list"
    data['id_'] = RECORDTRAIL['module_uid']

    resp = wapp_put(TESTAPP, "content", data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    err.write("\n"+"test_put_module: %s" % data['id_'])
    assert developers['OTHERUSER']['uri'] in resp.json['acl']
    assert "should" in resp.json['body']


@with_setup(funcsetup)
def test_put_module_by_otheruser():
    data = decl.declarationdict['module']
    data['body'] = "<p> developers['OTHERUSER']['sessionid'] has set this"
    resp = wapp_put(TESTAPP, "content", data, developers[
                    'OTHERUSER']['sessionid'], RECORDTRAIL['module_uid'])
    assert "developers['OTHERUSER']['sessionid']" in resp.json['body']

    ### So, user 0002 (ross) is allowed to put on this module


@with_setup(funcsetup)
def test_put_collection():
    data = decl.declarationdict['collection_small']
    data['acl'] = [developers['OTHERUSER']['sessionid'], ]
    resp = wapp_put(TESTAPP, "content",
                    data, developers['GOODUSER']['sessionid'], RECORDTRAIL['collection_uid'])
    assert resp.json['body'].find('href="cnxmodule:d3911c28') > -1


@with_setup(funcsetup)
def test_put_collection_otheruser():
    data = decl.declarationdict['collection']
    data['body'] = ["cnxmodule:SHOULDNEVERHITDB0", ]
    resp = wapp_put(TESTAPP, "content",
                    data, developers['BADUSER']['sessionid'], RECORDTRAIL['collection_uid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_put_folder():
    fldr = decl.declarationdict['folder']
    fldr['acl'] = [developers['OTHERUSER']['sessionid'], ]
    fldr['title'] = "New title for folder"
    resp = wapp_put(TESTAPP,
                    "content",
                    fldr,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['folder_uid'])
    assert resp.status_int == 200


######################## POSTS AND PUTS /
@with_setup(funcsetup)
def test_get_module():

    resp = wapp_get(TESTAPP, "content",
                    RECORDTRAIL['module_uid'],
                    developers['GOODUSER']['sessionid'])
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_valid_fields_in_GET():
    """Are we getting back the editor and translator fields

    XXX: this should simply expand to be a jsonschema compliance test"""
    resp = wapp_get(TESTAPP,
                    "content",
                    RECORDTRAIL['module_uid'],
                    developers['GOODUSER']['sessionid'])
    assert "translators" in resp.json.keys()
    assert "editors" in resp.json.keys()


### Folders are returned as follows
#    {u'body': [{u'title': u'Introduction', u'mediaType': u'application/vnd.org.cnx.module', u'id': u'cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126'}],


@with_setup(funcsetup)
def dtest_get_folder():
    resp = wapp_get(
        TESTAPP,
        "content",
        "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707",
        developers['GOODUSER']['sessionid'], None)
    assert resp.json['id'] == "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707"


@with_setup(funcsetup)
def test_get_collection():
    resp = wapp_get(TESTAPP,
                    "content",
                    RECORDTRAIL['collection_uid'],
                    developers['GOODUSER']['sessionid'], None)
    assert resp.json['id'] == RECORDTRAIL['collection_uid']


### Testing GAC
@with_setup(funcsetup)
def test_put_googleanalytics_module():
    """
    """
    data = decl.declarationdict['module']
    gacval = """UA-12345678-1"""
    data['googleTrackingID'] = gacval
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    assert 'googleTrackingID' in resp.json.keys()
    assert resp.json['googleTrackingID'] == gacval


@with_setup(funcsetup)
def test_put_badgoogleanalytics_module():
    """
    """
    data = decl.declarationdict['module']
    gacval = """<script>evil</script>"""
    data['googleTrackingID'] = gacval
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    assert resp.status_int == 400


@with_setup(funcsetup)
def test_put_googleanalytics_collection():
    """
    """
    data = decl.declarationdict['collection']
    data['googleTrackingID'] = """UA-12345678-1"""
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['collection_uid'])
    assert 'googleTrackingID' in resp.json.keys()


@with_setup(funcsetup)
def test_dateModifiedStamp():
    data = decl.declarationdict['module']
    data['body'] = "Declaration test text"
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['GOODUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    assert resp.status_int == 200
    assert resp.json['dateLastModifiedUTC'] != resp.json['dateCreatedUTC']


@with_setup(funcsetup)
def test_put_module_rouser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['BADUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    assert resp.status_int == 403, resp.status_int


def ntest_put_module_baduser():
    data = decl.declarationdict['module']
    data['body'] = "NEVER HIT DB"
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['BADUSER']['sessionid'],
                    RECORDTRAIL['module_uid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_put_folder_ro():
    data = decl.declarationdict['folder']
    data['body'] = ["THIS IS TEST", ]
    resp = wapp_put(TESTAPP,
                    "content",
                    data,
                    developers['BADUSER']['sessionid'],
                    RECORDTRAIL['folder_uid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_read_module_rouser():
    resp = wapp_get(TESTAPP,
                    "content",
                    RECORDTRAIL['module_uid'],
                    developers['OTHERUSER']['sessionid'])
    assert resp.status_int == 200, resp.status_int


@with_setup(funcsetup)
def test_read_folder_gooduser():
    resp = wapp_get(TESTAPP, "content", RECORDTRAIL[
                    'folder_uid'], developers['GOODUSER']['sessionid'])
    assert resp.status_int == 200, resp.status_int


@with_setup(funcsetup)
def test_read_module_baduser():
    resp = wapp_get(TESTAPP, "content", RECORDTRAIL[
                    'module_uid'], developers['BADUSER']['sessionid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_get_workspace_good():
    resp = wapp_get(TESTAPP, "workspace", None, developers[
                    'GOODUSER']['sessionid'])
    assert len(resp.json) == 3
    assert resp.status_int == 200, resp.status_int


###############
@with_setup(funcsetup)
def test_delete_module_baduser():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'module_uid'], developers['BADUSER']['sessionid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_delete_module_good():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'module_uid'], developers['GOODUSER']['sessionid'])
    assert resp.status_int == 200, resp.status_int

###


@with_setup(funcsetup)
def test_delete_collection_baduser():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'collection_uid'], developers['BADUSER']['sessionid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_delete_collection_good():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'collection_uid'], developers['GOODUSER']['sessionid'])
    assert resp.status_int == 200, resp.status_int

###


@with_setup(funcsetup)
def test_delete_folder_baduser():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'folder_uid'], developers['BADUSER']['sessionid'])
    assert resp.status_int == 403, resp.status_int


@with_setup(funcsetup)
def test_delete_folder_good():
    resp = wapp_delete(TESTAPP, "content", RECORDTRAIL[
                       'folder_uid'], developers['GOODUSER']['sessionid'])
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_whoami():
    resp = wapp_get(TESTAPP, "-", None,
                    developers['GOODUSER']['sessionid'],
                    URL="http://localhost:8000/me/"
                    )
    assert resp.status_int == 200
    assert resp.json["user_id"] == GOODUSERID


@with_setup(funcsetup)
def test_atc_logging():
    testmsg = {"message-type": "log",
               "log-message": "This is log msg",
               "metric-label": None,
               "metric-value": None,
               "metric-type": None
               }

    resp = wapp_post(TESTAPP, "logging", testmsg, developers[
                     'GOODUSER']['sessionid'])
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_atc_triggerlogging():
    """
    the atc client is servicing a different format for now
    It is not expected these will be useful messages for debuigging
    and the story for atc to make them useful is 21 pts.
    """
    testmsg = {"trigger": "A message",
               }

    resp = wapp_post(TESTAPP, "logging", testmsg, developers[
                     'GOODUSER']['sessionid'])
    assert resp.status_int == 200


@with_setup(funcsetup)
def test_bad_atc_triggerlogging():
    """
    the atc client is servicing a different format for now
    It is not expected these will be useful messages for debuigging
    and the story for atc to make them useful is 21 pts.
    """
    testmsg = {"wibble": "A malformed message",
               }

    resp = wapp_post(TESTAPP, "logging", testmsg, developers[
                     'GOODUSER']['sessionid'])
    assert resp.status_int == 400

if __name__ == '__main__':
    import doctest
    doctest.testmod()
