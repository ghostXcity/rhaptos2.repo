
import os
import json
import pprint
from rhaptos2.repo import backend, model
from rhaptos2.repo.tests import decl
from rhaptos2.repo.backend import db_session
from rhaptos2.common import conf

owner = decl.users['paul'].useruri


CONFD_PATH = os.path.join(".", "../../testing.ini")
confd = conf.get_config(CONFD_PATH)
# backend.clean_dbase(confd['app'])
backend.initdb(confd['app'])
