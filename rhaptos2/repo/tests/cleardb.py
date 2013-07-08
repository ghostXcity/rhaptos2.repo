
import logging
logging.basicConfig(file="clear-db.log", level=logging.INFO)

import os
import json
import pprint
from rhaptos2.repo import backend, model, sessioncache
from rhaptos2.repo.backend import db_session
from rhaptos2.common import conf


CONFD_PATH = os.path.join(".", "../../../testing.ini")
confd = conf.get_config(CONFD_PATH)
# backend.clean_dbase(confd['app'])
backend.initdb(confd['app'])
backend.clean_dbase(confd['app'])


def convert_config(config):
    """
    This is done to convert the "dict" from configuration into true dict.

    FIXME - this is ridiculous - just go back to one confd object
    """
    defaultsection = 'app'
    for k in config[defaultsection]:
        config[k] = config[defaultsection][k]
    # del config[defaultsection]
    return config

xconfd = convert_config(confd)
sessioncache.set_config(xconfd)
sessioncache._fakesessionusers()
