#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


import requests
import webob
import json
import os
from urlparse import urlparse

"""
restrest
--------

ReStREST is a simple attempt to grab the HTTP conversation between
a client and a server and output it in nice ReSt format for easy
documentation of RESTful interfaces

useage:

    simply execute the script, it should print to stderr the conversation
    with google.

JSON - we assume pretty much anything we care about is sent as json.
XML - TBD

This is still very simple.

"""



def sanestr(s, cutoff=40):
    """When printing headers and content
       replace reams of text with ellipsis and otherwise neaten stuff up"""

    if len(s) > cutoff:
        return s[:cutoff] + "..."
    else:
        return s


def format_req_body(txt):
    """ """
    if txt == None or len(txt)==0:
        return ""
    else:
        #assume its a json dict
        s = "\n\nBody::\n\n"
        try:
            pydatatype = json.loads(txt)
            jsonstr = json.dumps(pydatatype,
                                 sort_keys=True,
                                 indent=4)
            return s + indenttxt(jsonstr)
        except:
            return s + indenttxt(txt)

def format_req(req):
    """Neatly format the request """
    s = ""
    path = urlparse(req.url).path
    title = "%s %s" % (req.method, path)
    title += "\n" + "-"*len(title) + "\n\n"

    hdrs = ""
    for key in req.headers:
        hdrs += "    %s: %s\n" % (key, sanestr(req.headers[key]))
    s += title + "::\n\n" + hdrs

    body = format_req_body(req.body)

    return s + body

def indenttxt(txt, indent=4):
    indentedtxt = ''
    if not txt: return indentedtxt

    for line in txt.split("\n"):
        indentedtxt += " "*indent + sanestr(line, 79) + "\n"
    return indentedtxt

def format_content(resp):
    """ """
    try:
        d = resp.json()
        txt = json.dumps(d, sort_keys=True, indent=4)
    except:
        #ok not json. Likely mass of html, so ellipiss
        txt = resp.text[:40] + "..."
    return indenttxt(txt)


def format_resp(resp):
    """ """
    s = "\n\nResponse:: \n\n"
    hdrs = ""
    for key in resp.headers:
        hdrs += "    %s: %s\n" % (key, sanestr(resp.headers[key]))
    content = format_content(resp)
    s += hdrs + "\n\n::\n\n" + content

    return s

def restrest(resp):
    """Simple tool to document a HTTP "conversation" using the
       requests library

    useage: resp = requests.get("http://www.google.com")
            restrest(resp)
       """

    
    req_str = format_req(resp.request)
    resp_str = format_resp(resp)
    return req_str + resp_str + "\n\n"


if __name__ == '__main__':

    resp = requests.get("http://www.google.com", data={"foo":"bar"})
    print restrest(resp)

