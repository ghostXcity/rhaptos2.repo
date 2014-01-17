# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Database models and utilities"""
import os
import psycopg2


CONNECTION_SETTINGS_KEY = 'db-connection-string'
ARCHIVE_CONNECTION_SETTINGS_KEY = 'archive-db-connection-string'

here = os.path.abspath(os.path.dirname(__file__))
SQL_DIRECTORY = os.path.join(here, 'sql')
DB_SCHEMA = os.path.join(SQL_DIRECTORY, 'schema.sql')

def _read_sql_file(name):
    path = os.path.join(SQL_DIRECTORY, '{}.sql'.format(name))
    with open(path, 'r') as fp:
        return fp.read()
SQL = {
    'get-content': _read_sql_file('get-content'),
    'get-folder': _read_sql_file('get-folder'),
    'get-folder-contents': _read_sql_file('get-folder-contents'),
    'get-workspace': _read_sql_file('get-workspace'),
    'check-uid-in-archive': _read_sql_file('check-uid-in-archive'),
    'check-uid-n-version-in-archive': _read_sql_file('check-uid-n-version-in-archive'),
    }

def initdb(settings):
    with psycopg2.connect(settings[CONNECTION_SETTINGS_KEY]) as db_connection:
        with db_connection.cursor() as cursor:
            with open(DB_SCHEMA, 'r') as f:
                cursor.execute(f.read())
