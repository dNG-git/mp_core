# -*- coding: utf-8 -*-
##j## BOF

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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
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

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.binary import Binary
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.database.connection import Connection
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.database.sort_definition import SortDefinition
from dNG.pas.database.transaction_context import TransactionContext
from dNG.pas.database.instances.data_linker_meta import DataLinkerMeta as _DbDataLinkerMeta
from dNG.pas.database.instances.key_store import KeyStore as _DbKeyStore
from dNG.pas.database.instances.mp_upnp_resource import MpUpnpResource as _DbMpUpnpResource
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.exception_log_trap import ExceptionLogTrap
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from dNG.pas.runtime.type_exception import TypeException
from dNG.pas.runtime.value_exception import ValueException
from .abstract_thumbnail import AbstractThumbnail
from .thumbnail_mixin import ThumbnailMixin
from .thumbnail_resource_mixin import ThumbnailResourceMixin

class MpEntry(Resource, DataLinker, ThumbnailResourceMixin):
#
	"""
"MpEntry" represents an database resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	DB_CDS_TYPE_CONTAINER = _DbMpUpnpResource.CDS_TYPE_CONTAINER
	"""
Database container entry
	"""
	DB_CDS_TYPE_ITEM = _DbMpUpnpResource.CDS_TYPE_ITEM
	"""
Database item entry
	"""
	DB_CDS_TYPE_ROOT = _DbMpUpnpResource.CDS_TYPE_ROOT
	"""
Database root container entry
	"""
	_DB_INSTANCE_CLASS = _DbMpUpnpResource
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""

	def __init__(self, db_instance = None, user_agent = None, didl_fields = None):
	#
		"""
Constructor __init__(MpEntry)

:param db_instance: Encapsulated SQLAlchemy database instance
:param user_agent: Client user agent
:param didl_fields: DIDL fields list

:since: v0.1.00
		"""

		Resource.__init__(self)
		DataLinker.__init__(self, db_instance)
		ThumbnailResourceMixin.__init__(self)

		self.encapsulated_id = None
		"""
Encapsulated UPnP resource ID
		"""
		self.encapsulated_resource = None
		"""
Encapsulated UPnP resource
		"""
		self.resource_title = None
		"""
UPnP resource title
		"""

		if (isinstance(db_instance, _DbMpUpnpResource)):
		#
			with self:
			#
				self._load_data()

				if (user_agent is not None): self.set_client_user_agent(user_agent)
				if (didl_fields is not None): self.set_didl_fields(didl_fields)
			#
		#

		self.supported_features['thumbnail_file'] = True
	#

	def add_content(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member

		_return = False

		if (isinstance(resource, MpEntry) and resource.get_type() is not None):
		#
			with self, self._lock:
			#
				matched_entry = (self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id))
				                 .filter(_DbMpUpnpResource.resource == resource.get_encapsulated_id())
				                 .scalar()
				                )

				if (matched_entry < 1):
				#
					self.add_entry(resource)
					self.set_update_id("++")
				#
			#

			_return = True
		#

		return _return
	#

	def _apply_content_list_where_condition(self, db_query):
	#
		"""
Returns the modified SQLAlchemy database query with the "where" condition
applied.

:param db_query: Unmodified SQLAlchemy database query

:return: (object) SQLAlchemy database query
:since:  v0.1.02
		"""

		raise NotImplementedException()
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:since: v0.1.00
		"""

		with self, TransactionContext():
		#
			if (self.type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER):
			#
				for entry in self.get_content_list(): entry.delete()
			#

			db_resource_metadata_instance = self.local.db_instance.rel_resource_metadata

			DataLinker.delete(self)
			if (db_resource_metadata_instance is not None): self.local.connection.delete(db_resource_metadata_instance)
		#
	#

	def get_content(self, position):
	#
		"""
Returns the UPnP content resource at the given position.

:param position: Position of the UPnP content resource to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.1.01
		"""

		if (self.local.db_instance is None): raise ValueException("Database instance is not correctly initialized")

		child_position = (position if (self.content_offset is None or self.content_offset < 1) else (position - self.content_offset))
		children = self.get_content_list()

		if (len(children) < child_position): raise ValueException("UPnP content position out of range")
		return children[child_position]
	#

	def get_content_list(self):
	#
		"""
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member,protected-access

		if (self.local.db_instance is None): raise ValueException("Database instance is not correctly initialized")

		_return = [ ]

		if (self.type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER):
		#
			with self:
			#
				db_query = self.local.db_instance.rel_mp_upnp_resource_children.join(_DbMpUpnpResource.rel_meta)

				if (self.is_supported("content_list_where_condition")):
				#
					db_query = self._apply_content_list_where_condition(db_query)
					children_length = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
				#
				else: children_length = self.local.db_instance.rel_meta.sub_entries

				if (children_length > 0):
				#
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
		elif (self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
		#
			self._init_content()
			if (self.content is not None): _return = self.content
		#

		return _return
	#

	def get_content_list_of_type(self, _type = None):
	#
		"""
Returns the UPnP content resources of the given type or all ones between
offset and limit.

:param _type: UPnP resource type to be returned

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member

		if (_type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER): db_type = _DbMpUpnpResource.CDS_TYPE_CONTAINER
		elif (_type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM): db_type = _DbMpUpnpResource.CDS_TYPE_ITEM
		else: db_type = None

		if (db_type is None): _return = self.get_content_list()
		else:
		#
			with self:
			#
				db_query = self.local.db_instance.rel_mp_upnp_resource_children.filter(_DbMpUpnpResource.cds_type == db_type).join(_DbMpUpnpResource.rel_meta)
				_return = [ ]

				if (self.is_supported("content_list_where_condition")):
				#
					db_query = self._apply_content_list_where_condition(db_query)
					children_length = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
				#
				else: children_length = self.local.db_instance.rel_meta.sub_entries

				if (children_length > 0):
				#
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
	#
		"""
Returns an UPnP DIDL result of generated XML for all contained UPnP content
resources.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		with self: return Resource.get_content_didl_xml(self)
	#

	def _get_default_sort_definition(self, context = None):
	#
		"""
Returns the default sort definition list.

:param context: Sort definition context

:return: (object) Sort definition
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_default_sort_definition({1})- (#echo(__LINE__)#)", self, context, context = "pas_datalinker")

		return (SortDefinition([ ( "cds_type", SortDefinition.ASCENDING ),
		                         ( "position", SortDefinition.ASCENDING ),
		                         ( "resource_title", SortDefinition.ASCENDING )
		                       ])
		        if (context == "MpEntry") else
		        DataLinker._get_default_sort_definition(self, context)
		       )
	#

	def get_encapsulated_id(self):
	#
		"""
Returns the ID of the encapsulated resource.

:return: (str) UPnP encapsulated resource ID
:since:  v0.1.01
		"""

		return self.encapsulated_id
	#

	def get_encapsulated_resource(self):
	#
		"""
Returns the encapsulated resource if used to create the UPnP resource.

:return: (object) UPnP encapsulated resource
:since:  v0.1.01
		"""

		return self.encapsulated_resource
	#

	def get_parent_resource_id(self):
	#
		"""
Returns the UPnP resource parent ID.

:return: (str) UPnP resource parent ID; None if empty
:since:  v0.1.01
		"""

		if (self.parent_resource_id is None):
		#
			entry_data = self.get_data_attributes("cds_type")

			if (entry_data['cds_type'] == MpEntry.DB_CDS_TYPE_ROOT): self.parent_resource_id = "0"
			else:
			#
				parent_object = self.load_parent()
				if (isinstance(parent_object, Resource)): self.parent_resource_id = parent_object.get_resource_id()
			#
		#

		return Resource.get_parent_resource_id(self)
	#

	def get_thumbnail_file_path_name(self):
	#
		"""
Returns the thumbnail file path and name if applicable.

:return: (str) File path and name; None if no thumbnail file exist
:since:  v0.1.02
		"""

		_return = None

		with ExceptionLogTrap("pas_upnp"):
		#
			encapsulated_resource = self.load_encapsulated_resource()
			if (isinstance(encapsulated_resource, ThumbnailMixin)): _return = encapsulated_resource.get_thumbnail_file_path_name()
		#

		return _return
	#

	def get_mimeclass(self):
	#
		"""
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class; None if unknown
:since:  v0.1.01
		"""

		_return = self.mimeclass
		if (_return is None and self.encapsulated_resource is not None): _return = self.encapsulated_resource.get_mimeclass()

		if (_return is None):
		#
			_type = self.get_type()

			if (_type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
			#
				if (_type & MpEntry.TYPE_CDS_ITEM_AUDIO == MpEntry.TYPE_CDS_ITEM_AUDIO): _return = "audio"
				elif (_type & MpEntry.TYPE_CDS_ITEM_IMAGE == MpEntry.TYPE_CDS_ITEM_IMAGE): _return = "image"
				elif (_type & MpEntry.TYPE_CDS_ITEM_VIDEO == MpEntry.TYPE_CDS_ITEM_VIDEO): _return = "video"
			#
			elif (_type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER): _return = "directory"
		#

		if (_return is None): _return = "unknown"
		return _return
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.1.00
		"""

		with self:
		#
			return (-1
			        if (self.local.db_instance.rel_meta is None) else
			        self.local.db_instance.rel_meta.time_sortable
			       )
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.1.00
		"""

		_return = 0

		with self:
		#
			if (self.is_supported("content_list_where_condition")):
			#
				db_query = self.local.db_instance.rel_mp_upnp_resource_children.join(_DbMpUpnpResource.rel_meta)
				db_query = self._apply_content_list_where_condition(db_query)
				_return = db_query.from_self(sql_count(_DbMpUpnpResource.id)).scalar()
			#
			else: _return = self.local.db_instance.rel_meta.sub_entries
		#

		return _return
	#

	def get_type(self):
	#
		"""
Returns the UPnP resource type.

:return: (str) UPnP resource type; None if empty
:since:  v0.1.01
		"""

		if (self.type is None):
		#
			entry_data = self.get_data_attributes("cds_type")

			if (entry_data['cds_type'] == _DbMpUpnpResource.CDS_TYPE_ITEM):
			#
				_return = MpEntry.TYPE_CDS_ITEM

				if (self.mimeclass is not None): mimeclass = self.mimeclass
				elif (self.encapsulated_resource is not None): mimeclass = self.encapsulated_resource.get_mimeclass()
				else: mimeclass = self.get_mimetype().split("/")[0]

				if (mimeclass == "audio"): _return = MpEntry.TYPE_CDS_ITEM_AUDIO | MpEntry.TYPE_CDS_ITEM
				elif (mimeclass == "image"): _return = MpEntry.TYPE_CDS_ITEM_IMAGE | MpEntry.TYPE_CDS_ITEM
				elif (mimeclass == "video"): _return = MpEntry.TYPE_CDS_ITEM_VIDEO | MpEntry.TYPE_CDS_ITEM
			#
			else:
			#
				_return = MpEntry.TYPE_CDS_CONTAINER
				mimetype = self.get_mimetype()

				if (mimetype == "text/x-directory-upnp-audio"): _return = MpEntry.TYPE_CDS_CONTAINER | MpEntry.TYPE_CDS_CONTAINER_AUDIO
				elif (mimetype == "text/x-directory-upnp-image"): _return = MpEntry.TYPE_CDS_CONTAINER | MpEntry.TYPE_CDS_CONTAINER_IMAGE
				elif (mimetype == "text/x-directory-upnp-video"): _return = MpEntry.TYPE_CDS_CONTAINER | MpEntry.TYPE_CDS_CONTAINER_VIDEO
			#

			_return = self._get_custom_type(_return)
		#
		else: _return = Resource.get_type(self)

		return _return
	#

	def _get_unknown_data_attribute(self, attribute):
	#
		"""
Returns the data for the requested attribute not defined for this instance.

:param attribute: Requested attribute

:return: (dict) Value for the requested attribute
:since:  v0.1.00
		"""

		return (self.local.db_instance.rel_resource_metadata.value
		        if (attribute == "metadata" and self.local.db_instance.rel_resource_metadata is not None) else
		        DataLinker._get_unknown_data_attribute(self, attribute)
		       )
	#

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		Resource.init_cds_id(self, _id, client_user_agent, deleted)
		_return = (self.resource_id is not None)

		if (_return):
		#
			with Connection.get_instance():
			#
				url_elements = urlsplit(self.resource_id)

				if (url_elements.scheme == "mp-entry" or url_elements.scheme.startswith("mp-entry-")):
				#
					if (self.local.db_instance is None):
					#
						self.local.db_instance = (DataLinker.get_db_class_query(self.__class__)
						                          .filter(_DbMpUpnpResource.id == url_elements.path[1:])
						                          .first()
						                         )
					#

					if (self.local.db_instance is None): _return = False
					else: self._load_data()
				#
				else:
				#
					self.encapsulated_resource = Resource.load_cds_id(_id, deleted = True)

					if (self.encapsulated_resource is None): _return = False
					else:
					#
						self.encapsulated_id = self.encapsulated_resource.get_resource_id()

						if (self.local.db_instance is None):
						#
							self.local.db_instance = (DataLinker.get_db_class_query(self.__class__)
							                          .filter(_DbMpUpnpResource.resource == self.encapsulated_id)
							                          .first()
							                         )

							if (self.local.db_instance is None): self._init_encapsulated_resource()
							else:
							#
								self.resource_id = None
								self._load_data()
								_return = (self.resource_id is not None)
							#
						#

						self.updatable = self.encapsulated_resource.get_updatable()
					#
				#
			#
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		_return = False

		if (self.type is not None
		    and self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM
		   ):
		#
			_return = self._init_item_content()

			if (_return):
			#
				is_thumbnail_available = False

				for resource in self.content:
				#
					if (isinstance(resource, AbstractThumbnail)):
					#
						is_thumbnail_available = True
						break
					#
				#

				thumbnail_path_name = (None if (is_thumbnail_available) else self.get_thumbnail_file_path_name())

				if ((not is_thumbnail_available)
				    and thumbnail_path_name is not None
				   ): self.append_thumbnail_resources(self.content, thumbnail_path_name)
			#
		#

		return _return
	#

	def _init_encapsulated_resource(self):
	#
		"""
Initialize an new encapsulated UPnP resource.

:since: v0.1.00
		"""

		if (self.encapsulated_resource is None): raise ValueException("Encapsulated resource not accessible")
		self._ensure_thread_local_instance()

		self.resource_id = self.encapsulated_resource.get_resource_id()
		self.name = self.encapsulated_resource.get_name()
		self.mimeclass = self.encapsulated_resource.get_mimeclass()
		self.mimetype = self.encapsulated_resource.get_mimetype()
		self.source = "MediaProvider"
		self.type = self.encapsulated_resource.get_type()

		db_type = (_DbMpUpnpResource.CDS_TYPE_ITEM
		           if (self.encapsulated_resource.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM) else
		           _DbMpUpnpResource.CDS_TYPE_CONTAINER
		          )

		self.set_data_attributes(title = self.name,
		                         cds_type = db_type,
		                         mimeclass = self.mimeclass,
		                         mimetype = self.mimetype,
		                         resource_title = self.name,
		                         resource = self.encapsulated_id
		                        )
	#

	def _init_item_content(self):
	#
		"""
Initializes the content of an UPnP CDS item entry.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		_return = True

		encapsulated_resource = self.load_encapsulated_resource()

		if (encapsulated_resource is not None):
		#
			encapsulated_resource.set_parent_resource_id(self.get_resource_id())
			with ExceptionLogTrap("mp_server"): self.content = encapsulated_resource.get_content_list()
		#
		elif (self.log_handler is not None):
		#
			_return = False
			self.log_handler.warning("mp.MpEntry failed to load encapsulated resource for ID '{0}'", self.resource_id, context = "mp_server")
		#

		return _return
	#

	def _insert(self):
	#
		"""
Insert the instance into the database.

:since: v0.1.00
		"""

		# pylint: disable=maybe-no-member

		DataLinker._insert(self)

		with self.local.connection.no_autoflush:
		#
			if (self.local.db_instance.mimeclass == "directory"):
			#
				parent_object = self.load_parent()
				if (isinstance(parent_object, MpEntry)): self.local.db_instance.mimetype = parent_object.get_mimetype()
			#

			if (self.local.db_instance.resource_type is None):
			#
				self.local.db_instance.resource_type = NamedLoader.RE_CAMEL_CASE_SPLITTER.sub("\\1-\\2",
				                                                                              self.__class__.__name__
				                                                                             ).lower()
			#
		#
	#

	def is_resource_id(self, _id):
	#
		"""
Returns true if the given ID identifies this resource or the contained one.

:param _id: ID

:return: (bool) True if successful
:since:  v0.1.02
		"""

		return (_id == self.resource_id or _id == self.encapsulated_id)
	#

	def _load_data(self):
	#
		"""
Loads the MpEntry instance and populates variables.

:since: v0.1.00
		"""

		with self:
		#
			entry_data = self.get_data_attributes("id", "id_parent", "title", "mimeclass", "mimetype", "resource_type", "resource_title", "resource", "size")

			self.db_id = entry_data['id']
			self.name = entry_data['title']
			self.mimeclass = entry_data['mimeclass']
			self.mimetype = entry_data['mimetype']
			self.resource_title = entry_data['resource_title']
			self.encapsulated_id = entry_data['resource']
			self.size = entry_data['size']
			self.source = "MediaProvider"
			self.type = self.get_type()
			# self.updatable = True # @TODO: Support CreateObject & co.

			if (entry_data['resource_type'] == "mp-entry" or entry_data['resource_type'].startswith("mp-entry-")):
			#
				if (self.resource_id is None): self.resource_id = "{0}:///{1}".format(entry_data['resource_type'], entry_data['id'])
				self.searchable = True
			#
			else:
			#
				self.encapsulated_resource = Resource.load_cds_id(self.encapsulated_id, self.client_user_agent)
				if (self.resource_id is None): self.resource_id = self.encapsulated_id

				if (self.encapsulated_resource is not None):
				#
					self.encapsulated_resource.set_didl_fields(self.didl_fields)
					self.encapsulated_resource.set_sort_criteria(self.sort_criteria)

					self.searchable = self.encapsulated_resource.get_searchable()
				#
			#
		#
	#

	def load_encapsulated_resource(self, deleted = False):
	#
		"""
Returns the ID of the encapsulated resource.

:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.01
		"""

		return (Resource.load_cds_id(self.get_encapsulated_id(), self.client_user_agent, deleted = deleted)
		        if (self.encapsulated_resource is None) else
		        self.encapsulated_resource
		       )
	#

	def load_parent(self):
	#
		"""
Load the parent instance.

:return: (object) Parent MpEntry instance
:since:  v0.1.00
		"""

		# pylint: disable=maybe-no-member

		with self:
		#
			db_parent_instance = self.local.db_instance.rel_parent

			_return = (None
			           if (db_parent_instance is None or (not isinstance(db_parent_instance, _DbMpUpnpResource))) else
			           MpEntry(db_parent_instance)
			          )
		#

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with the MpEntry.

:since: v0.1.00
		"""

		encapsulated_resource = self.get_encapsulated_resource()

		if (encapsulated_resource is not None):
		#
			entry_data = { "refreshable": False,
			               "time_sortable": encapsulated_resource.get_timestamp(),
			               "size": encapsulated_resource.get_size()
			             }

			if (self.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
			#
				entry_data['mimeclass'] = encapsulated_resource.get_mimeclass()
				entry_data['mimetype'] = encapsulated_resource.get_mimetype()
			#

			self.set_data_attributes(**entry_data)
		#
	#

	def remove_content(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member

		_return = False

		if (isinstance(resource, MpEntry) and resource.get_type() is not None):
		#
			with self, self._lock:
			#
				matched_entry = (self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id))
				                 .filter(_DbMpUpnpResource.resource == resource.get_encapsulated_id())
				                 .scalar()
				                )

				if (matched_entry > 0):
				#
					self.remove_entry(resource)
					self.set_update_id("++")

					_return = True
				#
			#
		#

		return _return
	#

	def save(self):
	#
		"""
Saves changes of the MpEntry into the database. Encapsulated resources
used for "init_cds_id()" will be cleared.

:since: v0.1.00
		"""

		with self:
		#
			DataLinker.save(self)

			if (self.encapsulated_resource is not None): self.encapsulated_resource = None
			if (self.resource_id is None): self.resource_id = "{0}:///{1}".format(self.local.db_instance.resource_type, self.local.db_instance.id)
			self.set_update_id("++")
		#
	#

	def search_content_didl_xml(self, search_criteria):
	#
		"""
Returns an UPnP DIDL result of generated XML for all UPnP content resources
matching the given UPnP search criteria.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		with self: return Resource.search_content_didl_xml(self, search_criteria)
	#

	def _set_cds_resource_type(self):
	#
		"""
Set this MpEntry to be a CDS resource.

:since: v0.1.00
		"""

		resource_type = self.get_type()
		if (resource_type & MpEntry.TYPE_CDS_ITEM != MpEntry.TYPE_CDS_ITEM): raise ValueException("Unsupported operation")

		self.encapsulated_resource = None

		if (resource_type & MpEntry.TYPE_CDS_ITEM_AUDIO == MpEntry.TYPE_CDS_ITEM_AUDIO): self.type = MpEntry.TYPE_CDS_ITEM_AUDIO | MpEntry.TYPE_CDS_RESOURCE
		if (resource_type & MpEntry.TYPE_CDS_ITEM_IMAGE == MpEntry.TYPE_CDS_ITEM_IMAGE): self.type = MpEntry.TYPE_CDS_ITEM_IMAGE | MpEntry.TYPE_CDS_RESOURCE
		if (resource_type & MpEntry.TYPE_CDS_ITEM_VIDEO == MpEntry.TYPE_CDS_ITEM_VIDEO): self.type = MpEntry.TYPE_CDS_ITEM_VIDEO | MpEntry.TYPE_CDS_RESOURCE
		else: self.type = MpEntry.TYPE_CDS_RESOURCE
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		with self, self.local.connection.no_autoflush:
		#
			DataLinker.set_data_attributes(self, **kwargs)

			if ("cds_type" in kwargs): self.local.db_instance.cds_type = kwargs['cds_type']
			if ("mimeclass" in kwargs): self.local.db_instance.mimeclass = kwargs['mimeclass']
			if ("mimetype" in kwargs): self.local.db_instance.mimetype = kwargs['mimetype']
			if ("resource_type" in kwargs): self.local.db_instance.resource_type = kwargs['resource_type']
			if ("resource_title" in kwargs): self.local.db_instance.resource_title = Binary.utf8(kwargs['resource_title'])
			if ("resource" in kwargs): self.local.db_instance.resource = Binary.utf8(kwargs['resource'])
			if ("refreshable" in kwargs): self.local.db_instance.refreshable = kwargs['refreshable']
			if ("size" in kwargs): self.local.db_instance.size = kwargs['size']

			if ("metadata" in kwargs):
			#
				is_empty = (kwargs['metadata'] is None or kwargs['metadata'].strip() == "")

				if (self.local.db_instance.rel_resource_metadata is None):
				#
					self.local.db_instance.rel_resource_metadata = _DbKeyStore()
					self.local.db_instance.rel_resource_metadata.key = self.local.db_instance.id
				#
				elif (is_empty): del(self.local.db_instance.rel_resource_metadata)

				if (not is_empty): self.local.db_instance.rel_resource_metadata.value = kwargs['metadata']
			#
		#
	#

	def set_sort_criteria(self, sort_criteria):
	#
		"""
Sets the UPnP sort criteria.

:param sort_criteria: UPnP sort criteria

:since: v0.1.01
		"""

		# pylint: disable=protected-access

		Resource.set_sort_criteria(self, sort_criteria)

		if (len(self.sort_criteria) > 0):
		#
			criteria_list = (self.sort_criteria.copy() if (hasattr(self.sort_criteria, "copy")) else copy(self.sort_criteria))
			sort_definition = SortDefinition([ ( "cds_type", SortDefinition.ASCENDING ) ])

			for criteria in criteria_list:
			#
				criteria_first_char = criteria[:1]
				if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]
				direction = (SortDefinition.ASCENDING if (criteria_first_char == "+") else SortDefinition.DESCENDING)

				self.__class__._db_append_didl_field_sort_definition(sort_definition, criteria, direction)

				self.set_sort_definition(sort_definition)
			#
		#
	#

	def _supports_search_content(self):
	#
		"""
Returns false if the resource content can't be searched for.

:return: (bool) True if resource content is searchable.
:since:  v0.1.00
		"""

		return self.get_searchable()
	#

	@staticmethod
	def _db_append_didl_field_sort_definition(sort_definition, didl_field, sort_direction):
	#
		"""
Append the DIDL field sort direction to the given sort definition.

:param sort_definition: Sort definition instance
:param didl_field: DIDL field
:param sort_direction: Sort direction

:since: v0.1.01
		"""

		if (didl_field == "dc:date" or didl_field == "upnp:recordedStartDateTime"): sort_definition.append("time_sortable", sort_direction)
		elif (didl_field == "dc:title"):
		#
			sort_definition.append("resource_title", sort_direction)
			sort_definition.append("title", sort_direction)
		#
	#

	@staticmethod
	def _db_apply_sort_filter(query, sort_criteria):
	#
		"""
Apply the filter to the given SQLAlchemy query instance.

:param query: SQLAlchemy query instance
:param sort_criteria: DIDL sort criteria

:return: (object) Modified SQLAlchemy query instance
:since:  v0.1.00
		"""

		_return = query.order_by(_DbMpUpnpResource.cds_type.asc())

		if (sort_criteria is None): criteria_list = [ ]
		else: criteria_list = (sort_criteria if (type(sort_criteria) is list) else sort_criteria.split(","))

		for criteria in criteria_list:
		#
			criteria_first_char = criteria[:1]
			if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]

			if (criteria == "dc:date" or criteria == "upnp:recordedStartDateTime"):
			#
				_return = _return.order_by(_DbDataLinkerMeta.time_sortable.desc()
				                           if (criteria_first_char == "-") else
				                           _DbDataLinkerMeta.time_sortable.asc()
				                          )
			#
			elif (criteria == "dc:title"):
			#
				_return = _return.order_by(_DbDataLinkerMeta.title.desc()
				                           if (criteria_first_char == "-") else
				                           _DbDataLinkerMeta.title.asc()
				                          )
		#

		return _return
	#

	@staticmethod
	def get_root_containers_count():
	#
		"""
Returns the count of root container MpEntry entries.

:return: (int) Number of MpEntry entries
:since:  v0.1.00
		"""

		with Connection.get_instance() as connection:
		#
			db_query = (connection.query(sql_count(_DbMpUpnpResource.id))
			            .filter(_DbMpUpnpResource.cds_type == _DbMpUpnpResource.CDS_TYPE_ROOT)
			           )

			return db_query.scalar()
		#
	#

	@staticmethod
	def load_encapsulating_entry(_id, client_user_agent = None, cds = None, deleted = False):
	#
		"""
Loads a matching MpEntry for the given UPnP CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.00
		"""

		if (_id is None): raise TypeException("Encapsulated ID is invalid")
		_return = None

		if (_id == "mp-entry" or _id.startswith("mp-entry-")): _return = MpEntry.load_cds_id(_id, client_user_agent, cds, deleted)
		else:
		#
			resource = Resource.load_cds_id(_id, client_user_agent, cds, deleted)
			mimeclass = (None if (resource is None) else resource.get_mimeclass())

			if (mimeclass is not None):
			#
				if (mimeclass == "directory"): entry_class_name = "dNG.pas.data.upnp.resources.MpEntry"
				else:
				#
					camel_case_mimeclass = "".join([word.capitalize() for word in re.split("\\W", mimeclass.split("/")[0])])
					entry_class_name = "dNG.pas.data.upnp.resources.MpEntry{0}".format(camel_case_mimeclass)

					if (not NamedLoader.is_defined(entry_class_name)): entry_class_name = "dNG.pas.data.upnp.resources.MpEntry"
				#

				_return = NamedLoader.get_instance(entry_class_name, False)
				if (_return is not None and (not _return.init_cds_id(_id, client_user_agent, deleted))): _return = None
			#
		#

		return _return
	#

	@classmethod
	def load_resource(cls, resource, client_user_agent = None, cds = None, deleted = False):
	#
		"""
Loads the matching MpEntry for the given UPnP resource.

:param cls: Expected encapsulating database instance class
:param resource: UPnP resource
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.02
		"""

		if (resource is None): raise NothingMatchedException("UPnP resource is invalid")

		with Connection.get_instance():
		#
			db_instance = (DataLinker.get_db_class_query(cls)
			               .filter(_DbMpUpnpResource.resource == resource)
			               .first()
			              )

			if (db_instance is None): raise NothingMatchedException("UPnP resource '{0}' is invalid".format(resource))
			DataLinker._ensure_db_class(cls, db_instance)

			return MpEntry(db_instance)
		#
	#

	@staticmethod
	def load_root_containers(sort_criteria = "+dc:title", offset = 0, limit = -1):
	#
		"""
Loads a list of UPnP root container MpEntry instances.

:param sort_criteria: UPnP sort criteria
:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) List of MpEntry instances on success
:since:  v0.1.00
		"""

		with Connection.get_instance() as connection:
		#
			db_query = (connection.query(_DbMpUpnpResource)
			            .filter(_DbMpUpnpResource.cds_type == _DbMpUpnpResource.CDS_TYPE_ROOT)
			            .join(_DbMpUpnpResource.rel_meta)
			           )

			result = connection.execute(MpEntry._db_apply_sort_filter(db_query, sort_criteria))

			if (offset > 0): db_query = db_query.offset(offset)
			if (limit > 0): db_query = db_query.limit(limit)

			return ([ ] if (result is None) else MpEntry.buffered_iterator(_DbMpUpnpResource, result))
		#
	#
#

##j## EOF