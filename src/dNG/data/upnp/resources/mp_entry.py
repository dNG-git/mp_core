# -*- coding: utf-8 -*-

"""
MediaProvider
A device centric multimedia solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?mp;core

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,no-name-in-module

from copy import copy
from sqlalchemy.sql.functions import count as sql_count
import re

try: from urllib.parse import quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import urlsplit
#

from dNG.data.binary import Binary
from dNG.data.file_center.entry import Entry
from dNG.data.mime_type import MimeType
from dNG.data.text.link import Link
from dNG.database.connection import Connection
from dNG.database.instances.data_linker_meta import DataLinkerMeta as _DbDataLinkerMeta
from dNG.database.instances.key_store import KeyStore as _DbKeyStore
from dNG.database.instances.mp_upnp_resource import MpUpnpResource as _DbMpUpnpResource
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.database.sort_definition import SortDefinition
from dNG.module.named_loader import NamedLoader
from dNG.runtime.not_implemented_exception import NotImplementedException
from dNG.runtime.type_exception import TypeException
from dNG.runtime.value_exception import ValueException
from dNG.vfs.implementation import Implementation

from .abstract import Abstract

class MpEntry(Entry, Abstract):
    """
"MpEntry" represents an database resource.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    _DB_INSTANCE_CLASS = _DbMpUpnpResource
    """
SQLAlchemy database instance class to initialize for new instances.
    """

    def __init__(self, db_instance = None, user_agent = None, didl_fields = None):
        """
Constructor __init__(MpEntry)

:param db_instance: Encapsulated SQLAlchemy database instance
:param user_agent: Client user agent
:param didl_fields: DIDL fields list

:since: v0.2.00
        """

        Abstract.__init__(self)
        Entry.__init__(self, db_instance)

        self.resource_title = None
        """
UPnP resource title
        """

        if (isinstance(db_instance, _DbMpUpnpResource)):
            with self:
                self._load_data()

                if (user_agent is not None): self.set_client_user_agent(user_agent)
                if (didl_fields is not None): self.set_didl_fields(didl_fields)
            #
        #

        self.supported_features['vfs_url'] = True
    #

    def add_content(self, resource):
        """
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.2.00
        """

        # pylint: disable=maybe-no-member

        _return = False

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
            _return = Abstract.add_content(self, resource)
        elif (resource.get_type() is not None):
            with self, self._lock:
                matched_entry = (self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id))
                                 .filter(_DbMpUpnpResource.vfs_url == resource.get_vfs_url())
                                 .scalar()
                                )

                if (matched_entry < 1):
                    self.add_entry(resource)
                    self.set_update_id("++")
                #
            #

            _return = True
        #

        return _return
    #

    def _apply_content_list_where_condition(self, db_query):
        """
Returns the modified SQLAlchemy database query with the "where" condition
applied.

:param db_query: Unmodified SQLAlchemy database query

:return: (object) SQLAlchemy database query
:since:  v0.2.00
        """

        raise NotImplementedException()
    #

    def get_content(self, position):
        """
Returns the UPnP content resource at the given position.

:param position: Position of the UPnP content resource to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.2.00
        """

        if (self.local.db_instance is None): raise ValueException("Database instance is not correctly initialized")

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
            children = Abstract.get_content(self, position)
        else:
            child_position = (position
                              if (self.content_offset is None or self.content_offset < 1) else
                              (position - self.content_offset)
                             )

            children = self.get_content_list()
        #

        if (len(children) < child_position): raise ValueException("UPnP content position out of range")
        return children[child_position]
    #

    def get_content_list(self):
        """
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.2.00
        """

        # pylint: disable=maybe-no-member,protected-access

        if (self.local.db_instance is None): raise ValueException("Database instance is not correctly initialized")

        _return = [ ]

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
            _return = Abstract.get_content_list(self)
        else:
            with self:
                db_query = self.local.db_instance.rel_mp_upnp_resource_children.join(_DbMpUpnpResource.rel_meta)

                if (self.is_supported("content_list_where_condition")):
                    db_query = self._apply_content_list_where_condition(db_query)
                    children_length = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
                else: children_length = self.local.db_instance.rel_meta.sub_entries

                if (children_length > 0):
                    db_query = self._apply_db_sort_definition(db_query, "MpEntry")

                    child_first = (0 if (self.content_offset is None or self.content_offset >= children_length) else self.content_offset)
                    child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
                    if (child_last is None or child_last >= children_length): child_last = children_length

                    if (child_first > 0): db_query = db_query.offset(child_first)
                    if (child_first <= child_last): db_query = db_query.limit(child_last - child_first)

                    _return = MpEntry.iterator(_DbMpUpnpResource, self.local.connection.execute(db_query), self.client_user_agent, self.didl_fields)
                #
            #
        #

        return _return
    #

    def get_content_list_of_type(self, _type = None):
        """
Returns the UPnP content resources of the given type or all ones between
offset and limit.

:param _type: UPnP resource type to be returned

:return: (list) List of UPnP resources
:since:  v0.2.00
        """

        # pylint: disable=maybe-no-member

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM
            or _type is None
            or (_type & MpEntry.TYPE_CDS_CONTAINER != MpEntry.TYPE_CDS_CONTAINER
                and _type & MpEntry.TYPE_CDS_ITEM != MpEntry.TYPE_CDS_ITEM
               )
           ):
            _return = Abstract.get_content_list_of_type(self, _type)
        else:
            with self:
                db_query = self.local.db_instance.rel_mp_upnp_resource_children

                if (_type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER): db_query = db_query.filter(_DbMpUpnpResource.mimeclass == "directory")
                else: db_query = db_query.filter(_DbMpUpnpResource.mimeclass != "directory")

                db_query = db_query.join(_DbMpUpnpResource.rel_meta)
                _return = [ ]

                if (self.is_supported("content_list_where_condition")):
                    db_query = self._apply_content_list_where_condition(db_query)
                    children_length = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
                else: children_length = self.local.db_instance.rel_meta.sub_entries

                if (children_length > 0):
                    db_query = self._apply_db_sort_definition(db_query, "MpEntry")

                    child_first = (0 if (self.content_offset is None or self.content_offset >= children_length) else self.content_offset)
                    child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
                    if (child_last is None or child_last >= children_length): child_last = children_length

                    if (child_first > 0): db_query = db_query.offset(child_first)
                    if (child_first <= child_last): db_query = db_query.limit(1 + child_last - child_first)

                    _return = MpEntry.iterator(_DbMpUpnpResource, self.local.connection.execute(db_query), self.client_user_agent, self.didl_fields)
                #
            #
        #

        return _return
    #

    def get_content_didl_xml(self):
        """
Returns an UPnP DIDL result of generated XML for all contained UPnP content
resources.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.2.00
        """

        with self: return Abstract.get_content_didl_xml(self)
    #

    def _get_default_sort_definition(self, context = None):
        """
Returns the default sort definition list.

:param context: Sort definition context

:return: (object) Sort definition
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_default_sort_definition({1})- (#echo(__LINE__)#)", self, context, context = "mp_core")

        return (SortDefinition([ ( "position", SortDefinition.ASCENDING ),
                                 ( "vfs_type", SortDefinition.ASCENDING ),
                                 ( "resource_title", SortDefinition.ASCENDING )
                               ])
                if (context == "MpEntry") else
                Entry._get_default_sort_definition(self, context)
               )
    #

    def get_parent_resource_id(self):
        """
Returns the UPnP resource parent ID.

:return: (str) UPnP resource parent ID; None if empty
:since:  v0.2.00
        """

        if (self.parent_resource_id is None):
            entry_data = self.get_data_attributes("role_id")

            if (entry_data['role_id'] == "upnp_root_container"): self.parent_resource_id = "0"
            else:
                parent_object = self.load_parent()
                if (isinstance(parent_object, Abstract)): self.parent_resource_id = parent_object.get_resource_id()
            #
        #

        return Abstract.get_parent_resource_id(self)
    #

    def _get_resource_class_scheme(self):
        """
Returns the scheme name based on this resource instance class.

:return: (str) UPnP resource scheme name
:since:  v0.2.00
        """

        return (NamedLoader.RE_CAMEL_CASE_SPLITTER
                .sub("\\1-\\2", self.__class__.__name__)
                .lower()
               )
    #

    def get_timestamp(self):
        """
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.2.00
        """

        with self:
            return (-1
                    if (self.local.db_instance.rel_meta is None) else
                    self.local.db_instance.rel_meta.time_sortable
                   )
        #
    #

    def get_total(self):
        """
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.2.00
        """

        _return = 0

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
            _return = Abstract.get_total(self)
        else:
            with self:
                if (self.is_supported("content_list_where_condition")):
                    db_query = self.local.db_instance.rel_mp_upnp_resource_children.join(_DbMpUpnpResource.rel_meta)
                    db_query = self._apply_content_list_where_condition(db_query)
                    _return = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
                else: _return = self.local.db_instance.rel_meta.sub_entries
            #
        #

        return _return
    #

    def get_type(self):
        """
Returns the UPnP resource type.

:return: (str) UPnP resource type; None if empty
:since:  v0.2.00
        """

        if (self.type is None):
            entry_data = self.get_data_attributes("vfs_type")

            if (entry_data['vfs_type'] == Entry.VFS_TYPE_ITEM):
                _return = MpEntry.TYPE_CDS_ITEM
                mimeclass = self.get_mimeclass()

                if (mimeclass == "audio"): _return |= MpEntry.TYPE_CDS_ITEM_AUDIO
                elif (mimeclass == "image"): _return |= MpEntry.TYPE_CDS_ITEM_IMAGE
                elif (mimeclass == "video"): _return |= MpEntry.TYPE_CDS_ITEM_VIDEO
            else:
                _return = MpEntry.TYPE_CDS_CONTAINER
                mimetype = self.get_mimetype()

                if (mimetype == "text/x-directory-upnp-audio"): _return |= MpEntry.TYPE_CDS_CONTAINER_AUDIO
                elif (mimetype == "text/x-directory-upnp-image"): _return |= MpEntry.TYPE_CDS_CONTAINER_IMAGE
                elif (mimetype == "text/x-directory-upnp-video"): _return |= MpEntry.TYPE_CDS_CONTAINER_VIDEO
            #

            _return = self._get_custom_type(_return)
        else: _return = Abstract.get_type(self)

        return _return
    #

    def _get_unknown_data_attribute(self, attribute):
        """
Returns the data for the requested attribute not defined for this instance.

:param attribute: Requested attribute

:return: (dict) Value for the requested attribute
:since:  v0.2.00
        """

        return (self.local.db_instance.rel_resource_metadata.value
                if (attribute == "metadata" and self.local.db_instance.rel_resource_metadata is not None) else
                Entry._get_unknown_data_attribute(self, attribute)
               )
    #

    get_vfs_url = Entry.get_vfs_url
    """
Returns the VFS URL of this instance.

:return: (str) UPnP resource VFS URL; None if undefined
:since:  v0.2.00
    """

    def init_cds_id(self, _id, client_user_agent = None, deleted = False):
        """
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
        """

        _return = Abstract.init_cds_id(self, _id, client_user_agent, deleted)

        if (_return):
            url_elements = urlsplit(self.resource_id)

            with Connection.get_instance():
                if (url_elements.scheme == "mp-entry" or url_elements.scheme.startswith("mp-entry-")):
                    if (self.local.db_instance is None):
                        self.local.db_instance = Entry.get_db_class_query(self.__class__).get(url_elements.path[1:])
                    #

                    if (self.local.db_instance is None): _return = False
                    else: self._load_data()
                else:
                    vfs_url = self.resource_id
                    self.resource_id = None

                    if (self.local.db_instance is None):
                        self.local.db_instance = (Entry.get_db_class_query(self.__class__)
                                                  .filter(_DbMpUpnpResource.vfs_url == vfs_url)
                                                  .first()
                                                 )
                    #

                    if (self.local.db_instance is None):
                        vfs_object = Implementation.load_vfs_url(vfs_url, True)
                        if (vfs_object.is_valid()): self._init_from_vfs_object(vfs_object)
                    else: self._load_data()

                    _return = (self.resource_id is not None)
                #
            #
        #

        return _return
    #

    def _init_from_vfs_object(self, vfs_object):
        """
Initialize an new UPnP resource based on the given VFS object instance.

:param vfs_object: VFS object instance

:since: v0.2.00
        """

        if (not vfs_object.is_valid()): raise ValueException("Underlying VFS object is not valid")
        self._ensure_thread_local_instance()

        mimetype = vfs_object.get_mimetype()
        mimetype_definition = MimeType.get_instance().get(mimetype = mimetype)

        mimeclass = (mimetype.split("/", 1)[0] if (mimetype_definition is None) else mimetype_definition['class'])

        self.name = vfs_object.get_name()
        self.resource_id = "{0}:///{1}".format(self._get_resource_class_scheme(), self.get_id())
        self.mimeclass = mimeclass
        self.mimetype = mimetype
        self.source = "MediaProvider"

        vfs_type = (Entry.VFS_TYPE_DIRECTORY
                    if (vfs_object.is_directory()) else
                    Entry.VFS_TYPE_ITEM
                   )

        self.set_data_attributes(title = self.name,
                                 vfs_type = vfs_type,
                                 vfs_url = vfs_object.get_url(),
                                 mimeclass = self.mimeclass,
                                 mimetype = self.mimetype,
                                 resource_title = self.name
                                )

        self.type = self.get_type()
    #

    def _insert(self):
        """
Insert the instance into the database.

:since: v0.2.00
        """

        # pylint: disable=maybe-no-member

        with self.local.connection.no_autoflush:
            Entry._insert(self)

            if (self.local.db_instance.mimeclass == "directory"):
                parent_object = self.load_parent()
                if (isinstance(parent_object, MpEntry)): self.local.db_instance.mimetype = parent_object.get_mimetype()
            #
        #
    #

    def _load_data(self):
        """
Loads the MpEntry instance and populates variables.

:since: v0.2.00
        """

        with self:
            entry_data = self.get_data_attributes("id", "id_parent", "title", "vfs_url", "mimeclass", "mimetype", "resource_title", "size")

            self.db_id = entry_data['id']
            self.name = entry_data['title']
            self.mimeclass = entry_data['mimeclass']
            self.mimetype = entry_data['mimetype']
            self.resource_title = entry_data['resource_title']
            self.size = entry_data['size']
            self.source = "MediaProvider"
            self.type = self.get_type()
            # self.updatable = True # @TODO: Support CreateObject & co.

            if (self.resource_id is None):
                self.resource_id = "{0}:///{1}".format(self._get_resource_class_scheme(), entry_data['id'])
            #

            self.searchable = True
        #
    #

    def load_parent(self):
        """
Load the parent instance.

:return: (object) Parent MpEntry instance
:since:  v0.2.00
        """

        # pylint: disable=maybe-no-member

        with self:
            db_parent_instance = self.local.db_instance.rel_parent

            _return = (None
                       if (db_parent_instance is None or (not isinstance(db_parent_instance, _DbMpUpnpResource))) else
                       MpEntry(db_parent_instance)
                      )
        #

        return _return
    #

    def refresh_metadata(self):
        """
Refresh metadata associated with the MpEntry.

:since: v0.2.00
        """

        vfs_object = self.get_vfs_object(True)

        try:
            self.timestamp = vfs_object.get_time_updated()
            self.size = vfs_object.get_size()

            entry_data = { "time_sortable": self.timestamp,
                           "size": self.size
                         }

            if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
                self.mimetype = vfs_object.get_mimetype()
                mimetype_definition = MimeType.get_instance().get(mimetype = self.mimetype)

                self.mimeclass = (self.mimetype.split("/", 1)[0]
                                  if (mimetype_definition is None) else
                                  mimetype_definition['class']
                                 )

                entry_data['mimeclass'] = self.mimeclass
                entry_data['mimetype'] = self.mimetype
            #

            with self: self.set_data_attributes(**entry_data)
        finally: vfs_object.close()
    #

    def remove_content(self, resource):
        """
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.2.00
        """

        # pylint: disable=maybe-no-member

        _return = False

        if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
            _return = Abstract.remove_content(self, resource)
        elif (resource.get_type() is not None):
            with self, self._lock:
                matched_entry = (self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id))
                                 .filter(_DbMpUpnpResource.vfs_url == resource.get_vfs_url())
                                 .scalar()
                                )

                if (matched_entry > 0):
                    self.remove_entry(resource)
                    self.set_update_id("++")

                    _return = True
                #
            #
        #

        return _return
    #

    def save(self):
        """
Saves changes of the MpEntry into the database.

:since: v0.2.00
        """

        with self:
            Entry.save(self)

            if (self.resource_id is None):
                self.resource_id = "{0}:///{1}".format(self._get_resource_class_scheme(), self.local.db_instance.id)
            #

            self.set_update_id("++")
        #
    #

    def search_content_didl_xml(self, search_criteria):
        """
Returns an UPnP DIDL result of generated XML for all UPnP content resources
matching the given UPnP search criteria.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.2.00
        """

        with self: return Abstract.search_content_didl_xml(self, search_criteria)
    #

    def set_data_attributes(self, **kwargs):
        """
Sets values given as keyword arguments to this method.

:since: v0.2.00
        """

        with self, self.local.connection.no_autoflush:
            Entry.set_data_attributes(self, **kwargs)

            if ("resource_title" in kwargs): self.local.db_instance.resource_title = Binary.utf8(kwargs['resource_title'])
            if ("refreshable" in kwargs): self.local.db_instance.refreshable = kwargs['refreshable']

            if ("metadata" in kwargs):
                is_empty = (kwargs['metadata'] is None or kwargs['metadata'].strip() == "")

                if (self.local.db_instance.rel_resource_metadata is None):
                    self.local.db_instance.rel_resource_metadata = _DbKeyStore()
                    self.local.db_instance.rel_resource_metadata.key = self.local.db_instance.id
                elif (is_empty): del(self.local.db_instance.rel_resource_metadata)

                if (not is_empty): self.local.db_instance.rel_resource_metadata.value = kwargs['metadata']
            #
        #
    #

    def set_sort_criteria(self, sort_criteria):
        """
Sets the UPnP sort criteria.

:param sort_criteria: UPnP sort criteria

:since: v0.2.00
        """

        # pylint: disable=protected-access

        Abstract.set_sort_criteria(self, sort_criteria)

        if (len(self.sort_criteria) > 0):
            criteria_list = (self.sort_criteria.copy() if (hasattr(self.sort_criteria, "copy")) else copy(self.sort_criteria))
            sort_definition = SortDefinition([ ( "vfs_type", SortDefinition.ASCENDING ) ])

            for criteria in criteria_list:
                criteria_first_char = criteria[:1]
                if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]
                direction = (SortDefinition.ASCENDING if (criteria_first_char == "+") else SortDefinition.DESCENDING)

                self.__class__._db_append_didl_field_sort_definition(sort_definition, criteria, direction)

                self.set_sort_definition(sort_definition)
            #
        #
    #

    def _supports_search_content(self):
        """
Returns false if the resource content can't be searched for.

:return: (bool) True if resource content is searchable.
:since:  v0.2.00
        """

        return self.get_searchable()
    #

    @staticmethod
    def _db_append_didl_field_sort_definition(sort_definition, didl_field, sort_direction):
        """
Append the DIDL field sort direction to the given sort definition.

:param sort_definition: Sort definition instance
:param didl_field: DIDL field
:param sort_direction: Sort direction

:since: v0.2.00
        """

        if (didl_field == "dc:date" or didl_field == "upnp:recordedStartDateTime"): sort_definition.append("time_sortable", sort_direction)
        elif (didl_field == "dc:title"):
            sort_definition.append("resource_title", sort_direction)
            sort_definition.append("title", sort_direction)
        #
    #

    @staticmethod
    def _db_apply_sort_filter(query, sort_criteria):
        """
Apply the filter to the given SQLAlchemy query instance.

:param query: SQLAlchemy query instance
:param sort_criteria: DIDL sort criteria

:return: (object) Modified SQLAlchemy query instance
:since:  v0.2.00
        """

        _return = query.order_by(_DbMpUpnpResource.vfs_type.asc())

        if (sort_criteria is None): criteria_list = [ ]
        else: criteria_list = (sort_criteria if (type(sort_criteria) is list) else sort_criteria.split(","))

        for criteria in criteria_list:
            criteria_first_char = criteria[:1]
            if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]

            if (criteria == "dc:date" or criteria == "upnp:recordedStartDateTime"):
                _return = _return.order_by(_DbDataLinkerMeta.time_sortable.desc()
                                           if (criteria_first_char == "-") else
                                           _DbDataLinkerMeta.time_sortable.asc()
                                          )
            elif (criteria == "dc:title"):
                _return = _return.order_by(_DbDataLinkerMeta.title.desc()
                                           if (criteria_first_char == "-") else
                                           _DbDataLinkerMeta.title.asc()
                                          )
            #
        #

        return _return
    #

    @staticmethod
    def get_root_containers_count():
        """
Returns the count of root container MpEntry entries.

:return: (int) Number of MpEntry entries
:since:  v0.2.00
        """

        with Connection.get_instance() as connection:
            db_query = (connection.query(sql_count(_DbMpUpnpResource.id))
                        .filter(_DbMpUpnpResource.role_id == "upnp_root_container")
                       )

            return db_query.scalar()
        #
    #

    @staticmethod
    def _get_http_upnp_stream_url(_id):
        """
Returns the HTTP URL to stream the given UPnP CDS ID.

:param _id: UPnP CDS ID

:return: (str) HTTP URL for streaming
:since:  v0.2.00
        """

        link_parameters = { "__virtual__": "/upnp/stream/{0}".format(quote(_id, "")) }
        return Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, link_parameters)
    #

    @staticmethod
    def load_encapsulating_entry(_id, client_user_agent = None, cds = None, deleted = False):
        """
Loads a matching MpEntry for the given MpEntry instance based ID or VFS URL.

:param _id: MpEntry instance based ID or VFS URL
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.2.00
        """

        if (_id is None): raise TypeException("MpEntry ID or VFS URL given is invalid")
        _return = None

        if ("://" in _id
            and (_id.startswith("mp-entry:") or _id.startswith("mp-entry-"))
           ): _return = MpEntry.load_cds_id(_id, client_user_agent, cds, deleted)
        else:
            vfs_object = Implementation.load_vfs_url(_id, True)

            if (vfs_object.is_directory()): entry_class_name = "dNG.data.upnp.resources.MpEntry"
            else:
                mimetype = vfs_object.get_mimetype()
                mimetype_definition = MimeType.get_instance().get(mimetype = mimetype)

                mimeclass = (mimetype.split("/", 1)[0] if (mimetype_definition is None) else mimetype_definition['class'])
                camel_case_mimeclass = "".join([ word.capitalize() for word in re.split("\\W", mimeclass) ])

                entry_class_name = "dNG.data.upnp.resources.MpEntry{0}".format(camel_case_mimeclass)
                if (not NamedLoader.is_defined(entry_class_name)): entry_class_name = "dNG.data.upnp.resources.MpEntry"
            #

            _return = NamedLoader.get_instance(entry_class_name, False)
            if (_return is not None and (not _return.init_cds_id(_id, client_user_agent, deleted))): _return = None
        #

        return _return
    #

    @classmethod
    def load_resource(cls, resource, client_user_agent = None, cds = None, deleted = False):
        """
Loads the matching MpEntry for the given UPnP resource.

:param cls: Expected encapsulating database instance class
:param resource: UPnP resource
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.2.00
        """

        if (resource is None): raise NothingMatchedException("UPnP resource is invalid")

        with Connection.get_instance():
            db_instance = (Entry.get_db_class_query(cls)
                           .filter(_DbMpUpnpResource.vfs_url == resource)
                           .first()
                          )

            if (db_instance is None): raise NothingMatchedException("UPnP resource '{0}' is invalid".format(resource))
            Entry._ensure_db_class(cls, db_instance)

            return MpEntry(db_instance)
        #
    #

    @staticmethod
    def load_root_containers(sort_criteria = "+dc:title", offset = 0, limit = -1):
        """
Loads a list of UPnP root container MpEntry instances.

:param sort_criteria: UPnP sort criteria
:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) List of MpEntry instances on success
:since:  v0.2.00
        """

        with Connection.get_instance() as connection:
            db_query = (connection.query(_DbMpUpnpResource)
                        .filter(_DbMpUpnpResource.role_id == "upnp_root_container")
                        .join(_DbMpUpnpResource.rel_meta)
                       )

            result = connection.execute(MpEntry._db_apply_sort_filter(db_query, sort_criteria))

            if (offset > 0): db_query = db_query.offset(offset)
            if (limit > 0): db_query = db_query.limit(limit)

            return ([ ] if (result is None) else MpEntry.buffered_iterator(_DbMpUpnpResource, result))
        #
    #
#
