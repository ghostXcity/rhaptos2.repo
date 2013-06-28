#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###

"""How does Authentication, Authorisation and Sessions work?
---------------------------------------------------------

We are operating a Single-Sign-On service, using `Valruse` to do the
authentication.

Workflow
~~~~~~~~

A user will hit the repo-home page, and :func:`handle_user_authentication`will be fired,
and based on the cookies stored in the user browser we will know one of three things
about the user.

* Never seen before
* Known user, no in session
* Known user, in session
* Edge cases

Usually they will choose to *login* and will be directed to the login page on
cnx-user.  Here, the cnx-user will authenticate them in some fashion (OpenID)
and the *redirect* the user browser back to the repo, with a *token*.

The repo then looks up this token against the cnx-user service.  And hey presto,
if the token matches, the repo knows they can trust the browser.  (assuming SSL
all the way)

The redirect hits at the `/valid` endpoint in the repo, which will check the
token against the cnx-user, and then ::


   authenticated_identifier_to_registered_user_details
    given a authenticated user ID (OpenID), look up the user details
    on cnx-user
   create_session()

At this point, we now have a user who logged in against `cnx-user`, has then proven to cnx-repo
that they did log in, and now has a session cookie set in their browser that the repo can
trust as password-replacement for a set period.

Temporary sessions
------------------

Temporary sessions, or *anonymous editing* is where a user *does not login* but uses the repo
anonymously, perhaps creating test modules.

This is supported by hitting the endpoint `/tempsession` which will trigger the view `temp_session`.
This in turn calls :func:`set_temp_session`.  Here we create both a random sessionID (as per usual for sessions)
and we *also* create a random `user_uri`.  This user_uri is used exactly as if it were a real registered user,
but it is never sent back to the cnx-user, instead it solely is used in ACLs on the unpub repo.

This way, at the end of a temp session, the user effectively loses all their edits.  This may want to be avoided,
and is possible but not yet implemented.




known issues
~~~~~~~~~~~~

* requesting_user_uri This is passed around a lot This is suboptimal, and I think
  should be replaced with passing around the environ dict as a means of linking
  functions with the request calling them

* I am still passing around the userd in ``g.`` This is fairly silly
  but seems consistent for flask. Will need rethink.

* secure (https) - desired future toggle

* further notes at http://executableopinions.mikadosoftware.com/en/latest/labs/webtest-cookie/cookie_testing.html

"""
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)

import os
import datetime
import json
import uuid

import flask
import requests
import statsd
from flask import abort, request, g, session, redirect
from flaskext.openid import OpenID
from webob import Request

from rhaptos2.repo.err import Rhaptos2Error, Rhaptos2NoSessionCookieError
from rhaptos2.repo import get_app, sessioncache


# Paths which do not require authorization.
DMZ_PATHS = ('/valid', '/autosession', '/favicon.ico', '/home', '/tempsession')
# The key used in session cookies.
CNX_SESSION_ID = "cnxsessionid"




########################
# User Auth flow
########################



def store_userdata_in_request(userd, sessionid):
    """
    given a userdict, keep it in the request cycle for later reference.
    Best practise here will depend on web framework.

    """
    ### For now keep ``g`` the source of data on current thread-local request.
    ### later we transfer to putting it all on environ for extra portability
    userd['user_uri'] = userd['user_id']
    g.userd = userd
    g.sessionid = sessionid
    lgr.info("SESSION LINKER, sessionid:%s::user_uri:%s::requestid:%s::" %
         (g.sessionid, userd['user_uri'], g.requestid))
    ### Now flask actually calls __call__


def handle_user_authentication(flask_request):
    """Correctly perform all authentication workflows

    We have 16 options for different user states such as IsLoggedIn, NotRegistered.
    The states are listed below.

    THis function is where *eventually* all 16 will be handled.  For the moment
    only a limited number are.

    :param flask_request: request object of pococo flavour.
    :returns: No return is good because it allows the onward rpocessing of requests.
    Otherwise we return a login page.


    This gets called on ``before_request`` (which is *after* processing of HTTP headers
    but *before* __call__ on wsgi.)

    .. note::

        All the functions in sessioncache, and auth, should be called from here
        (possibly in a chain) and raise errors or other signals to allow this function
        to take action, not to presume on some action (like a redirect)
        themselves. (todo-later: such late decisions are well suited for deferred
        callbacks)


    ====   ===  =========  ==============  ====================================  =================
    Auth   Reg  InSession  ProfileCookie   Next Action / RoleType                Handled Here
    ====   ===  =========  ==============  ====================================  =================
    Y      Y    Y          Y               Go                                    Y
    Y      Y    Y          N               set_profile_cookie                    Y
    Y      Y    N          Y               set_session                           Y
    Y      Y    N          N               FirstTimeOK

    Y      N    Y          Y               ErrorA
    Y      N    Y          N               ErrorB
    Y      N    N          Y               ErrorC
    Y      N    N          N               NeedToRegister

    N      N    Y          Y               AnonymousGo
    N      N    Y          N               set_profile_cookie
    N      N    N          Y               LongTimeNoSee
    N      N    N          N               FreshMeat

    N      Y    Y          Y               Conflict with anonymous and reg?
    N      Y    Y          N               Err-SetProfile-AskForLogin
    N      Y    N          Y               NotArrivedYet
    N      Y    N          N               CouldBeAnyone
    ====   ===  =========  ==============  ====================================  =================


    All the final 4 are problematic because if the user has not authorised
    how do we know they are registered? Trust the profile cookie?


    we examine the request, find session cookie,
    register any logged in user, or redirect to login pages

    """
    # clear down storage area.
    g.userd = None
    g.sessionid = None

    ### if someone is trying to login, it is the *only* time they should
    ### hit this wsgi app and *not* get bounced out for bad session
    ### FIXME - while this is the *only* exception I dont like the hardcoded manner
    ### options: have /login served by another app - ala Velruse?
    if flask_request.path in DMZ_PATHS:
        return None
        
    lgr.error("Auth test for %s" % flask_request.path)

    ### convert the cookie to a registered users details
    try:
        userdata, sessionid = session_to_user(
            flask_request.cookies, flask_request.environ)
    except Rhaptos2NoSessionCookieError, e:
        lgr.error("Session Lookup returned NoCookieError, so redirect to login")
        if 'cnxprofile' in flask_request.cookies:
            userdata, sessionid = set_temp_session()    
        else:
            abort(401)
        ### FIXME - add in temp session & fake userid.
        
        
    # We are at start of request cycle, so tell everything downstream who User
    # is.  If userdata not set, create a temp user and move on.
    if userdata is not None:
        store_userdata_in_request(userdata, sessionid)
    else:
        lgr.error("Session Lookup returned None User, so redirect to login")
        if 'cnxprofile' in flask_request.cookies:
            userdata, sessionid = set_temp_session()
            store_userdata_in_request(userdata, sessionid)
        else:
            abort(401)
        
##########################
## Session Cookie Handling
##########################


def session_to_user(flask_request_cookiedict, flask_request_environ):
    """
    Given a request environment and cookie



    >>> cookies = {"cnxsessionid": "00000000-0000-0000-0000-000000000000",}
    >>> env = {}
    >>> userd = session_to_user(cookies, env)
    >>> outenv["fullname"]
    'pbrian'

    :params flask_request_cookiedict: the cookiejar sent over as a dict(-like obj).
    :params flask_request_environ: a dict like object representing WSGI environ

    :returns: Err if lookup fails, userdict if not

    """
    if CNX_SESSION_ID in flask_request_cookiedict:
        sessid = flask_request_cookiedict[CNX_SESSION_ID]
    else:
        raise Rhaptos2NoSessionCookieError("NO SESSION")
    userdata = lookup_session(sessid)
    return (userdata, sessid)


def lookup_session(sessid):
    """
    As this will be called on *every* request and is a network lookup
    we should *storngly* look into redis-style lcoal disk cacheing
    performance monitoring of request life cycle?

    returns python dict of ``user_dict`` format.
            or None if no session ID in cache
            or Error if lookup failed for other reason.

    """
    lgr.error("begin look up sessid %s in cache" % sessid)
    try:
        userd = sessioncache.get_session(sessid)
        lgr.error("we got this from session lookup %s" % str(userd))
        if userd:
            lgr.error("We attempted to look up sessid %s in cache SUCCESS" %
                  sessid)
            return userd
        else:
            lgr.error("We attempted to look up sessid %s in cache FAILED" %
                  sessid)
            return None
    except Exception, e:
        lgr.error("We attempted to look up sessid %s in cache FAILED with Err %s" %
              (sessid, str(e)))
        raise e


def authenticated_identifier_to_registered_user_details(ai):
    """
    Given an ``authenticated_identifier (ai)`` request full user details from
    the ``user service``

    returns dict of userdetails (success),
            None (user not registerd)
            or error (user service down).

    """
    payload = {'user': ai}
    user_service_url = get_app().config['cnx-user-url']
    url = "%s/api/users/%s" % (user_service_url, ai)

    lgr.error("user info - from url %s and query string %s" %
                  (user_service_url, repr(payload)))

    try:
        resp = requests.get(url, params=payload)
    except requests.exceptions.RequestException:
        raise Rhaptos2Error("Problem communicating with the user service.")

    if resp.status_code == 404:
        return None
    if resp.status_code == 403:
        raise Rhaptos2Error("Access to user details denied. Do you have "
                            "permissions to use the user service?")
    if resp.status_code != 200:
        raise Rhaptos2Error("Problem communicating with the user service.")
    user_details = resp.json()

    lgr.error("Got back %s " % user_details)
    return user_details


def create_session(userdata):
    """A ``closure`` function that is stored and called at end of response,
    allowing us to set a cookie, with correct uuid, before response obj
    has been created (before request is processed !)

    :param: userdata - a ``userdict`` format.
    :returns: sessionid

    cookie settings:

    * cnxsessionid - a fixed key string that is constant
    * expires - we want a cookie that will live even if user
    shutsdown browser.  However do not live forever ...?
    * httponly - prevent easy CSRF, however allow AJAX to request browser
    to send cookie.

    """
    sessionid = str(uuid.uuid4())

    def begin_session(resp):
        resp.set_cookie('cnxsessionid', sessionid,
                        httponly=True,
                        expires=datetime.datetime.today()+datetime.timedelta(days=1))
        return resp

    def begin_profile(resp):
        # XXX Using the user information should be left to
        #     the client-side code. We should supply the client-side code with
        #     the id and url to the user profile. The user already has
        #     authorization to acquire their data.
        resp.set_cookie('cnxprofile', 'FOO',
                        httponly=True,
                        expires=datetime.datetime.today()+datetime.timedelta(days=365))
        return resp

    g.deferred_callbacks.append(begin_session)
    g.deferred_callbacks.append(begin_profile)
    sessioncache.set_session(sessionid, userdata)
    ### Now at end of request we will call begin_session() and its closure will
    ### set sessionid correctly.
    return sessionid


def delete_session(sessionid):
    """
    request browser temove cookie from client, remove from
    session-cache dbase.

    """

    def end_session(resp):
        resp.set_cookie('cnxsessionid', "SessionExpired",
                        expires=0,
                        httponly=True)
        return resp

    g.deferred_callbacks.append(end_session)
    sessioncache.delete_session(sessionid)
    ### Now at end of request we will call end_session() and its closure will
    ### set an invalid cookie, thus removeing the cookie in most cases.


def set_autosession():
    """
    This is a convenience function for development
    It should fail in production

    """
    userdict_example ={"interests": None, "identifiers": [{"identifierstring":
    "https://michaelmulich.myopenid.com", "user_id":
    "cnxuser:75e06194-baee-4395-8e1a-566b656f6924", "identifiertype":
    "openid"}], "user_id": "cnxuser:75e06194-baee-4395-8e1a-566b656f6924",
    "suffix": None, "firstname": None, "title": None, "middlename": None,
    "lastname": None, "imageurl": None, "otherlangs": None,
    "affiliationinstitution_url": None, "email": None, "version": None,
    "location": None, "recommendations": None, "preferredlang": None,
    "fullname": "Michael Mulich", "homepage": None, "affiliationinstitution":
    None, "biography": None}

    
    if not get_app().debug:
        raise Rhaptos2Error("autosession should fail in prod.")

    # check if session already live for this user?
    # Hmm I have not written such code yet - seems a problem
    # only likely to occur here...

    # FIXME get the real userdict template
    standarduser = userdict_example
    sessionid = create_session(standarduser)
    store_userdata_in_request(standarduser, sessionid)
    lgr.info("Session %s now has %s" % (sessionid, g.userd['user_id']))
    ### fake in three users of id 0001 002 etc
    sessioncache._fakesessionusers(sessiontype='fixed')
    store_userdata_in_request(standarduser, sessionid)
    return standarduser


def set_temp_session():
    """
    A temopriary session is not yet fully implemented
    A temporary session is to allow a unregistered and unauthorised user to
    vist the site, acquire a temporary userid and a normal session.

    Then they will be able to work as normal, the workspace and acls set to the just invented
    temporary id.

    However work saved will be irrecoverable after session expires...

    """
    useruri = create_temp_user(
        "temporary", "http:/openid.cnx.org/%s" % str(uuid.uuid4()))
    tempuserdict = {'fullname': "temporary user", 'user_id': useruri}
    sessionid = create_session(tempuserdict)
    return (tempuserdict, sessionid)


def create_temp_user(identifiertype, identifierstring):
    """
    We should ping to user service and create a temporary userid
    linked to a made up identifier.  This can then be linked to the
    unregistered user when they finally register.

    FIXME - needs to actually talk to userservice.
    THis is however a asynchronous problem, solve under session id
    """
    ### vist the user dbase, get back a user_uri
    stubbeduri = "cnxuser:" + str(uuid.uuid4())
    return stubbeduri

def whoami():
    """based on session cookie
    returns userd dict of user details, equivalent to mediatype from
    service / session
    """
    return g.userd

def apply_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

def logout():
    """kill the session in cache, remove the cookie from client"""
    raise NotImplementedError()

############################
# cnx-user communication API
############################

# cnx-user requires that a service have a /valid route to handle users when
#   they return from authenticating.

def valid():
    """cnx-user /valid view for capturing valid authentication requests."""
    user_token = request.args['token']
    next_location = request.args.get('next', '/')

    # Check with the service to verify authentication is valid.
    user_service_url = get_app().config['cnx-user-url']
    url = "%s/server/check" % user_service_url
    try:
        resp = requests.post(url, data={'token': user_token})
    except requests.exceptions.RequestException as exc:
        raise Rhaptos2Error("Invalid authentication token")
    if resp.status_code == 400:
        raise Rhaptos2Error("Invalid authentication token")
    elif resp.status_code != 200:
        raise Rhaptos2Error("Had problems communicating with the "
                            "authentication service")
    user_id = resp.json()['id']

    # Now that we have the user's authenticated id, we can associate the user
    #   with the system and any previous session.
    user_details = authenticated_identifier_to_registered_user_details(user_id)
    create_session(user_details)
    return redirect(next_location)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
