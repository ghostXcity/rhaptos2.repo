#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###

""":module:`auth` supplies the logic to authenticate users and then store that authentication
for later requests.
It is strongly linked with :module:`sessioncache`.

Future revisions will pull out the authentication chunk, to be replaced with user-profile-auth, however
the logic over authorisation will remain.


Overview

auth.handle_user_authentication is called on before_requset and will ensure we end up with a verified user in a session
or the user is unable to authenticate

after_authentication is called by the openid or similar machinery, to trigger the session cache mgmt


known issues
~~~~~~~~~~~~

requesting_user_uri This is passed around a lot This is suboptimal, and I think
should be replaced with passing around the environ dict as a means of linking
functions with the request calling them

I am still passing around the userd in ``g.`` This is fairly silly
but seems consistent for flask. Will need rethink.

secure (https) - desired future toggle

further notes at http://executableopinions.mikadosoftware.com/en/latest/labs/webtest-cookie/cookie_testing.html


userdict example::

    {"interests": null, "identifiers": [{"identifierstring": "https://michaelmulich.myopenid.com", "user_id": "cnxuser:75e06194-baee-4395-8e1a-566b656f6924", "identifiertype": "openid"}], "user_id": "cnxuser:75e06194-baee-4395-8e1a-566b656f6924", "suffix": null, "firstname": null, "title": null, "middlename": null, "lastname": null, "imageurl": null, "otherlangs": null, "affiliationinstitution_url": null, "email": null, "version": null, "location": null, "recommendations": null, "preferredlang": null, "fullname": "Michael Mulich", "homepage": null, "affiliationinstitution": null, "biography": null}

"""

import datetime
import os
import statsd
import json
import pprint
import uuid
from rhaptos2.repo.err import Rhaptos2Error, Rhaptos2NoSessionCookieError
from rhaptos2.repo import get_app, sessioncache
import flask
from flask import request, g, session, redirect
from flaskext.openid import OpenID
import requests
from webob import Request


import logging
lgr = logging.getLogger("authmodule")

### This is a temporary log fix
### The full fix is in branch fix-logging-importing
### THis is a temp workaround to handle the circular import


def dolog(lvl, msg):
    lgr.info(msg)


### global namespace placeholder
app = None


##########
### Module startup
##########

def setup_auth():
    """
    As part of drive to remove app setup from the import process,
    have moved to calls into this function.  This is driving
    a circular import cycle, which while temp solved will only
    be fixed by changing logging process.

    So to ensure docs work, and as a nod towards cleaning up the
    import-time work happening here, this needs to be called by run.

    """

    global app
    import views

    app = get_app()
    app.config.update(
        SECRET_KEY=app.config['openid_secretkey'],
        DEBUG=app.debug
    )

    # setup flask-openid
    #: we setup the loginhandler and after_login callbacks here
    #: flesh out docs
    oid = OpenID(app)
    # views - why here and not in __init
    oid.loginhandler(login)
    oid.after_login(create_or_login)


########################
# User Auth flow
########################

### this is key found in all session cookies
### It is hardcoded here not config.
CNXSESSIONID = "cnxsessionid"


def redirect_to_login():
    """
    On first hitting the site, the user will have no cookie
    If we issued a 301, the browser would issue another request,
    which would have no cookie, which would issue a 301...

    By presenting this HTML when the user hits the login server,
    we avoid this.  Clearly templating is needed.

    """
    tmpl = """<p>Hello It seems your session has expired.
    <p>Please <a href="/login">login again.</a>
    <p>Developers can <a href="/autosession">autosession</a> """
    resp = flask.make_response(tmpl)
    return resp


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
    dolog("INFO", "SESSION LINKER, sessionid:%s::user_uri:%s::requestid:%s::" %
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
    if flask_request.path in ("/login", "/favicon.ico", "/autosession"):
        return None
    dolog("INFO", "Auth test for %s" % flask_request.path)

    ### convert the cookie to a registered users details
    try:
        userdata, sessionid = session_to_user(
            flask_request.cookies, flask_request.environ)
    except Rhaptos2NoSessionCookieError, e:
        dolog(
            "INFO", "Session Lookup returned NoCookieError, so redirect to login")
        return redirect_to_login()
        # We end here for now - later we shall fix tempsessions
        # userdata = set_temp_session()

    # We are at start of request cycle, so tell everything downstream who User
    # is.
    if userdata is not None:
        store_userdata_in_request(userdata, sessionid)
    else:
        g.userd = None
        dolog(
            "INFO", "Session Lookup returned None User, so redirect to login")
        return redirect_to_login()

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
    if CNXSESSIONID in flask_request_cookiedict:
        sessid = flask_request_cookiedict[CNXSESSIONID]
    else:
        raise Rhaptos2NoSessionCookieError("NO SESSION - REDIRECT TO LOGIN")
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
    dolog("INFO", "begin look up sessid %s in cache" % sessid)
    try:
        userd = sessioncache.get_session(sessid)
        dolog("INFO", "we got this from session lookup %s" % str(userd))
        if userd:
            dolog("INFO", "We attempted to look up sessid %s in cache SUCCESS" %
                  sessid)
            return userd
        else:
            dolog("INFO", "We attempted to look up sessid %s in cache FAILED" %
                  sessid)
            return None
    except Exception, e:
        dolog("INFO", "We attempted to look up sessid %s in cache FAILED with Err %s" %
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
    ### Fixme - the whole app global thing is annoying me now.
    user_server_url = app.config['globals'][
        u'userserver'].replace("/user", "/openid")

    dolog("INFO", "user info - from url %s and query string %s" %
                  (user_server_url, repr(payload)))

    try:
        r = requests.get(user_server_url, params=payload)
        userdetails = r.json()
    except Exception, e:
        #.. todo:: not sure what to do here ... the user dbase is down
        dolog("INFO", e)
        userdetails = None

    dolog("INFO", "Got back %s " % str(userdetails))
    if userdetails and r.status_code == 200:
        return userdetails
    else:
        raise Rhaptos2Error("Not a known user")


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
        resp.set_cookie('cnxprofile', userdata['fullname'],
                        httponly=True,
                        expires=-0)
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
    if not app.debug:
        raise Rhaptos2Error("autosession should fail in prod.")

    # check if session already live for this user?
    # Hmm I have not written such code yet - seems a problem
    # only likely to occur here...

    # FIXME get the real userdict template
    standarduser = {'fullname': 'Paul Brian', 'user_id': 'cnxuser:1234'}
    sessionid = create_session(standarduser)
    store_userdata_in_request(standarduser, sessionid)
    ### fake in three users of id 0001 002 etc
    sessioncache._fakesessionusers(sessiontype='fixed')
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
    create_session(tempuserdict)
    return tempuserdict


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


def after_authentication(authenticated_identifier, method):
    """Called after a user has provided a validated ID (openid or peresons)

    This would be an ``endpoint`` in Valruse.

    method either openid, or persona

    :parms: authenticated_identifier

    pass on responsibility to



    """
    if method not in ('openid', 'persona', 'temporary'):
        raise Rhaptos2Error("Incorrect method of authenticating ID")

    dolog("INFO", "in after auth - %s %s" % (authenticated_identifier, method))
    userdetails = authenticated_identifier_to_registered_user_details(
        authenticated_identifier)
    create_session(userdetails)
    return userdetails


def whoami():
    '''

    based on session cookie
    returns userd dict of user details, equivalent to mediatype from service / session

    '''
    return g.userd


def apply_cors(resp):
    '''  '''
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


def add_location_header_to_response(fn):
    '''add Location: header

        from: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        For 201 (Created) responses, the Location is that of the new
        resource which was created by the request


    decorator that assumes we are getting a flask response object

    '''

    resp = fn()
    resp.headers["Location"] = "URL NEEDED FROM HASHID"


#@property ## need to evolve a class here I feel...
def userspace():
    ''' '''
    userspace = app.config['repodir']

    if os.path.isdir(userspace):
        return userspace
    else:
        try:
            os.makedirs(userspace)
            return userspace
        except Exception, e:
            raise Rhaptos2Error('cannot create repo \
                                or userspace %s - %s' % (
                                userspace, e))


def callstatsd(dottedcounter):
    ''' '''
    # Try to call logging. If not connected to a network this throws
    # "socket.gaierror: [Errno 8] nodename nor servname provided, or not known"
    try:
        c = statsd.StatsClient(app.config['globals']['statsd_host'],
                               int(app.config['globals']['statsd_port']))
        c.incr(dottedcounter)
        # todo: really return c and keep elsewhere for efficieny I suspect
    except:
        pass

# zombie code


def asjson(pyobj):
    '''just placeholder


    >>> x = {'a':1}
    >>> asjson(x)
    '{"a": 1}'

    '''
    return json.dumps(pyobj)


def gettime():
    return datetime.datetime.today().isoformat()


################ openid views - from flask


def temp_openid_image_url():
    """Provides a (temporary) fix for the openid images used
    on the login page.
    """
    # Gets around http://openid-selector.googlecode.com quickly
    resp = flask.redirect('/static/img/openid-providers-en.png')
    return resp


def login():
    """Does the login via OpenID.  Has to call into `auth.oid.try_login`
    to start the OpenID .
    """
    # if we are already logged in, go back to were we came from
    if g.userd is not None:
        dolog("INFO", "Were at /login with g.user_uri of %s" % g.user_uri)
        return redirect(auth.oid.get_next_url())

    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return auth.oid.try_login(openid, ask_for=['email', 'fullname',
                                                       'nickname'])

    return render_template('login.html', next=auth.oid.get_next_url(),
                           error=auth.oid.fetch_error(),
                           confd=app.config)


def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.

    """
    dolog("INFO", "OpenID worked, now set server to believe this is logged in")
    auth.after_authentication(resp.identity_url, 'openid')
    return redirect(auth.oid.get_next_url())


def logout():
    """
    kill the session in cache, remove the cookie from client

    """

    auth.delete_session(g.sessionid)
    return redirect(auth.oid.get_next_url())

##############


def logoutpersona():
    dolog("INFO", "logoutpersona")
    return "Yes"


def loginpersona():
    """Taken mostly from mozilla quickstart """
    dolog("INFO", "loginpersona")
    # The request has to have an assertion for us to verify
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    audience = "http://%s" % app.config['www_server_name']
    data = {'assertion': request.form['assertion'], 'audience': audience}
    resp = requests.post(
        'https://verifier.login.persona.org/verify', data=data, verify=True)

    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)
        dolog("INFO", "Verified persona:%s" % repr(verification_data))

        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
#            session.update({'email': verification_data['email']})
            after_authentication(verification_data['email'], 'persona')
            return resp.content

    # Oops, something failed. Abort.
    abort(500)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
