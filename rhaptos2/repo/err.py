##!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)


from werkzeug.exceptions import HTTPException


class Rhaptos2Error(Exception):
    pass


class Rhaptos2SecurityError(Exception):
    pass


class Rhaptos2SessionLookupFailedError(Exception):
    pass


class Rhaptos2NoSessionCookieError(Exception):
    pass


### To Be used for generioc raising of errors - expect to replace
### most calls with more specific error


class Rhaptos2HTTPStatusError(HTTPException):
    pass


class Rhaptos2AccessNotAllowedError(HTTPException):
    code = 403
    description = "Attempt to access a component you do not have access to"
