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

    Or supply a request and response object to the main function :meth:`restrest`.  Please note that this was built initially to use ``Requests`` objects, then moved to ``WebOb.Requests``.  They main use case is webob so the formatting works sensibly there, the requests generally work fine.


JSON - we assume pretty much anything we care about is sent as json.

Output is returned to you from restrest, do with it what you will.

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

def restrest(req, resp, shortformat=True):
    """Simple tool to document a HTTP "conversation" using the
       requests library

    useage: resp = requests.get("http://www.google.com")
            restrest(resp)

    At the moment only supporting WebOb, requests was originally supported
    
    :params req: a request object of WebOb type
    :params resp: a response object of WebOb type    
    :params shortformat: Boolean.  If True output more readable
                         body and headers, replacing extra text with ellipsis
                         If false output everything as is.
       """

    ### Quick dirty solution 
    if not shortformat:
        req_str = str(req)
        resp_str = str(resp)
        req_str = "    "+ req_str.replace("\n", "\n    ")
        resp_str = "    "+ resp_str.replace("\n", "\n    ")        
    else:
        req_str = format_req(req)
        resp_str = format_resp(resp)

    return req_str + resp_str + "\n\n"


if __name__ == '__main__':

    resp = requests.get("http://www.google.com", data={"foo":"bar"})
    print restrest(resp.request, resp)

