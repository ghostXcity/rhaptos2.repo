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

security issues

Discussion

I see each resource (folder, module, collection) as a individual resource
with individually managed permissions.

Each function (GET PUT POST DELETE) should be requested through the API with
a security "thing" (useruri).  This is to try and keep stateless end to end
(ie not have to worry how we are handling sessions from the request point through the
backend)



Security use cases

folder

1. User has RW permission set on Folder F and children C1,C2


"""
## root logger set in application startup
import logging
lgr = logging.getLogger(__name__)

import json
import datetime
from err import Rhaptos2Error
from werkzeug.exceptions import BadRequest
import string


class CNXBase():
    """

    The resources we use (Folder, Collection, Module) all adhere to a common
    access protocol that is defined in :class:CNXBase.

    Where incomingjsond is a python representation of a json object that
    meets a folder jsonschema

    > f2 = model.Folder(creator_uuid=user_urn)
    > f2.populate_self(incomingjsond)
    f2 will now be populated

    > f2.to_dict(requesting_user_urn)
    Here I am getting the object to return as python std types,
    so they can be easily jsonified at the last possible minute.

    """
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

    def populate_self(self, d, requesting_user_id=None):
        ''' '''
        self.from_dict(d, requesting_user_id=requesting_user_id)

    def from_dict(self, userprofile_dict, requesting_user_id=None):
        """
        given a dict, derived from either test fixture or json POST
        populate the object.

        setattr is valid as a means of internally updating
        a sqlalchemy object, and will correctly pass the diamond lookup.

        >>> from rhaptos2.repo import model
        >>> m = model.Module(creator_uuid="test")
        >>> d = {"InvalidFieldName":100}
        >>> m.populate_self(d)
        Traceback (most recent call last):
          ...
        Rhaptos2Error: ...

        [correct usage would be as:]
        >>> d = {"title":"testtitle"}
        >>> m.populate_self(d)
        >>> m
        Module:(...)-testtitle


        """
        idnames = ['id_', ]
        d = userprofile_dict
        for k in d:
            if k in idnames and d[k] is None:
                continue  # do not assign a id of None to the internal id
            elif k not in self.__table__.columns:
                raise Rhaptos2Error(
                    "Tried to set attr %s when no matching table column" % k)
            elif k == "acl":
                ## convert acls into userrole assignments
                self.update_userroles(d[
                                      'acl'], requesting_user_id=requesting_user_id)
                setattr(self, k, d['acl'])
            elif k == "googleTrackingID":
                ### validate the ID - it must not have
                if not simple_xss_validation(d[k]):
                    raise BadRequest(
                        description="googleTrackingID cannot have script-like charaters in it")
                else:
                    setattr(self, k, d[k])
            else:
                setattr(self, k, d[k])

    def jsonify(self, requesting_user_id, softform=True):
        """
        public method to return the object as a JSON formatted string.


        form.  There are two types we *shall* support.  softform and hardform
        A resource only contains links (pointers) to other resources - so
        a container-type resource (folder, collection) will hold links only
        such as
         body = ["/folder/1234", "/module/5678"]

        However if we returned that resource to the client, it would then need
        to perform *n* more requests to get the title of each.

        To avoid this we return a softform

         body = [{'id': '/folder/1234', 'title': 'foo', 'mediatype':'application/vnd.org.cnx.folder'},
                 {'id': '/module/5678', 'title': 'bar', 'mediatype':'application/vnd.org.cnx.module'},

        This however needs us to descend into the container, and requiores a security check at each
        resource.  It also requires a flag for whih form.

        At the moment only folder has any need for a softform approach and it is the default here

        .. discussion::
           There seems to be two distinctions, softform/hardform where a object must descend into
           its own hierarchy and produce short-form versions of its children
           And a short-form long-form approach that needs to produce either the whole object
           or just a few items (title, id etc)

        """
        # get self as a (non-recursive) list of python types (ie json
        # encodaeable)
        self_as_complex = self.__complex__(requesting_user_id, softform)
        jsonstr = json.dumps(self_as_complex)
        return jsonstr

    def __complex__(self, requesting_user_id, softform=True):
        """Return self as a dict, suitable for jsonifying     """

        # softform and hardform have no distinction if there are
        # no child nodes
        if not self.is_action_auth("GET", requesting_user_id):
            raise Rhaptos2AccessNotAllowedError("user %s not allowed access to %s"
                                                % (requesting_user_id,
                                                self.id_))
        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.safe_type_out(col)
        d["id"] = d["id_"]
        return d

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

    def prep_delete_userrole(self, user_id, role_type=None):
        """policy: we are ignoring role type for now.  Any delete will delete
        the user, there should only be one roletype per user, and one user per
        resource.  This is policy not enforced

       *editing* a user's role is not transaction supported (del then add in one
        trans).  If we ever change policy we need to fix that

        """

        for usr in self.userroles:
            if usr.user_id == user_id:
                self.userroles.remove(usr)

    def set_acls(self, setter_user_id, acllist, userrole_klass=None):
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
          'user_id': u'Testuser1',
          'role_type': 'author'},
         {'dateLastModifiedUTC': None,
          'dateCreatedUTC': None,
          'user_id': u'testuser2',
          'role_type': 'author'}]

        """
        # is this authorised? - sep function?
        if (setter_user_id, "aclrw") not in [(u.user_id, u.role_type)
           for u in self.userroles]:
            raise Rhaptos2Error("http:401")
        else:
            for usrdict in acllist:
                # I am losing modified info...
                self.adduserrole(
                    userrole_klass, usrdict, requesting_user_id=setter_user_id)

    def update_userroles(self, proposed_acl_list, requesting_user_id):
        """
        Given a list of (valid) user uris, add them to SQLA list

        The proposed list is *always* accurate, *except* if it leaves off the
        current requesting_user_id, which is always added. (This may lead to some
        strange behaviour or test issues so be flexible)

        """
        #: We assume one auth check will suffice as there is by policy one
        #: acl only (aclrw).  More fine grained policy will need more checks.
        proceed = self.is_action_auth(
            action="PUT", requesting_user_id=requesting_user_id)
        if not proceed:
            raise Rhaptos2Error(
                "Action forbidden for user %s cannot update userroles" % requesting_user_id)

        ### am i not matching sessons to useruris?
        set_curr_uris = set(self.userroles)
        set_proposed_uris = set(proposed_acl_list)
        del_uris = set_curr_uris - set_proposed_uris
        add_uris = set_proposed_uris - set_curr_uris

        lgr.info(str(set_proposed_uris))
        lgr.info(str(set_curr_uris))

        for user_id in add_uris:
            lgr.info("will add following: %s" % str(add_uris))
            self.adduserrole(self.userroleklass,
                             {'user_id': user_id,
                              'role_type': 'aclrw'},
                             requesting_user_id=requesting_user_id)
        for user_id in del_uris:
            lgr.info("will deelte following: %s" % str(del_uris))
            self.prep_delete_userrole(user_id)

    def adduserrole(self, userrole_klass, usrdict, requesting_user_id):
        """ keeping a common funciton in one place

        Given a usr_uuid and a role_type, update a UserRole object

        I am checking setter_user is authorised in calling function.

        The requesting_user_id merry-go-round
        I am pushing the user name all over the place - I think because
        userrole.from_dict is in cnbxbase which is not exclusive as base for userrole module.
        SO have cnxbase klass for userroles as well. ToDO
        """
        t = self.get_utcnow()

        # why not pass around USerROle objects??
        user_id = usrdict['user_id']
        role_type = usrdict['role_type']

        if user_id not in [u.user_id for u in self.userroles]:
            # UserID is not in any assoc. role - add a new one
            i = userrole_klass()
            i.from_dict(usrdict, requesting_user_id=requesting_user_id)
            i.dateCreatedUTC = t
            i.dateLastModifiedUTC = t
            self.userroles.append(i)

        elif (user_id, role_type) not in [(u.user_id, u.role_type) for u
                                           in self.userroles]:
            # UserID has got a role, so *update*
            i = userrole_klass()
            i.from_dict(usrdict, requesting_user_id=requesting_user_id)
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

    def save(self, dbase_session):
        """
        Assumes we are working with sqlalchemy dbsessions

        This is a naive implementation of the dateModified field.
        More sensitive approaches would include taking the timestamp of
        a request as the point of all changes. FIXME
        """
        self.dateLastModifiedUTC = self.get_utcnow()
        dbase_session.add(self)
        dbase_session.commit()

    def delete(self, dbase_session):
        """
        Assumes we are working with sqlalchemy dbsessions

        """
        dbase_session.delete(self)
        dbase_session.commit()

    def is_action_auth(self, action=None,
                       requesting_user_id=None):
        """ Given a user and a action type, determine if it is
            authorised on this object



        #unittest not available as setup is large.
        >> C = CNXBase()
        >> C.is_action_auth(action="PUT", requesting_user_id="Fake1")
        *** [u'Fake1']
        True
        >> C.is_action_auth(action="PUT", requesting_user_id="ff")
        *** [u'Fake1']
        False

        """
        s = "***AUTHATTEMPT:"
        s += "-" + str(self)
        s += "-" + str(action)
        s += "-" + str(requesting_user_id)

        if action in ("GET", "HEAD", "OPTIONS"):
            valid_user_list = [u.user_id for u in self.userroles
                               if u.role_type in ("aclro", "aclrw")]
        elif action in ("POST", "PUT", "DELETE"):
            valid_user_list = [u.user_id for u in self.userroles
                               if u.role_type in ("aclrw",)]
        else:
            s += "FAILED - Unknown action type  %s" % action
            lgr.error(s)
            return False

        if requesting_user_id is None:
            s += "FAILED - None user supplied"
            lgr.error(s)
            return False
        else:
            if requesting_user_id not in valid_user_list:
                s += "FAIL - user not in valid list %s" % str(valid_user_list)
                lgr.error(s)
                return False
            else:
                # At last!
                s += "SUCCESS user in valid list %s" % str(valid_user_list)
                lgr.info(s)
                return True
###


def simple_xss_validation(html_fragment):
    """

    >>> simple_xss_validation("US-12345678-1")
    True
    >>> simple_xss_validation("<script>Evil</script>")
    False

    This is very quick and dirty, and we need some consideration
    over XSS escaping. FIXME
    """

    whitelist = string.ascii_letters + string.digits + "-" + string.whitespace
    lgr.info("Start XSS whitelist - %s" % html_fragment)
    for char in html_fragment:
        if char not in whitelist:
            lgr.error("Failed XSS whitelist - %s" % html_fragment)
            return False
    return True


if __name__ == '__main__':
    import doctest
    val = doctest.ELLIPSIS+doctest.REPORT_ONLY_FIRST_FAILURE + \
        doctest.IGNORE_EXCEPTION_DETAIL
    doctest.testmod(optionflags=val)
