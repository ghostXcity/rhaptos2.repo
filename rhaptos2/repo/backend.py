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


### As long as we subclass everything from Base, we are following
### declarative pattern recommended by sa docs.

def connect_now(confd):
    connstr = "postgresql+psycopg2://%(pgusername)s:%(pgpassword)s@%(pghost)s/%(pgdbname)s" % confd  # noqa
    engine = create_engine(connstr, echo=False)
    return engine


def initdb(confd):
    """This could become a conn factory.  """
    global db_session
    db_engine = connect_now(confd)
    db_session.configure(bind=db_engine)
    Base.metadata.create_all(db_engine)


def clean_dbase(config):
    """clear down the database tables - used for testing purposes
    """
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config)
    c = conn.cursor()

    stmts = [
        "DELETE FROM public.userrole_module",
        "DELETE FROM public.cnxmodule",

        "DELETE FROM public.userrole_folder",
        "DELETE FROM public.cnxfolder",

        "DELETE FROM public.userrole_collection",
        "DELETE FROM public.cnxcollection",

    ]
    for stmt in stmts:
        c.execute(stmt)
        conn.commit()
    conn.close()


def status_dbase(config):
    """clear down the database tables - used for testing purposes
    """
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config)
    c = conn.cursor()
    tables = [
        "public.cnxmodule",
        "public.userrole_module",
        "public.cnxfolder",
        "public.userrole_folder",
        "public.cnxcollection",
        "public.userrole_collection",
    ]

    for tbl in tables:
        c.execute("SELECT COUNT(*) FROM %s" % tbl)
        print c.fetchall()
    conn.close()
