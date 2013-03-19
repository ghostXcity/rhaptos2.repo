#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


import md5
import uuid


txt = """
    <html>                                                                                 
    <body>                                                                                 
    I went to the Beach, and made a sandcastle.                                            
    <a href="chapter2.html">next</a>                                                       
    </body>                                                                                
    </html>
"""

def md5txt():
    m = md5.new()
    m.update(txt.strip())
    return m.hexdigest()

if __name__ == '__main__':
    print md5txt()
    print uuid.uuid4()

