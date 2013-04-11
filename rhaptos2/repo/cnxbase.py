#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""THis exists solely to provide less typing for a "leaf node" in a
simple realtional schema (1:M and 1:M-N:1) when used with SQLAlchemy

SA does not support class based inheritence in the normal Python way
for objects inheriting from Base.  Thus we have those objects perform
multiple inheritence...

"""
import json
import datetime
from err import Rhaptos2Error


class CNXBase():

    def validateid(self, id_):
        """Given a id_ check it is of correct uri format

        .. todo::
           validateid check really needs improving

        >>> C = CNXBase()
        >>> C.validateid("cnxuser:1234")
        True
        >>> C.validateid("1234")
        False

        """
        if not id_:
            return True
        elif id_.find(":") >= 0:
            return True
        else:
            return False

    def from_json(self, json_str):
        """ Not used at moment - json conversion usually done in
            web servers so this has little use for now."""
        d = json.loads(json_str)
        self.from_dict(d)

    def populate_self(self, d):
        ''' '''
        self.from_dict(d)

    def from_dict(self, userprofile_dict):
        """
        SHould test for schema validity etc.

        """
        idnames = ['id_', ]
        d = userprofile_dict
        for k in d:
            if k in idnames and d[k] is None:
                continue  # do not assign a id of None to the internal id
            else:
                setattr(self, k, d[k])

    def to_dict(self):
        """Return self as a dict, suitable for jsonifying """

        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.safe_type_out(col)
        return d

    def jsonify(self):
        """Helper function that returns simple json repr """
        selfd = self.to_dict()
        
        ##hacky - change output to use id not id_(backbone.js issue)
        ## .. todo:: validate broad assumptions about existence of these keys
        selfd['id'] = selfd['id_']; del selfd['id_']
        
        jsonstr = json.dumps(selfd)  # here use the Json ENcoder???
        return jsonstr

    def safe_type_out(self, col):
        """return the value of a coulmn field safely for json
        This is essentially a JSONEncoder sublclass inside object - ...
        """
        # XXX cannot get isinstance match on sqlalchem types
        if str(col.type) == "DATETIME":
            try:
                outstr = getattr(self, col.name).isoformat()
            except:
                outstr = None
        else:
            outstr = getattr(self, col.name)
        return outstr

    def set_acls(self, setter_user_uri, acllist, userrole_klass=None):
        """set the user acls on this object.

        inheriting from CNXBase implies we are modelling
        a resource, and we want to control Read?write of the resource
        through ACLs - which are represented in dbase as userrole_<resource>

        NB whilst practical to use one userrole table and preferable
        SQLAlchemy seems to place limits on it. and I dont want to
        muck about.

        SOme, not all objects that inherit form CNXBase (!)
        will have a relatred user_roles table.
        This will map the object ID to a acl type and a user


        [{'dateLastModifiedUTC': None,
          'dateCreatedUTC': None,
          'user_uri': u'Testuser1',
          'role_type': 'author'},
         {'dateLastModifiedUTC': None,
          'dateCreatedUTC': None,
          'user_uri': u'testuser2',
          'role_type': 'author'}]

        """
        # is this authorised? - sep function?
        if (setter_user_uri, "aclrw") not in [(u.user_uri, u.role_type)
           for u in self.userroles]:
            raise Rhaptos2Error("http:401")
        else:
            for usrdict in acllist:
                # I am losing modified info...
                self.adduserrole(userrole_klass, usrdict)

    def adduserrole(self, userrole_klass, usrdict):
        """ keeping a common funciton in one place

        Given a usr_uuid and a role_type, update a UserRole object

        I am checking setter_user is authorised in calling function.
        Ideally check here too.
        """
        t = self.get_utcnow()

        # why not pass around USerROle objects??
        user_uri = usrdict['user_uri']
        role_type = usrdict['role_type']

        if user_uri not in [u.user_uri for u in self.userroles]:
            # UserID is not in any assoc. role - add a new one
            i = userrole_klass()
            i.from_dict(usrdict)
            i.dateCreatedUTC = t
            i.dateLastModifiedUTC = t
            self.userroles.append(i)

        elif (user_uri, role_type) not in [(u.user_uri, u.role_type) for u
                                           in self.userroles]:
            # UserID has got a role, so *update*
            i = userrole_klass()
            i.from_dict(usrdict)
            i.dateLastModifiedUTC = t
            self.userroles.append(i)
        else:
            # user is there, user and role type is there, this is duplicate
            pass

    def parse_json(self, jsonstr):
        """Given a json-formatted string representing a folder, return a dict

        There is a lot todo here.
        We should have version handling (see online discussions)
        We should check that the json is actually valid for a folder
        """
        try:
            jsond = json.loads(jsonstr)
        except:
            raise Rhaptos2Error("Error converting json to dict")
        return jsond

    def get_utcnow(self):
        """Eventually we shall handle TZones here too"""
        return datetime.datetime.utcnow()

    def is_action_auth(self, action=None,
                       requesting_user_uri=None):
        """ Given a user and a action type, determine if it is
            authorised on this object

        #unittest not available as setup is large.
        >> C = CNXBase()
        >> C.is_action_auth(action="PUT", requesting_user_uri="Fake1")
        *** [u'Fake1']
        True
        >> C.is_action_auth(action="PUT", requesting_user_uri="ff")
        *** [u'Fake1']
        False

        """
        s = "*****AUTH"
        s += "model" + str(self)
        s += "action" + str(action)
        s += "user" + str(requesting_user_uri)
        s += "*****/AUTH"
        dolog("INFO", s)
        if action in ("GET", "HEAD", "OPTIONS"):
            valid_user_list = [u.user_uri for u in self.userroles
                               if u.role_type in ("aclro", "aclrw")]
        elif action in ("POST", "PUT", "DELETE"):
            valid_user_list = [u.user_uri for u in self.userroles
                               if u.role_type in ("aclrw",)]
        else:
            # raise Rhaptos2SecurityError("Unknown action type: %s" % action)
            return False

        if requesting_user_uri is None:
            # raise Rhaptos2SecurityError("No user_uri supplied: %s" %
            #                            requesting_user_uri)
            return False
        else:
            if requesting_user_uri in valid_user_list:
                return True
            else:
                return False


if __name__ == '__main__':
    import doctest
    doctest.testmod()
