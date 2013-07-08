#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###

raise ImportError("These tests out of date - 20 mar 2013")

import doctest

doctest.testfile("example.txt",
                 optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS)

# doctest.testfile("coltest.txt",
#                 optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS)
#
# doctest.testfile("modtest.txt",
# optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS)
