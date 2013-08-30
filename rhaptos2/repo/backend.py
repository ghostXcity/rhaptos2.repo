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
Provide a abstracted SQL Alchemy backend to allow
models to connect to postegres.


"""

## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import psycopg2


### Module globals.  Following Pylons lead, having global
### scoped_session will ensure threads (and thread locals in Flask)
### all have theit own sessions
db_engine = None
db_session = scoped_session(sessionmaker(autoflush=True,
                                         autocommit=False))

Base = declarative_base()
from rhaptos2.repo import model ## Must import after Base decl. 


##############################################################
### As long as we subclass everything from Base, we are following
### declarative pattern recommended by sa docs.


def connect_now(confd):
    connstr = "postgresql+psycopg2://%(pgusername)s:%(pgpassword)s@%(pghost)s/%(pgdbname)s" % confd  # noqa
    engine = create_engine(connstr, echo=False)
    lgr.debug("Connected to postgres - returning engine")
    return engine


def initdb(confd):
    """This could become a conn factory.  """
    global db_session
    global Base
    
    db_engine = connect_now(confd)
    db_session.configure(bind=db_engine)
    Base.metadata.create_all(db_engine)
    lgr.debug("created tables")

    ### Now select * from all main tables to check
    try:
        from rhaptos2.repo.model import Folder, Collection, Module
        for klass in [Folder, Collection, Module]:
            q = db_session.query(klass)
            rs = q.all()
    except:
        lgr.error("The init db failed")
        raise