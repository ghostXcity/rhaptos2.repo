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


The non-sqlalchemy version
--------------------------

We have moved from SqlAlchemy to a direct model.
The actions of PUT POST DELETE and GET will be modelled in SQL Stmts
and passed through the psycopg2 driver.  Because the mental overhead is lower.

I will stick with using Classes to represent Collections, Folders and Modules.
However I will try and move the majority of CNXBase classes into those classes directly.

There are two major sets of changes:

- simple API for each class to support PUT POST GET DELETE
- removing the double layer of calls


Connection Pooling
------------------

You must setup the pool after initial import.

"""

## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)

import psycopg2
from psycopg2.pool import ThreadedConnectionPool as tPool


############
DBPOOL = None

def setpool(confd):
    global DBPOOL
    DBPOOL = tPool(5,10,host=confd['pghost'],
                                database=confd['pgdbname'],
                                user=confd['pgusername'],
                                password=confd['pgpassword'])
    return DBPOOL.getconn()


def getconn():
    """returns a connection object based on global confd.

    This is, at the moment, not a pooled connection getter.

    We do not want the ThreadedPool here, as it is designed for
    "real" threads, and listens to their states, which will be 'awkward'
    in moving to greenlets.

    We want a pool that will relinquish
    control back using gevent calls

    https://bitbucket.org/denis/gevent/src/5f6169fc65c9/examples/psycopg2_pool.py
    http://initd.org/psycopg/docs/pool.html

    :return ``psycopg2 connection obj``: conn obj
    :return psycopg2.Error:              or Err

    """
    conn = DBPOOL.getconn()
    return conn

def close_conn(conn):
    """
    """
    conn.close()

def query_to_dict(SQL, params):
    """
    Given (valid!) SQL execute and return
    the results as a dict

    no attempt at iterating over the recordset,
    this is for middle length resultsets only.
    
    :params: dict
    :SQL: uses %(xx)s format

    SQL = '''SELECT * FROM cnxmodule where id_ = %(id)s '''
    params = {'id': '5678'}
    rs = backend.query_to_dict(SQL, params)

    """
    conn = getconn()
    cr = conn.cursor()
    cr.execute(SQL, params)
    rs = cr.fetchall()
    des = cr.description
    rsd = []
    for row in rs:
         rsd.append(dict(zip([col.name for col in des], row)))
    conn.commit()
    DBPOOL.putconn(conn)
    return rsd
    
    
def initdb(confd):
    """This could become a conn factory.  """
    conn = getconn(confd)
    cursor =  conn.cursor()
    cursor.execute(CREATE_ALL_TABLES)
    conn.commit()
    close_conn(conn)


CREATE_ALL_TABLES = """

-- complete and rather dumb initialisation

DROP TABLE IF EXISTS session_cache;

DROP TABLE IF EXISTS session_cache;

DROP TABLE IF EXISTS userrole_module;
DROP TABLE IF EXISTS userrole_collection;
DROP TABLE IF EXISTS userrole_folder;

DROP TABLE IF EXISTS cnxcollection;
DROP TABLE IF EXISTS cnxfolder;
DROP TABLE IF EXISTS cnxmodule;
DROP TYPE IF EXISTS cnxrole_type;

DROP TABLE IF EXISTS cnxacl;


CREATE TYPE cnxrole_type AS ENUM (
    'aclrw',
    'aclro'
);


CREATE TABLE cnxacl (
    id SERIAL,
    moduleid character varying,
    folderid character varying,
    collectionid character varying,
    userid character varying,
    roletype character varying
);


CREATE TABLE cnxcollection (
    id_ character varying PRIMARY KEY,
    title character varying,
    language character varying,
    "subType" character varying,
    subjects character varying[],
    keywords character varying[],
    summary character varying,
    authors character varying[],
    maintainers character varying[],
    copyrightHolders character varying[],
    editors character varying[],
    translators character varying[],
    acl character varying[],
    body character varying,
    dateCreatedUTC timestamp without time zone,
    dateLastModifiedUTC timestamp without time zone,
    mediaType character varying,
    googleTrackingID character varying
);

CREATE TABLE cnxfolder (
    id_ character varying PRIMARY KEY,
    title character varying,
    contents character varying[],
    dateCreatedUTC timestamp without time zone,
    dateLastModifiedUTC timestamp without time zone,
    mediaType character varying,
    acl character varying[]
);


CREATE TABLE cnxmodule (
    id_ character varying PRIMARY KEY,
    title character varying,
    authors character varying[],
    maintainers character varying[],
    copyrightHolders character varying[],
    editors character varying[],
    translators character varying[],
    acl character varying[],
    body character varying,
    language character varying,
    subType character varying,
    subjects character varying[],
    keywords character varying[],
    summary character varying,
    dateCreatedUTC timestamp without time zone,
    dateLastModifiedUTC timestamp without time zone,
    mediaType character varying,
    googleTrackingID character varying
);

CREATE TABLE session_cache (
    sessionid character varying PRIMARY KEY,
    userdict character varying NOT NULL,
    session_startutc timestamp with time zone,
    session_endutc timestamp with time zone
);


CREATE TABLE userrole_collection (
    collection_uuid character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type NOT NULL,
    beginDateUTC timestamp without time zone,
    endDateUTC timestamp without time zone
);


CREATE TABLE userrole_folder (
    folder_uuid character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type NOT NULL,
    beginDateUTC timestamp without time zone,
    endDateUTC timestamp without time zone
);


CREATE TABLE userrole_module (
    module_uri character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type,
    beginDateUTC timestamp without time zone,
    endDateUTC timestamp without time zone
);


ALTER TABLE ONLY userrole_collection
    ADD CONSTRAINT userrole_collection_pkey PRIMARY KEY (collection_uuid, user_id, role_type);

ALTER TABLE ONLY userrole_folder
    ADD CONSTRAINT userrole_folder_pkey PRIMARY KEY (folder_uuid, user_id, role_type);

ALTER TABLE ONLY userrole_module
    ADD CONSTRAINT userrole_module_pkey PRIMARY KEY (module_uri, user_id);

ALTER TABLE ONLY userrole_collection
    ADD CONSTRAINT userrole_collection_collection_uuid_fkey FOREIGN KEY (collection_uuid) REFERENCES cnxcollection(id_);

ALTER TABLE ONLY userrole_folder
    ADD CONSTRAINT userrole_folder_folder_uuid_fkey FOREIGN KEY (folder_uuid) REFERENCES cnxfolder(id_);

ALTER TABLE ONLY userrole_module
    ADD CONSTRAINT userrole_module_module_uri_fkey FOREIGN KEY (module_uri) REFERENCES cnxmodule(id_);

"""

