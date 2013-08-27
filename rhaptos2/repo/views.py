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
import json
import logging
from functools import wraps
import string
import uuid

import flask
from flask import (
    render_template,
    request, g, session, flash,
    redirect, abort,
    send_from_directory
)
import psycopg2
import requests
import werkzeug.exceptions

from . import get_app, get_settings, auth, VERSION
from .database import CONNECTION_SETTINGS_KEY, SQL
from .err import (Rhaptos2Error,
                  Rhaptos2SecurityError,
                  Rhaptos2HTTPStatusError)


#### common mapping
MODELS_BY_MEDIATYPE = [
    "application/vnd.org.cnx.collection",
    "application/vnd.org.cnx.module",
    "application/vnd.org.cnx.folder"
]

lgr = logging.getLogger(__name__)


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


_cached_index_html = None
def index():
    """Serves up the index.html file. This will be removed."""
    # BBB (05-12-2013) We shouldn't be serving the index file from here,
    #     but at the moment this is the only way around the issue of serving
    #     it from somewhere.
    global _cached_index_html
    if _cached_index_html is None:
        app = get_app()
        index_html_filepath = app.config['index_html']
        with open(index_html_filepath, 'r') as buffer:
            _cached_index_html = buffer.read()
    resp = flask.make_response(_cached_index_html)
    resp.status_code = 200
    resp.content_type = 'text/html; charset=utf-8'
    return resp


def bootstrap():
    """
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
        resp = flask.redirect('/')
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
        lgr.info("Calling workspace with %s" % userd['user_id'])
        settings = get_settings()

        # Do the workspace lookup
        user_id = userd['user_id']
        with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
            with db_connection.cursor() as cursor:
                args = dict(user_id=user_id)
                cursor.execute(SQL['get-workspace'], args)
                result = cursor.fetchall()
                # FIXME: There is probably a cleaner way to unwrap the results when the are empty
                result = [item[0] for item in result]

        resp = flask.make_response(json.dumps(result))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers['Content-type'] = 'application/json; charset=utf-8'
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


def simple_xss_validation(html_fragment):
    """

    >>> simple_xss_validation("US-12345678-1")
    True
    >>> simple_xss_validation("<script>Evil</script>")
    False

    This is very quick and dirty, and we need some consideration
    over XSS escaping. FIXME
    """

    if not html_fragment:
        return True
    whitelist = string.ascii_letters + string.digits + "-" + string.whitespace
    lgr.info("Start XSS whitelist - %s" % html_fragment)
    for char in html_fragment:
        if char not in whitelist:
            lgr.error("Failed XSS whitelist - %s" % html_fragment)
            return False
    return True



def validate_mediaType(payload):
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


def validate_googleTrackingID(payload):
    """
    Given a (json) formatted payload,
    return whether the google tracking ID is valid
    """
    # payload should be a dict
    if payload.get('googleTrackingID'):
        if not simple_xss_validation(payload['googleTrackingID']):
            raise werkzeug.exceptions.BadRequest(
                    'googleTrackingID cannot have script-like characters in it')


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

    VALID_UPDATE_FIELDS = [
        'mediaType', # TODO: This is not needed for UPDATE but the validator needs it
        'title',
        'authors',
        'copyrightHolders',
        'body',
        'language',
        'subjects',
        'keywords',
        'summary',
        'googleTrackingID',
    ]


    requesting_user_id = g.user_details['user_id']
    payload = obtain_payload(request) # will be empty sometimes
    lgr.debug("In content router, %s payload is %s " % (request.method, str(payload)))

    settings = get_settings()

    ###

    if request.method == "GET":
        # The GET is handled at the end of this if block
        pass

    elif request.method == "POST":
        if payload is None:
            raise Rhaptos2HTTPStatusError(
                "Received a Null payload, expecting JSON")
        else:

            uid = str(uuid.uuid4())

            # Generate the SQL needed to INSERT
            fields = {'id': uid}
            sql_field_names = []
            sql_field_values = []
            for field_name in VALID_UPDATE_FIELDS:
                if field_name in payload:
                    fields[field_name] = payload[field_name]
                    # FIXME: Please tell me how to dynamically UPDATE fields
                    sql_field_names.append('"%s"' % field_name)
                    sql_field_values.append('%%(%s)s' % field_name)

            dynamic_insert = 'INSERT INTO cnxmodule (id_, %s) VALUES (%%(id)s, %s)' % (', '.join(sql_field_names), ', '.join(sql_field_values))

            # Perform validation before inserting
            validate_mediaType(fields)
            validate_googleTrackingID(fields)

            with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
                with db_connection.cursor() as cursor:
                    cursor.execute(dynamic_insert, fields)

                    roles = {
                        'content_id': uid,
                        'user_id': requesting_user_id
                    }
                    cursor.execute("INSERT INTO cnxacl (module_id, user_id, role_type) "
                                   "VALUES (%(content_id)s, %(user_id)s, 'aclrw')", roles)

    elif request.method == "PUT":
        # Generate the SQL needed to UPDATE
        fields = {'id': uid}
        sql_fields = []
        for field_name in VALID_UPDATE_FIELDS:
            if field_name in payload:
                fields[field_name] = payload[field_name]
                # FIXME: Please tell me how to dynamically UPDATE fields
                sql_fields.append('"%s" = %%(%s)s' % (field_name, field_name))
        sql_fields.append('"dateLastModifiedUTC" = NOW() AT TIME ZONE \'UTC\'')

        dynamic_update = 'UPDATE cnxmodule SET %s WHERE id_ = %%(id)s' % (' , '.join(sql_fields))

        # Perform validation before updating
        validate_mediaType(fields)
        validate_googleTrackingID(fields)

        with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
            with db_connection.cursor() as cursor:
                # Check if allowed to PUT
                sql = '''SELECT COUNT(*) FROM cnxacl
                         WHERE role_type = 'aclrw'
                         AND module_id = %(id)s AND user_id = %(user_id)s'''
                cursor.execute(sql, {'id': fields['id'], 'user_id': requesting_user_id})
                if cursor.fetchone()[0] != 1:
                    return werkzeug.exceptions.Forbidden(
                            "User {} not permitted to adjust resource {}".format(
                                uid, requesting_user_id))

                cursor.execute(dynamic_update, fields)

                for acl in payload.get('acl', []):
                    sql = '''INSERT INTO cnxacl (module_id, user_id, role_type)
                             VALUES (%(id)s, %(acl)s, 'aclrw')'''
                    cursor.execute(sql, {'id': fields['id'], 'acl': acl})

    else:
        return werkzeug.exceptions.MethodNotAllowed("Methods:GET PUT POST.")


    # Always Return the full Content JSON after POST or PUT
    with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
        with db_connection.cursor() as cursor:
            args = dict(id=uid)
            cursor.execute(SQL['get-content'], args)
            result = cursor.fetchone()[0]

            sql2 = """SELECT user_id
            FROM cnxacl 
            WHERE module_id = %(id)s;
            """
            cursor.execute(sql2, args)
            result['acl'] = [row[0] for row in cursor.fetchall()]
            lgr.debug('result is: {}'.format(result))

    if requesting_user_id not in result['acl']:
        abort(403)


    # status = "200 OK"
    # headers = [('Content-type', 'application/json',)]

    resp = flask.make_response(json.dumps(result))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers['Content-type'] = 'application/json; charset=utf-8'
    return resp



def folder_router(folderuri):
    """
    """
    lgr.info("In folder router, %s" % request.method)
    requesting_user_id = g.user_details['user_id']
    payload = obtain_payload(request)
    uid = folderuri

    VALID_UPDATE_FIELDS = [
        'mediaType',
        'title',
        'contents'
    ]

    requesting_user_id = g.user_details['user_id']
    payload = obtain_payload(request) # will be empty sometimes
    lgr.debug("In content router, %s payload is %s " % (request.method, str(payload)[:10]))

    settings = get_settings()

    ###
    if request.method == "GET":
        # The GET is handled at the end of this if block
        pass

    elif request.method == "POST":
        if payload is None:
            raise Rhaptos2HTTPStatusError(
                "Received a Null payload, expecting JSON")
        else:

            uid = str(uuid.uuid4())

            # Generate the SQL needed to INSERT
            fields = {'id': uid}
            sql_field_names = []
            sql_field_values = []
            for field_name in VALID_UPDATE_FIELDS:
                if field_name in payload:
                    fields[field_name] = payload[field_name]
                    # FIXME: Please tell me how to dynamically UPDATE fields
                    sql_field_names.append('"%s"' % field_name)
                    sql_field_values.append('%%(%s)s' % field_name)

            dynamic_insert = 'INSERT INTO cnxfolder (id_, %s) VALUES (%%(id)s, %s)' % (', '.join(sql_field_names), ', '.join(sql_field_values))

            # Perform validation before inserting
            validate_mediaType(fields)

            with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
                with db_connection.cursor() as cursor:
                    cursor.execute(dynamic_insert, fields)

                    roles = {
                        'content_id': uid,
                        'user_id': requesting_user_id
                    }
                    cursor.execute("INSERT INTO userrole_folder (folder_uuid, user_id, role_type)"
                                   " VALUES (%(content_id)s, %(user_id)s, 'aclrw')", roles)

    elif request.method == "PUT":

        # Generate the SQL needed to UPDATE
        fields = {'id': uid}
        sql_fields = []
        for field_name in VALID_UPDATE_FIELDS:
            if field_name in payload:
                fields[field_name] = payload[field_name]
                # FIXME: Please tell me how to dynamically UPDATE fields
                sql_fields.append('"%s" = %%(%s)s' % (field_name, field_name))
        sql_fields.append('"dateLastModifiedUTC" = NOW() AT TIME ZONE \'UTC\'')

        dynamic_update = 'UPDATE cnxfolder SET %s WHERE id_ = %%(id)s' % (' , '.join(sql_fields))

        # Perform validation before updating
        validate_mediaType(fields)

        with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(dynamic_update, fields)

    else:
        return werkzeug.exceptions.MethodNotAllowed("Methods:GET PUT POST.")


    # Always Return the full Content JSON after POST or PUT
    with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
        with db_connection.cursor() as cursor:
            args = dict(id=uid)
            cursor.execute(SQL['get-folder'], args)
            result = cursor.fetchone()[0]

    # FIXME: Use some fancy INNER JOIN magic here @Ross?
    # Sprinkle in the mediaType and id for every piece of content
    with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
        with db_connection.cursor() as cursor:
            if len(result['contents']):
                args = {'contents': result['contents']}
                cursor.execute(SQL['get-folder-contents'], args)
                resultContents = cursor.fetchall()[0]
                result['contents'] = resultContents

    resp = flask.make_response(json.dumps(result))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers['Content-type'] = 'application/json; charset=utf-8'
    return resp
