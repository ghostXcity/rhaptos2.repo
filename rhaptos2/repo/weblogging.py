# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""\
Contains an endpoint for ``atc`` to log its information server-side.
This is used to build metrics about interface usage and problems.

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

import statsd

from . import get_app


logger = logging.getLogger(__name__)
# BBB (20-12-2013) 
lgr = logger
##logging.basicConfig()


STATS_LOGGER_NAME = 'stats'
CONFIG_KEY__STATSD_HOST = 'statsd.host'
CONFIG_KEY__STATSD_PORT = 'statsd.port'
CONFIG_KEY__STATSD_PREFIX = 'statsd.prefix'


class _StatsLoggingClient(statsd.StatsClient):
    """This provides the same interface as statsd.StatsClient to make
    a logging compatible version of the statistics capturing methods.
    """

    def __init__(self, host=None, port=None, prefix=None, maxudpsize=512):
        """Keep the same parameters for easy instantiation."""
        self._addr = (host, port,)
        self._logger = logging.getLogger(STATS_LOGGER_NAME)
        self._prefix = prefix
        self._maxudpsize = maxudpsize

    def _send(self, data):
        """Send data to statsd."""
        self._logger.info(data.encode('ascii'))


# Decide statistician (or statist) method of operation.
statist = None
def make_statist():
    """Factory to create a statist object that will use statsd when
    configured or default to logging.
    """
    # Cached return value.
    global statist
    if statist is not None:
        return statist

    config = get_app().config
    host = config.get(CONFIG_KEY__STATSD_HOST, None)
    port = config.get(CONFIG_KEY__STATSD_PORT, 8125)
    prefix = config.get(CONFIG_KEY__STATSD_PREFIX, None)
    # Is statsd configured?
    if host is not None:
        # Use statsd client.
        klass = statsd.StatsClient
    else:
        # Use statsd logging clone.
        klass = _StatsLoggingClient
    statist = klass(host, port, prefix)
    return statist
# XXX statist assign needs to be done on application intialized event
#     or upon first use. Otherwise we *may* run into an import before
#     configuration issue in the future.
statist = make_statist()



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
    payload, is_valid = validate_msg_return_dict(json_formatted_payload)
    try:
        type_ = payload['message-type']
    except KeyError:
        # ??? Shouldn't this exception be handed in
        #     the validation function above? The message-type is required, no?
        is_valid = False
    else:
        if type_ == 'log':
            logger.info(payload['log-message'])
        elif type_ == 'metric':
            send_metric(payload)
        else:
            lgr.error("message-type supplied was {} - not supported." \
                      .format(type_))
            is_valid = False

    return is_valid

def send_metric(payload):
    metric_type = payload['metric-type']
    if metric_type == 'incr':
        statist.incr(msg_dict['metric-label'])
    else:
        lgr.error("not support metric-type: {}".format(metric_type))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
