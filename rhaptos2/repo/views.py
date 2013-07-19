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
views.py - View code for the repository application.

Structure:
We have three main view-areas.

 1. the models (Folder, Collection, Module)
 2. the helper views (workspace)
 3. binary uploads.
 4. openid and persona

Protocols
~~~~~~~~~
I try to stick to these

1. Every action (GET POST PUT DELETE) must have a useruri passed in to authorise
2. views recevie back *either* a model.<> object or a json-encodeable version of that


json-encoding
~~~~~~~~~~~~~

todo: convert to factory based app entirely
todo: remove view / as thats now JS
todo: remove apply_cors and apply internally. Or just use it?
todo: remove crash and burn


"""
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)
lgr.error("Initialised self logger for views.py")

import os
import json
from functools import wraps
import uuid
import requests
import flask
from flask import (
    render_template,
    request, g, session, flash,
    redirect, abort,
    send_from_directory
)

from rhaptos2.repo import (get_app,
                           auth, VERSION, model,
                           backend, weblogging)
from rhaptos2.repo.err import (Rhaptos2Error,
                               Rhaptos2SecurityError,
                               Rhaptos2HTTPStatusError)
import werkzeug.exceptions


#### common mapping
MODELS_BY_MEDIATYPE = {
    "application/vnd.org.cnx.collection": model.Collection,
    "application/vnd.org.cnx.module": model.Module,
    "application/vnd.org.cnx.folder": model.Folder
}

def model_from_mediaType(mediaType):
    """
    a simple dict lookup, but future proofing
    the possiblity of adding application/vnd.org.cnx.module+json
    """
    try:
        mdl =  MODELS_BY_MEDIATYPE[mediaType]
    except KeyError:
        raise werkzeug.exceptions.UnsupportedMediaType("Unrecognised mediaType: %s" % mediaType)
    return mdl
    


def requestid():
    """
    before_request is supplied with this to run before each __call_

    """
    g.requestid = uuid.uuid4()
    g.request_id = g.requestid
    g.deferred_callbacks = []

    ### Before the app.__call__ is called, perform processing of user auth
    ### status.  If this throws err, we redirect or similar, else __call__ app
    ### proceeds
    resp = auth.handle_user_authentication(request)
    if resp is not None:
        if hasattr(resp, "__call__") is True:
            return resp
    else:
        pass
    ## All good - carry on.


def call_after_request_callbacks(response):
    for callback in getattr(g, 'deferred_callbacks', ()):
        response = callback(response)
    return response


########################### views


def apply_cors(resp_as_pytype):
    '''A callable function (not decorator) to
       take the output of a app_end and convert it to a Flask response
       with appropriate Json-ified wrappings.

    '''
    resp = flask.make_response(resp_as_pytype)
    resp.content_type = 'application/json; charset=utf-8'
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


def logging_endpoint():
    """
    this is /logging - it will take a POST of json doc and pass it
    to the weblogging module, which will take care of details.
    """
    payld_as_json = obtain_payload(request)
    lgr.info(" %s %s" % (type(payld_as_json), payld_as_json))
    # FIXME - use python natie formats throughout
    result = weblogging.logging_router(json.dumps(payld_as_json))
    lgr.info("result was %s" % result)
    if result == True:
        return "logged"
    else:
        abort(400)


def home():
    """
    This is the "home" page for a visitor,

    At this point there is either a valid session (so redirect to atc)
    or there is a need to let the visitor choose either to get an
    anonymous session, or that they are registered, and they should
    choose to log in again.

    There is a logic choice that might improve things - if they have
    previously visited us, redirect to /login.
    """

    try:
        userdata, sessionid = auth.session_to_user(
            request.cookies, request.environ)
        resp = flask.redirect('/js/')
        return resp
    except Exception, e:
        return """<p>~~~ Bootstrap hotness here ~~~~</p>
        You are not logged in.
        <p>Try the site <a href="/tempsession">anonymously</a></p>
        <p>Or <a href="/login">sign in</a></p>
        <p>Please note all work will be lost at the end of anonymous sessions.</p>"""


def whoamiGET():
    '''
    returns
    Either 401 if OpenID not available or JSON document of form

    {"openid_url": "https://www.google.com/accounts/o8/id?id=AItOawlWRa8JTK7NyaAvAC4KrGaZik80gsKfe2U",  # noqa
     "email": "Not Implemented",
     "name": "Not Implemented"}


    '''
    ### todo: return 401 code and let ajax client put up login.
    userd = auth.whoami()  # same as g.user_details

    if userd:
        jsond = json.dumps(userd)
        resp = apply_cors(jsond)
        return resp
    else:
        return("Not logged in", 401)  # FIXME - zombie code again


def workspaceGET():
    ''' '''
    # TODO - should whoami redirect to a login page?
    ### yes the client should only expect to handle HTTP CODES
    ### compare on userID

    userd = auth.whoami()
    if not userd:
        abort(403)
    else:
        wout = {}
        lgr.info("Calling workspace with %s" % userd['user_id'])
        w = model.workspace_by_user(userd['user_id'])
        lgr.info(repr(w))
        ## w is a list of models (folders, cols etc).
        # it would require some flattening or a JSONEncoder but we just want
        # short form for now
        short_format_list = [{
            "id": i.id_, "title": i.title, "mediaType": i.mediaType} for i in w]
        flatten = json.dumps(short_format_list)
    resp = apply_cors(flatten)
    return resp


def keywords():
    """Returns a list of keywords for the authenticated user."""
    # XXX We really need a database search here. With the current
    #     state of the storage (file system), we would need to open
    #     every module's keywords in order to compile a comprehensive
    #     list of available keywords created by the user.
    #     We should come back to this after we have created a storage
    #     that can be queried (e.g. a SQL database).
    XXX_JUNK_KEYWORDS = ("Quantum Physics", "Information Technology",
                         "Biology", "Anthropology", "Philosophy", "Psychology",
                         "Physics", "Socialogy", "Plumbing", "Engine Repair",
                         "Programming", "Window Washing", "Cooking", "Hunting",
                         "Fishing", "Surfing",
                         )
    resp = flask.make_response(json.dumps(XXX_JUNK_KEYWORDS))
    resp.status_code = 200
    resp.content_type = 'application/json; charset=utf-8'
    return resp


def versionGET():
    ''' '''
    s = VERSION
    resp = flask.make_response(s)
    resp.content_type = 'application/json; charset=utf-8'
    resp.headers["Access-Control-Allow-Origin"] = "*"

    return resp


def auto_session():
    """
    strictly for testing purposes
    I want to fake three sessions with known ids.
    Also generate a "real" session with a known user
    FIXME - there has to be a better way
    """

    sessionid = auth.set_autosession()

    return "Session created - please see headers"


def temp_session():
    """
    When a user wants to edit anonymously, they need to hit this
    first.  This is to avoid the logic problems in knowing
    if a user should be redirected if they have one but not two cookies etc.

    Here we generate a temperoiary userid (that is *not* linked to cnx-user)
    then setup a session based on that userid.  All work will be lost
    at end of session.

    """
    sessionid = auth.set_temp_session()
    resp = flask.redirect("/")
    return resp


def obtain_payload(werkzeug_request_obj):
    """
    .. todo::
       expand this function to encompass various checks on incoming
       payload of POST / PUT requests incl unicode,

    """
    try:
        jsond = werkzeug_request_obj.json
    except:
        jsond = None
    return jsond


def verify_schema(model_dict, mediatype):
    """
    Given a json object, verify it matches the claimed mediaType schema

    model_dict: dict of the model as out of json - MUST be pure mediaType, not SOFT form
    mediatype: WHat we think the dict confirms to


    FixMe: we do not have versioning of schemas
    FixMe: we don't have a jsonschema verifier...

    """
    if mediatype not in MODELS_BY_MEDIATYPE:
        raise werkzeug.exceptions.UnsupportedMediaType(
            "mediatype supplied is not valid - %s" % mediatype)
    ### a valid schema is fairly limited ...
    if 'title' in model_dict.keys():
        return True
    else:
        return False


def mediaType_from_payload(payload):
    """
    Given a (json) formatted payload,
    find out if it is a `module`. `collection`, `folder`
    and return appropriate mediatype

    possible enhancements include using a acceptHeader to determine mediatype
    returns mediatype - seems odd..
    """
    # payload should be a dict
    
    if "mediaType" in payload.keys():
        mediaType = payload['mediaType']
    else:
        # bad
        raise werkzeug.exceptions.BadRequest(
            "missing mediaType key in model json")
    ### Now verify
    if not verify_schema(payload, mediaType):
        raise werkzeug.exceptions.BadRequest("schema failed verififcation")
    else:
        return mediaType

############################################################
## "Routers". genericly handle very similar actions
## but without 'reimplmenting' Flask disaptching
############################################################


def content_router(uid):
    """
    We now serve everything form api/content

    uid = content/1234-1234-12334
                  ^^^ uuid

    router logic is subtly different

    1. if we are GET, DELETE, HEAD then no payload and an uid
       do not collect payload, do collect uid
       route
    2. POST
       payload no uid
    3. PUT
       payload and uid
    (Ignore OPTIONS etc)

    
    
    """

    
    requesting_user_id = g.user_details['user_id']
    payload = obtain_payload(request) # will be empty sometimes
    lgr.info("In content router, %s payload is %s " % (request.method, str(payload)[:10]))

    ###
    if request.method == "GET":
        return generic_get(uid, requesting_user_id)

    elif request.method == "POST":
        if payload is None:
            raise Rhaptos2HTTPStatusError(
                "Received a Null payload, expecting JSON")
        else:
            mediaType = mediaType_from_payload(payload)
            mdlklass = model_from_mediaType(mediaType)  
            return generic_post(mdlklass,
                                payload, requesting_user_id)

    elif request.method == "PUT":
        if payload is None:
            raise Rhaptos2HTTPStatusError(
                "Received a Null payload, expecting JSON",
                code=400)
        else:
            mediaType = mediaType_from_payload(payload)
            mdlklass = model_from_mediaType(mediaType)  
            return generic_put(mdlklass, uid,
                               payload, requesting_user_id)

    elif request.method == "DELETE":
        return generic_delete(uid, requesting_user_id)

    else:
        return werkzeug.exceptions.MethodNotAllowed("Methods:GET PUT POST DELETE.")



##########################################################
## specific views called by "routers" above.
##########################################################
def folder_get(folderuri, requesting_user_id):
    """
    return folder as an appropriate json based response string

    This is returned not as the generic representation of a folder, but as
    a "soft" form, with names of folder children as well as "hard" uuids.
    This is why the folder_get is special cased here.

    .__complex__ -> creates a version of an object that can be run through a std json.dump

    Why am I passing in the same userid in two successive objects

    1. I am not maintaining any state in the object, not assuming any state in thread(*)
    2. The first call returns the "hard" object (pointers only)
       Thus it (rightly) has no knowledge of the user permissions of its children.
       We will need to descend the hierarchy to

    (*) This may get complicated with thread-locals in Flask and scoped sessions. please see notes
        on backend.py
    """
    fldr = model.obj_from_urn(folderuri, g.user_details['user_id'])
    fldr_complex = fldr.__complex__(g.user_details['user_id'])

    resp = flask.make_response(json.dumps(fldr_complex))
    resp.content_type = 'application/json; charset=utf-8'
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


def generic_get(uri, requesting_user_id):

    mod = model.obj_from_urn(uri, requesting_user_id)
    resp = flask.make_response(json.dumps(
                               mod.__complex__(requesting_user_id)))
    resp.status_code = 200
    resp.content_type = 'application/json; charset=utf-8'
    return resp


def generic_post(klass, payload_as_dict, requesting_user_id):
    """Post an appropriately formatted dict to klass

    .. todo::
       its very inefficient posting the folder, then asking for
       it to be recreated.

    """
    owner = requesting_user_id
    fldr = model.post_o(klass, payload_as_dict,
                        requesting_user_id=owner)
    resp = flask.make_response(json.dumps(fldr.__complex__(owner)))
    resp.status_code = 200
    resp.content_type = 'application/json; charset=utf-8'
    return resp


def generic_put(klass, resource_uri, payload_as_dict,
                requesting_user_id):

    owner = requesting_user_id
    fldr = model.put_o(payload_as_dict, klass, resource_uri,
                       requesting_user_id=owner)
    resp = flask.make_response(json.dumps(fldr.__complex__(owner)))
    resp.status_code = 200
    resp.content_type = 'application/json; charset=utf-8'
    return resp


def generic_delete(uri, requesting_user_id):
    """ """
    owner = requesting_user_id
    model.delete_o(uri, requesting_user_id=owner)
    resp = flask.make_response("%s is no more" % uri)
    resp.status_code = 200
    resp.content_type = 'application/json; charset=utf-8'
    return resp
