
import os
import json
import pprint
from rhaptos2.repo import backend, model
from rhaptos2.repo.tests import decl
from rhaptos2.repo.backend import db_session
from rhaptos2.common import conf
from rhaptos2.repo import sessioncache
d = {'pghost': '127.0.0.1',
     'pgusername': 'repo',
     'pgpassword': 'repopass',
     'pgdbname': 'dbtest'}

sessioncache.set_config(d)

CONFD_PATH = os.path.join(".", "../../../testing.ini")
confd = conf.get_config(CONFD_PATH)
# backend.clean_dbase(confd['app'])
backend.initdb(confd['app'])
