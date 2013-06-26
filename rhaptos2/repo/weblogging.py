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

and

  /metrics

The `logging` endpoint will take a message string and apply it to
the local syslog, which we expect will be configured to centralise
over rsyslogd.

The `metrics` endpoint will take a triple, of the below form and
convert it into a `stasd` call to be stored on the graphite database.

logging
-------

If it receives a POST of the correct form, it will pass that post onto
syslog on the local machine.

Form::

    {'log-message':'<txt>',
     'log-message-version': '0.0.1'}

There is no log level, or error code - it did not seem necessary in initial
discussions.  Again can revisit


Metrics
-------


Form::

    {'metric-label':'org.cnx.login.successful',
     'metric-type': 'incr',
     'metric-schema-version': '0.0.1'}

We currently only support label/incr on the metric side - this is for
simplicity, as writing timing tests got complex and I see little use
for them at the moment. We can revisit.


Improvements
------------
Run this as a WSGI middleware, so it is simple to import into
the chain.


Security considerations
-----------------------

Fundamentally no different from any web service.
I expect we shall need to use some form of long running token and
keep the conversastions in SSL to prevent simplistic DDOS attacks.

"""



import logging
import logging.handlers
import json



### Use module level global
lgr = None
stats_client_connected = None


## called by application startup
def configure_weblogging(confd):
    """
    """
    global lgr
    
    lgr = logging.getLogger(__name__)
    lgr.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    lgr.addHandler(handler)

## called by application startup
def validate_msg_return_dict(json_formatted_payload):
    """
    >>> configure_weblogging({})
    >>> payload_good = '''{"metric-label":"org.cnx.login.successful",
    ... "metric-type": "incr",
    ... "metric-value": null,
    ... "metric-schema-version": "0.0.1"}'''
    >>> x = validate_msg_return_dict(payload_good)
    >>> x
    ({u'metric-type': u'incr', u'metric-value': None, u'metric-label': u'org.cnx.login.successful', u'metric-schema-version': u'0.0.1'}, True)

    """
    try:
        metricpayload = json.loads(json_formatted_payload)
    except:
        lgr.error("Failed parse json")
        return('fff', False)
    ### better validation needed - json-schema
    if 'metric-label' not in metricpayload.keys():
        return (metricpayload, False)
    else:
        return (metricpayload, True)
        
def configure_statsd(confd):
    """
    """
    import statsd
    global stats_client_connected
    stats_client_connected = statsd.StatsClient(confd['globals']['statsd_host'],
                           confd['globals']['statsd_port'])
    
        
    
    

def log_endpoint(json_formatted_payload, context={}):
    """
    """
    msg_dict = json.loads(json_formatted_payload)
    if 'log-message' in msg_dict.keys():
        lgr.warn(msg_dict['log-message'])
    else:
        lgr.error("/logging recvd incorrect log payload %s" % json_formatted_payload)
    

def metric_endpoint(json_formatted_payload, context={}):
    """
    """
    msg_dict, is_valid = validate_msg_return_dict(json_formatted_payload)
    if not is_valid:
        lgr.error("/logging recvd incorrect log payload %s"
                   % json_formatted_payload)        
    else:
        if msg_dict['metric-type'] == 'incr':
            stats_client_connected.incr(msg_dict['metric-label'])
        else:
            lgr.error("/metric not support metric-type of %s" % msg_dict['metric-type'])
    
                  
    

if __name__ == '__main__':
    import doctest
    doctest.testmod()