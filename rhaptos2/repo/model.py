#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""dbase-backed models for content on unpub repositories
-----------------------------------------------------

This module provides the class defintions for

* :class:`Module`
* :class:`Folder`
* :class:`Collection`

These are backd onto SQLAlchemy foundations and then onto PostgresQL
database.  An explcit use of the ARRAY datatype in postgres limits the
ability to swap out backends.

Security
--------

We expect to receive a HTTP HEADER (REMOTE_USER / X-Fake-CNXUser) with
a user-uri

A cnx user-uri is in the glossary (!)

.. todo::
   We may need to write a custom handfler for sqlite3 to deal
   with ARRAY typoes to make on local dev machine testing easier.




models:  I am trying to keep things simple.  This may not be a good idea.

each model is a class, based on a SQLAlchemy foundation with :class:CNXBase
as a extra inheritence.  This CNXBase gives us to and from json capabilities,
but each model has to manually override to and from json calls if


What is the same about each model / class

1. They have only themselves - there are no child tables needing
   hierarchialcly handling.  If this was needed we should look at
   rhaptos2.user for the approach - pretty simple, just modiufy the
   from and to dict calls

2. They are representing *resources* - that is a entity we want to
   have some form of access control over.  So we use the generic-ish
   approach of userroles - see below.


3. THey are all ID'd by URI


Note on json - the obvious generic approach, of traversing the SQLA
model and converting to/from JSON automagically has so far failed.
There are no sensible approaches "out there", seemingly because the
obvious approaches (iter) have already been hijacked by SQLA and
the edge cases are producing weird effects.


So, this basically implies a protocol for objects / classes

1. support creater_uri= in your constructor
2. override fomr and to json SQLA where needed
3. Support ACLs
4. err ....

"""

from sqlalchemy import (ForeignKey,
                        Column, String,
                        Enum, DateTime,
                        UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
import uuid
from cnxbase import CNXBase
from rhaptos2.repo import dolog
from rhaptos2.repo.backend import Base, db_session
from err import (Rhaptos2Error,
                 Rhaptos2SecurityError,
                 Rhaptos2AccessNotAllowedError,
                 Rhaptos2HTTPStatusError)
import json
from flask import abort

################## COLLECTIONS #############################


class UserRoleCollection(Base, CNXBase):
    """The roles and users assigned for a given folder
    """
    __tablename__ = 'userrole_collection'
    collection_uuid = Column(String, ForeignKey('cnxcollection.id_'),
                             primary_key=True)
    user_uri = Column(String, primary_key=True)
    role_type = Column(Enum('aclrw', 'aclro', name="cnxrole_type"),
                       primary_key=True)
    beginDateUTC = Column(DateTime)
    endDateUTC = Column(DateTime)  # noqa
    UniqueConstraint(collection_uuid, user_uri, name="uniq_collection_user")

    def __repr__(self):
        return "%s-%s" % (self.role_type, self.user_uri)


class Collection(Base, CNXBase):
    """
    """
    __tablename__ = 'cnxcollection'
    id_ = Column(String, primary_key=True)
    title = Column(String)
    language = Column(String)
    subType = Column(String)
    subjects = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    summary = Column(String)
    authors = Column(ARRAY(String))
    maintainers = Column(ARRAY(String))
    copyrightHolders = Column(ARRAY(String))
    acl = Column(ARRAY(String))

    body = Column(String)
    dateCreatedUTC = Column(DateTime)
    dateLastModifiedUTC = Column(DateTime)
    mediaType = Column(String)

    userroles = relationship("UserRoleCollection",
                             backref="cnxcollection",
                             cascade="all, delete-orphan")
    
    ### cheat to ensure can use a CNXBase function instead of 3 repeted code chunks
    userroleklass = UserRoleCollection
    
    def __init__(self, id_=None, creator_uuid=None):
        """ """
        self.userroleklass = UserRoleCollection
        self.mediaType = "application/vnd.org.cnx.collection"
        if creator_uuid:
            self.adduserrole(UserRoleCollection,
                             {'user_uri': creator_uuid, 'role_type': 'aclrw'},
                             requesting_user_uri=creator_uuid)
        else:
            raise Rhaptos2Error("Foldersmust be created with a creator UUID ")

        if id_:
            self.id_ = id_
        else:
            self.id_ = "cnxcollection:" + str(uuid.uuid4())

        self.dateCreatedUTC = self.get_utcnow()

    def __repr__(self):
        return "Col:(%s)-%s" % (self.id_, self.title)

    # def set_acls(self, owner_uuid, aclsd):
    #     """allow each Folder / collection class to have a set_acls
    #     call, but catch here and then pass generic function the right
    #     UserRoleX klass.  Still want to find way to generically follow
    #     sqla

    #     """

    #     super(Collection, self).set_acls(owner_uuid, aclsd,
    #                                      UserRoleCollection)
    #     db_session.add(self)
    #     db_session.commit()


        

################# Modules ##################################

class UserRoleModule(Base, CNXBase):

    """The roles and users assigned for a given folder
    """
    __tablename__ = 'userrole_module'
    module_uri = Column(String, ForeignKey('cnxmodule.id_'),
                        primary_key=True)
    user_uri = Column(String, primary_key=True)
    role_type = Column(Enum('aclrw', 'aclro',
                            name="cnxrole_type"),
                       )
    beginDateUTC = Column(DateTime)
    endDateUTC = Column(DateTime)  # noqa
    UniqueConstraint(module_uri, user_uri, name="uniq_mod_user")

    def __repr__(self):
        return "%s-%s" % (self.role_type, self.user_uri)


class Module(Base, CNXBase):
    """

    >>> #test we can autogen a uuid
    >>> m = Module(id_=None, creator_uuid="cnxuser:1234")
    >>> m.mediaType
    'application/vnd.org.cnx.module'
    >>> j = m.jsonify("cnxuser:1234")
    {...
    >>> d = json.loads(j)
    >>> assert 'id' in d.keys()
    >>> assert 'mediaType' in d.keys()

    """
    __tablename__ = 'cnxmodule'
    id_ = Column(String, primary_key=True)
    title = Column(String)
    authors = Column(ARRAY(String))
    maintainers = Column(ARRAY(String))
    copyrightHolders = Column(ARRAY(String))
    acl = Column(ARRAY(String))
    body = Column(String)
    language = Column(String)
    subType = Column(String)
    subjects = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    summary = Column(String)

    dateCreatedUTC = Column(DateTime)
    dateLastModifiedUTC = Column(DateTime)
    mediaType = Column(String)

    userroles = relationship("UserRoleModule",
                             backref="cnxmodule",
                             cascade="all, delete-orphan")
    userroleklass = UserRoleModule
    
    def __init__(self, id_=None, creator_uuid=None):
        """
        setup a Module - validate given ID, extract data from db if needed
        add role for owner, create id if needed (ie new Module) and
        then save the lot.
        """
        self.userroleklass = UserRoleModule
        self.mediaType = "application/vnd.org.cnx.module"
        if not self.validateid(id_):
            raise Rhaptos2Error("%s not valid id" % id_)

        if creator_uuid:
            self.adduserrole(UserRoleModule,
                             {'user_uri': creator_uuid, 'role_type': 'aclrw'},
                             requesting_user_uri=creator_uuid)
        else:
            raise Rhaptos2Error("Modules need owner provided at init ")

        if id_:
            self.id_ = id_
        else:
            self.id_ = "cnxmodule:" + str(uuid.uuid4())
        self.dateCreatedUTC = self.get_utcnow()
        super(Base, self).__init__()#trigger all SQLA Base calss inits.
        #self.save(db_session) #SAve to disk.
        
    def __repr__(self):
        return "Module:(%s)-%s" % (self.id_, self.title)

    # def set_acls(self, owner_uuid, aclsd):
    #     """allow each Module class to have a set_acls call, but catch
    #         here and then pass generic function the right UserRoleX
    #         klass.  Still want to find way to generically follow
    #         sqla

    #     """

    #     super(Module, self).set_acls(owner_uuid, aclsd, UserRoleModule)
    #     db_session.add(self)
    #     db_session.commit()


################## FOLDERS #################################

class UserRoleFolder(Base, CNXBase):
    """The roles and users assigned for a given folder

    We have following Roles: Owner, Maintainer, XXX


    :todo: storing timezones naively here needs fixing


    
    """
    __tablename__ = 'userrole_folder'
    folder_uuid = Column(String, ForeignKey('cnxfolder.id_'),
                         primary_key=True)
    user_uri = Column(String, primary_key=True)
    role_type = Column(Enum('aclrw', 'aclro',
                       name="cnxrole_type"),
                       primary_key=True)
    beginDateUTC = Column(DateTime)
    endDateUTC = Column(DateTime)
    UniqueConstraint(folder_uuid, user_uri, name="uniq_fldr_user")

    def __repr__(self):
        return "%s-%s" % (self.role_type, self.user_uri)


class Folder(Base, CNXBase):
    """FOlder Class inheriting from SQLAlchemy and from a CNXBase
    class to get a few generic functions.

    """
    __tablename__ = 'cnxfolder'
    id_ = Column(String, primary_key=True)
    title = Column(String)
    body = Column(ARRAY(String))
    dateCreatedUTC = Column(DateTime)
    dateLastModifiedUTC = Column(DateTime)
    mediaType = Column(String)
    acl = Column(ARRAY(String))
    userroles = relationship("UserRoleFolder",
                             backref="cnxfolder",
                             cascade="all, delete-orphan")
    
    userroleklass = UserRoleFolder
    
    def __init__(self, id_=None, creator_uuid=None):
        """ """
        ### A cheat really - need to access this later on and not sure how to extrac t from SQLA
        self.userroleklass = UserRoleFolder
        self.mediaType = "application/vnd.org.cnx.folder"

        if creator_uuid:
            self.adduserrole(UserRoleFolder,
                             {'user_uri': creator_uuid, 'role_type': 'aclrw'},
                             requesting_user_uri=creator_uuid)
        else:
            raise Rhaptos2Error("Foldersmust be created with a creator UUID ")
        if id_:
            self.id_ = id_
        else:
            self.id_ = "cnxfolder:" + str(uuid.uuid4())
        self.dateCreatedUTC = self.get_utcnow()

    def __repr__(self):
        return "Folder:(%s)-%s" % (self.id_, self.title)

    # def set_acls(self, owner_uuid, aclsd):
    #     """allow each Folder / collection class to have a set_acls
    #     call, but catch here and then pass generic function the right
    #     UserRoleX klass.  Still want to find way to generically follow
    #     sqla.

    #     """
    #     super(Folder, self).set_acls(owner_uuid, aclsd, UserRoleFolder)
    #     db_session.add(self)
    #     db_session.commit()

         

            
    def __complex__(self, requesting_user_uri, softform=True):
        """overwrite the std __complex__, and become recursive

        The "body" of a folder is a array of uris to other items (list of
        pointers) we only care at this point

        softform = returning not only the list of pointers, but also data
                   about the items pointed to (ie title, mediatype)

                   This is the default for a folder, and is private
                   to indicate we have no plans to change this for now.


        CURRENTLY NOT RECURSIVE - folders are limited to one level by policy.
        If this was a collection, and collections did not store body as 'li'
        then would a recursive descnet beyond one level be appropriate?  FIXME -
        implement a recursive base class that folder and collection use.

        NB - the shortform exhibits *surprising* behaviour
        If it encounters a missing link (ie folder links to a module that not exist)
        it will drop it on the floor - hence its possible for database to hold 6 mdoules in a folder
        and none will be returned.

        FIXME - this really needs a debate.

        """
        if not softform:
            return super(Folder, self).__complex__(requesting_user_uri, softform)

        short_format_list = []
        if self.body:
            for urn in self.body:
                try:
                    subfolder = obj_from_urn(urn, requesting_user_uri)
                    short_format_list.append({"id": subfolder.id_,
                                              "title": subfolder.title,
                                              "mediaType": subfolder.mediaType})
                    ### exceptions: if you cannot read a single child item
                    ### we still want to return rest of the folder
                except Rhaptos2SecurityError, e:
                    dolog("INFO", "Error thrown in folder recursion %s" % e)
                except Rhaptos2Error, e:
                    dolog("INFO", "Error thrown in folder recursion %s" % e)
                    # todo: should we be ignoring bnroken links??
                except Exception, e:
                    raise e

        ## so get the object as a json-suitable python object
        ## now alter the body to be the result of recursive ouutpu
        fldr = super(Folder, self).__complex__(requesting_user_uri)
        fldr['body'] = short_format_list
        return fldr


def klass_from_uri(URI):
    """Return the callable klass that corresponds to a URI

    >>> c = klass_from_uri("cnxfolder:1234")
    >>> c
    <class '__main__.Folder'>
    >>> c = klass_from_uri("cnxfolder:")
    >>> c
    <class '__main__.Folder'>
    >>> c = klass_from_uri("cnxfolder:1234/acl/cnxuser:123456")
    >>> c
    <class '__main__.Folder'>


    """
    mapper = {"cnxfolder": Folder,
              "cnxcollection": Collection,
              "cnxmodule": Module,
              #              "cnxuser": User,
              }
    ## get first part of uri even if :folder: or folfer:
    val = [v for v in URI.split(":") if v != ""][0]
    return mapper[val]


def obj_from_urn(URN, requesting_user_uri, klass=None):
    """
    THis is the refactored version of get_by_id

    URN
      cnxmodule:1234-5678

    requesting_user_urn
      cnxuser:1234-5678

    I have reservations about encoding the type in the ID string.
    But not many.

    """
    if not klass:
        try:
            klass = klass_from_uri(URN)
        except:
            dolog("INFO", "Failed getting klass %s" % URN)
            abort(400)

    q = db_session.query(klass)
    q = q.filter(klass.id_ == URN)
    rs = q.all()
    if len(rs) == 0:
        raise Rhaptos2Error("ID Not found in this repo")
    ### There is  a uniq constraint on the table, but anyway...
    if len(rs) > 1:
        raise Rhaptos2Error("Too many matches")

    newu = rs[0]
    if not change_approval(newu, {}, requesting_user_uri, "GET"):
        raise Rhaptos2AccessNotAllowedError("user %s not allowed access to %s"
                                            % (requesting_user_uri,
                                                URN))
    return newu


# def get_by_id(klass, ID, useruri):
#     """

#     refactoring:
#     ID -> uri
#     Then use uri -> klass to get klass needed
#     Then do not abort but raise capturable error.
#     THen pass useruri all way through.

#     """
#     q = db_session.query(klass)
#     q = q.filter(klass.id_ == ID)
#     rs = q.all()
#     if len(rs) == 0:
# #        raise Rhaptos2Error("ID Not found in this repo")
#         abort(404)
#     ### There is a uniq constraint on the table, but anyway...
#     if len(rs) > 1:
#         raise Rhaptos2Error("Too many matches")

#     newu = rs[0]
#     if not change_approval(newu, {}, useruri, "GET"):
#         abort(403)
#     return newu


def post_o(klass, incomingd, requesting_user_uri):
    """Given a dict representing the complete set
    of fields then create a new user and those fields

    I am getting a dictionary direct form Flask request object - want
    to handle that myself with parser.

    returns User object, for later saveing to DB"""

    u = klass(creator_uuid=requesting_user_uri)

    # parser = verify_schema_version(None)
    # incomingd = parser(json_str)
    u.populate_self(incomingd, requesting_user_uri=requesting_user_uri)
    if not change_approval(u, incomingd, requesting_user_uri, "POST"):
        abort(403)
    u.save(db_session)
    return u


# def acl_setter(klass, uri, requesting_user_uri, acls_list):
#     """ """
#     obj = get_by_id(klass, uri, requesting_user_uri)
#     if not change_approval(obj, None, requesting_user_uri, "PUT"):
#         abort(403)
#     obj.set_acls(requesting_user_uri, acls_list)
#     return obj


def put_o(jsond, klass, ID, requesting_user_uri):
    """Given a user_id, and a json_str representing the "Updated" fields
       then update those fields for that user_id """

    uobj = obj_from_urn(ID, requesting_user_uri)
    if not change_approval(uobj, jsond, requesting_user_uri, "PUT"):
        dolog("INFO", "Failed change approval %s %s " % (ID, requesting_user_uri))
        abort(403)
    #.. todo:: parser = verify_schema_version(None)
    uobj.populate_self(jsond, requesting_user_uri=requesting_user_uri)
    uobj.save(db_session)
    return uobj


def delete_o(resource_uri, requesting_user_uri):
    """ """
    fldr = obj_from_urn(resource_uri, requesting_user_uri)
    if not change_approval(fldr, None, requesting_user_uri, "DELETE"):
        raise Rhaptos2AccessNotAllowedError(
            "User %s cannot delete %s" % (requesting_user_uri,
                                          resource_uri))
    else:
        fldr.delete(db_session)


def close_session():
    db_session.remove()


def change_approval(uobj, jsond, requesting_user_uri, requesttype):
    """
    is the change valid for the given ACL context?
    returns True / False

    """
    return uobj.is_action_auth(action=requesttype,
                               requesting_user_uri=requesting_user_uri)


def workspace_by_user(user_uri):
    """Its at times like these I just want to pass SQL in... """

    qm = db_session.query(Module)
    qm = qm.join(Module.userroles)
    qm = qm.filter(UserRoleModule.user_uri == user_uri)
    rs1 = qm.all()

    qf = db_session.query(Folder)
    qf = qf.join(Folder.userroles)
    qf = qf.filter(UserRoleFolder.user_uri == user_uri)
    rs2 = qf.all()

    qc = db_session.query(Collection)
    qc = qc.join(Collection.userroles)
    qc = qc.filter(UserRoleCollection.user_uri == user_uri)
    rs3 = qc.all()

    rs1.extend(rs2)
    rs1.extend(rs3)
    db_session.commit()  # hail mary...
    return rs1


if __name__ == '__main__':
    import doctest
    doctest.testmod(
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS)
