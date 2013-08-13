#!/usr/bin/env python
#! -*- coding: utf-8 -*-

### Copyright Rice University 2013

# This program is licensed, without  under the terms of the
# GNU Affero Public License 3 (or later).  Please see
# LICENSE.txt for details

###

""":author:  paul@mikadosoftware.com <Paul Brian>


This is initially a simple URL to be listened to::

  /logging

The `logging` endpoint will take either of the two forms of message below apply
it either to the local syslog, which we expect will be configured to centralise
over rsyslogd, or it will take a triple, of the below form and
convert it into a `stasd` call to be stored on the graphite database.

logging
-------

This endpoint will capture a JSON encoded POST sent to `/logging`
and will process one of three message types.


Firstly, just a block of text expected to be a traceback or other
log-ready message.  We would assume the client would *not* insert user
data. There is no expectation of capturing session details here.
Why would we want the log to be SSL protected? Might be an idea?

    {'message-type':'log',
     'log-message':'Traceback ...',

     'metric-label': null,
     'metric-value': null,
     'metric-type': null;,
     }

The common metric of simply adding one to a global counter
is shown here.  We are capturing the number of times anyone
types in the word penguin.

    {'message-type':'metric',
     'log-message':null,

     'metric-label': 'org.cnx.writes.penguin',
     'metric-value': null,
     'metric-type': 'incr',
     }


Here, a third type of message. We can capture a metric that is a
specific value, this would be useful in aggregate reporting. It might be
amount of time to perform an action, here its wpm.::


    {'message-type':'metric',
     'log-message':null,

     'metric-label': 'org.cnx.wordsperminute',
     'metric-value': 48,
     'metric-type': 'timing';,
     }

NB The above message is not yet supported.

Improvements
------------
Run this as a WSGI middleware, so it is simple to import into
the chain.


Security considerations
-----------------------

Fundamentally no different from any web service.
I expect we shall need to use some form of long running token and
keep the conversastions in SSL to prevent simplistic DDOS attacks.


Simple testing

>>> from weblogging import *
>>> confd = {'globals':
... {'syslogaddress':"/dev/log",
... 'statsd_host':'log.frozone.mikadosoftware.com',
... 'statsd_port':8125,
... }}
>>> testmsg = '''{"message-type":"log",
...            "log-message":"This is log msg",
...            "metric-label": null,
...            "metric-value": null,
...            "metric-type": null
...           }'''
>>> configure_weblogging(confd)
>>> logging_router(testmsg)



### FIXME - there is no really decent way to snaffle syslogs in a unit test...


"""
import logging
import logging.handlers
import json

### Use module level global
stats_client_connected = None
lgr = logging.getLogger(__name__)
logging.basicConfig()


## called by application startup
def configure_weblogging(confd):
    """
    """
    configure_statsd(confd)


def configure_statsd(confd):
    """
    """
    import statsd
    global stats_client_connected
    stats_client_connected = statsd.StatsClient(
        confd['globals']['statsd_host'],
        confd['globals']['statsd_port'])


## called by application startup
def validate_msg_return_dict(json_formatted_payload):
    """
    >>>
    >>> payload_good = '''{"message-type":"log",
    ...            "log-message":"This is log msg",
    ...            "metric-label": null,
    ...            "metric-value": null,
    ...            "metric-type": null
    ...           }'''
    >>> x = validate_msg_return_dict(payload_good)
    >>> x
    ({u'metric-type': None, u'metric-value': None, u'metric-label': None, u'message-type': u'log', u'log-message': u'This is log msg'}, True)

    """
    valid_logmsg_flag = False
    
    try:
        payload = json.loads(json_formatted_payload)
    except Exception, e:
        lgr.error("Failed parse json - %s %s" % (e, json_formatted_payload))
        return({}, valid_logmsg_flag)

    ### various tests for valid payload   
    if 'trigger' in payload.keys():
        ### this is currently all atc sends, so just handle it
        payload['message-type'] = 'log'
        payload['log-message'] = payload['trigger']
        valid_logmsg_flag = True

    ### pbrian: better validation needed - try json-schema
    elif 'message-type' in payload.keys():
        valid_logmsg_flag = True
    else:
        lgr.error("This message has no valid data %s" % payload)
        valid_logmsg_flag = False

    return (payload, valid_logmsg_flag)
    

def logging_router(json_formatted_payload):
    """pass in a json message, this will check it, then action the message.

    We have several types of incoming message, corresponding to an
    atc log message, an atc metric message (ie graphite).
    We want to correctly handle each so this acts as a router/dispatcher
    """
    isValid = True
    # validate and convert to dict
    payload, isValid = validate_msg_return_dict(json_formatted_payload)
    try:
        if payload['message-type'] == 'log':
            log_endpoint(payload)
        elif payload['message-type'] == 'metric':
            metric_endpoint(payload)
        else:
            lgr.error("message-type supplied was %s - not supported." %
                      payload['message-type'])



        isValid = False
    except KeyError, e:
        isValid = False
    return isValid

def log_endpoint(payload):
    """
    given a dict, log it to syslog

    """
    msg_dict = payload
    try:
        lgr.info(msg_dict['log-message'])
        
    except Exception, e:
        lgr.error("/logging recvd incorrect log payload %s" % repr(payload))
    

def metric_endpoint(payload):
    """
    given a dict, fire off to statsd

    """
    try:
        if msg_dict['metric-type'] == 'incr':
            lgr.info("Firing statsd")
            stats_client_connected.incr(msg_dict['metric-label'])
        else:
            lgr.error("/metric not support metric-type of %s" %
                      msg_dict['metric-type'])
    except Exception, e:
        lgr.error("Failed to log incoming metric %s" % repr(payload))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
