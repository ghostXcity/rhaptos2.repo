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
.. todo::
   Are we running in venv?
   Does that venv hold all needed requirements.


CARBON_SERVER = 'log.frozone.mikadosoftware.com'
CARBON_PORT = 2003
STATSD_PORT = 8125
STATSD_HOST = CARBON_SERVER

import statsd

def test_statsd():

    c = statsd.StatsClient(STATSD_HOST, STATSD_PORT)
    for i in range(1000):
        c.incr('rhaptos2.statsd.verify')

"""

import sys


# Simple python version test
major, minor = sys.version_info[:2]
py_version = sys.version.split()[0]
if major != 2 or minor < 7:
    print "You are using python %s, but \
version 2.7 or greater is required" % py_version
    raise SystemExit(1)
