# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.MpEntry
"""
"""n// NOTE
----------------------------------------------------------------------------
MediaProvider
A device centric multimedia solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?mp;core

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
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

# pylint: disable=import-error,no-name-in-module

from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql.functions import count as sql_count
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.binary import Binary
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.connection import Connection
from dNG.pas.database.sort_definition import SortDefinition
from dNG.pas.database.instances.data_linker_meta import DataLinkerMeta as _DbDataLinkerMeta
from dNG.pas.database.instances.key_store import KeyStore as _DbKeyStore
from dNG.pas.database.instances.mp_upnp_resource import MpUpnpResource as _DbMpUpnpResource
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from dNG.pas.runtime.value_exception import ValueException

class MpEntry(Resource, DataLinker):
#
	"""
"MpEntry" represents an database resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	TYPE_CDS_CONTAINER_AUDIO = 8
	"""
UPnP CDS audio container type
	"""
	TYPE_CDS_CONTAINER_IMAGE = 16
	"""
UPnP CDS image container type
	"""
	TYPE_CDS_CONTAINER_VIDEO = 32
	"""
UPnP CDS video container type
	"""
	TYPE_CDS_ITEM_AUDIO = 64
	"""
UPnP CDS audio item type
	"""
	TYPE_CDS_ITEM_IMAGE = 128
	"""
UPnP CDS image item type
	"""
	TYPE_CDS_ITEM_VIDEO = 256
	"""
UPnP CDS video item type
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

		if (isinstance(self.local.db_instance, _DbMpUpnpResource)):
		#
			with Connection.get_instance():
			#
				self._load()

				if (user_agent != None): self.client_set_user_agent(user_agent)
				if (didl_fields != None): self.set_didl_fields(didl_fields)
			#
		#

		self.supported_features['content_search'] = self._supports_content_search
	#

	def content_add(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member

		_return = False

		if (isinstance(resource, MpEntry) and resource.get_type() != None):
		#
			with self, self.lock:
			#
				matched_entry = self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id)).filter(_DbMpUpnpResource.resource == resource.get_encapsulated_id()).scalar()

				if (matched_entry < 1):
				#
					self.object_add(resource)
					self.set_update_id("++")
				#
			#

			_return = True
		#

		return _return
	#

	def content_remove(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member

		_return = False

		if (isinstance(resource, MpEntry) and resource.get_type() != None):
		#
			with self, self.lock:
			#
				matched_entry = self.local.db_instance.rel_children.from_self(sql_count(_DbMpUpnpResource.id)).filter(_DbMpUpnpResource.resource == resource.get_encapsulated_id()).scalar()

				if (matched_entry > 0):
				#
					self.object_remove(resource)
					self.set_update_id("--")

					_return = True
				#
			#
		#

		return _return
	#

	def content_get(self, position):
	#
		"""
Returns the UPnP content resource at the given position.

:param position: Position of the UPnP content resource to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.1.01
		"""

		_return = [ ]

		if (self.local.db_instance == None): raise ValueException("Database instance is not correctly initialized")

		if (self.encapsulated_resource == None):
		#
			child_position = (position if (self.content_offset == None or self.content_offset < 1) else (position - self.content_offset))
			children = self.content_get_list()

			if (len(children) < child_position): raise ValueException("UPnP content position out of range")
			_return = children[child_position]
		#
		else: _return = self.encapsulated_resource.content_get(position)

		return _return
	#

	def content_get_list(self):
	#
		"""
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member,protected-access

		_return = [ ]

		if (self.local.db_instance == None): raise ValueException("Database instance is not correctly initialized")

		if (self.encapsulated_resource == None):
		#
			if (self.type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER):
			#
				with self:
				#
					db_query = self.local.db_instance.rel_mp_upnp_resource_children.join(_DbMpUpnpResource.rel_meta)
					children_length = self.local.db_instance.rel_meta.objects

					if (children_length > 0):
					#
						db_query = self._db_apply_sort_definition(db_query)

						child_first = (0 if (self.content_offset == None or self.content_offset >= children_length) else self.content_offset)
						child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
						if (child_last == None or child_last >= children_length): child_last = children_length

						if (child_first > 0): db_query = db_query.offset(child_first)
						if (child_first <= child_last): db_query = db_query.limit(child_last - child_first)

						_return = MpEntry.buffered_iterator(_DbMpUpnpResource, self._database.execute(db_query), MpEntry, self.client_user_agent, self.didl_fields)
					#
				#
			#
			elif (self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
			#
				encapsulated_resource = self.load_encapsulated_resource()
				resource_stream = (None if (encapsulated_resource == None) else encapsulated_resource._get_stream_resource())

				if (resource_stream != None):
				#
					resource_stream.init_cds_id(encapsulated_resource.get_id(), self.client_user_agent)
					resource_stream.set_parent_id(self.get_id())
					if (isinstance(resource_stream, AbstractStream) and resource_stream.is_supported("metadata")): resource_stream.set_metadata(size = self.get_size())
					_return = [ resource_stream ]
				#
				elif (self.log_handler != None): self.log_handler.warning("mp.MpEntry failed to load resource stream for ID '{0}'".format(self.id))
			#
		#
		else: _return = self.encapsulated_resource.content_get_list()

		return _return
	#

	def content_get_list_of_type(self, _type = None):
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

		if (db_type == None): _return = self.content_get_list()
		elif (self.encapsulated_resource != None): _return = self.encapsulated_resource.content_get_list_of_type(_type)
		else:
		#
			with self:
			#
				db_query = self.local.db_instance.rel_mp_upnp_resource_children.filter(_DbMpUpnpResource.cds_type == db_type).join(_DbMpUpnpResource.rel_meta)
				_return = [ ]
				children_length = self.local.db_instance.rel_meta.objects

				if (children_length > 0):
				#
					db_query = self._db_apply_sort_definition(db_query)

					child_first = (0 if (self.content_offset == None or self.content_offset >= children_length) else self.content_offset)
					child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
					if (child_last == None or child_last >= children_length): child_last = children_length

					if (child_first > 0): db_query = db_query.offset(child_first)
					if (child_first <= child_last): db_query = db_query.limit(1 + child_last - child_first)

					_return = MpEntry.buffered_iterator(_DbMpUpnpResource, self._database.execute(db_query), MpEntry, self.client_user_agent, self.didl_fields)
				#
			#
		#

		return _return
	#

	def content_get_didl_xml(self):
	#
		"""
Returns an UPnP DIDL result of generated XML for all contained UPnP content
resources.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		with self: return Resource.content_get_didl_xml(self)
	#

	def _content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		raise NotImplementedException()
	#

	def _data_get_unknown(self, attribute):
	#
		"""
Return the data for the requested attribute not defined for this instance.

:param attribute: Requested attribute

:return: (dict) Value for the requested attribute
:since:  v0.1.00
		"""

		return (self.local.db_instance.rel_resource_metadata.value if (attribute == "metadata" and self.local.db_instance.rel_resource_metadata != None) else DataLinker._data_get_unknown(self, attribute))
	#

	def data_set(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		if (self.local.db_instance == None): self.local.db_instance = _DbMpUpnpResource()

		with self:
		#
			DataLinker.data_set(self, **kwargs)

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
				is_empty = (kwargs['metadata'] == None or kwargs['metadata'].strip() == "")

				if (self.local.db_instance.rel_resource_metadata == None):
				#
					self.local.db_instance.rel_resource_metadata = _DbKeyStore()
					self.local.db_instance.rel_resource_metadata.key = self.local.db_instance.id
				#
				elif (is_empty): del(self.local.db_instance.rel_resource_metadata)

				if (not is_empty): self.local.db_instance.rel_resource_metadata.value = kwargs['metadata']
			#
		#
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:return: (bool) True on success
:since:  v0.1.00
		"""

		_return = False

		with self:
		#
			self._database.begin()

			try:
			#
				_return = True

				if (self.type & MpEntry.TYPE_CDS_CONTAINER == MpEntry.TYPE_CDS_CONTAINER):
				#
					for entry in self.content_get_list():
					#
						_return = entry.delete()
						if (not _return): break
					#
				#

				db_resource_metadata_instance = self.local.db_instance.rel_resource_metadata

				if (_return): _return = DataLinker.delete(self)

				if (
					_return and
					db_resource_metadata_instance != None
				): self._database.delete(db_resource_metadata_instance)

				if (_return): self._database.commit()
				else: self._database.rollback()
			#
			except Exception:
			#
				self._database.rollback()
				raise
			#
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
		if (_return == None and self.encapsulated_resource != None): _return = self.encapsulated_resource.get_mimeclass()

		if (_return == None):
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

		if (_return == None): _return = "unknown"
		return _return
	#

	def get_encapsulated_id(self):
	#
		"""
Returns the ID of the encapsulated resource.

		"""

		return self.encapsulated_id
	#

	def get_encapsulated_resource(self):
	#
		"""
Returns the encapsulated resource if used to create the UPnP resource.

		"""

		return self.encapsulated_resource
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.1.00
		"""

		if (self.encapsulated_resource == None):
		#
			with self: _return = self.local.db_instance.rel_meta.time_sortable
		#
		else: _return = self.encapsulated_resource.get_timestamp()

		return _return
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.1.00
		"""

		if (self.encapsulated_resource == None):
		#
			with self: _return = self.local.db_instance.rel_meta.objects
		#
		else: _return = self.encapsulated_resource.get_total()

		return _return
	#

	def get_type(self):
	#
		"""
Returns the UPnP resource type.

:return: (str) UPnP resource type; None if empty
:since:  v0.1.01
		"""

		if (self.type == None):
		#
			entry_data = self.data_get("cds_type")

			if (entry_data['cds_type'] == _DbMpUpnpResource.CDS_TYPE_ITEM):
			#
				_return = MpEntry.TYPE_CDS_ITEM

				if (self.mimeclass != None): mimeclass = self.mimeclass
				elif (self.encapsulated_resource != None): mimeclass = self.encapsulated_resource.get_mimeclass()
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

	def get_type_class(self):
	#
		"""
Returns the UPnP resource type class.

:return: (str) UPnP resource type class; None if unknown
:since:  v0.1.00
		"""

		_return = None

		is_cds1_container_supported = False
		is_cds1_object_supported = False
		_type = self.get_type()

		if (_type != None):
		#
			client = Client.load_user_agent(self.client_user_agent)
			is_cds1_container_supported = client.get("upnp_didl_cds1_container_classes_supported", True)
			is_cds1_object_supported = client.get("upnp_didl_cds1_object_classes_supported", True)
		#

		if (is_cds1_container_supported):
		#
			if (_type & MpEntry.TYPE_CDS_CONTAINER_AUDIO == MpEntry.TYPE_CDS_CONTAINER_AUDIO): _return = "object.container.genre.musicGenre"
			elif (_type & MpEntry.TYPE_CDS_CONTAINER_IMAGE == MpEntry.TYPE_CDS_CONTAINER_IMAGE): _return = "object.container.album.photoAlbum"
			elif (_type & MpEntry.TYPE_CDS_CONTAINER_VIDEO == MpEntry.TYPE_CDS_CONTAINER_VIDEO): _return = "object.container.genre.movieGenre"
		#

		if (is_cds1_object_supported):
		#
			if (_type & MpEntry.TYPE_CDS_ITEM_AUDIO == MpEntry.TYPE_CDS_ITEM_AUDIO): _return = "object.item.audioItem.musicTrack"
			elif (_type & MpEntry.TYPE_CDS_ITEM_IMAGE == MpEntry.TYPE_CDS_ITEM_IMAGE): _return = "object.item.imageItem.photo"
			elif (_type & MpEntry.TYPE_CDS_ITEM_VIDEO == MpEntry.TYPE_CDS_ITEM_VIDEO): _return = "object.item.videoItem.movie"
		#

		if (_return == None): _return = Resource.get_type_class(self)
		return _return
	#

	def init_cds_id(self, _id, client_user_agent = None, update_id = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		Resource.init_cds_id(self, _id, client_user_agent, update_id, deleted)
		_return = (self.id != None)

		if (_return):
		#
			url_elements = urlsplit(self.id)

			if (url_elements.scheme == "mp-entry" or url_elements.scheme.startswith("mp-entry-")):
			#
				if (self.local.db_instance == None):
				#
					with Connection.get_instance() as database: self.local.db_instance = database.query(_DbMpUpnpResource).filter(_DbMpUpnpResource.id == url_elements.path[1:]).first()
				#

				if (self.local.db_instance == None): _return = False
				else: self._load()
			#
			else:
			#
				self.encapsulated_resource = Resource.load_cds_id(_id, deleted = True)

				if (self.encapsulated_resource == None): _return = False
				else:
				#
					self.encapsulated_id = self.encapsulated_resource.get_id()

					if (self.local.db_instance == None):
					#
						with Connection.get_instance() as database:
						#
							self.local.db_instance = database.query(_DbMpUpnpResource).filter(_DbMpUpnpResource.resource == self.encapsulated_id).first()

							if (self.local.db_instance == None): self._init_encapsulated_resource()
							else:
							#
								self.id = None
								self._load()
								_return = (self.id != None)
							#
						#
					#

					self.updatable = self.encapsulated_resource.get_updatable()
				#
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

		if (self.encapsulated_resource == None): raise ValueException("Encapsulated resource not accessible")
		if (self.local.db_instance == None): self.local.db_instance = _DbMpUpnpResource()

		self.id = self.encapsulated_resource.get_id()
		self.name = self.encapsulated_resource.get_name()
		self.mimeclass = self.encapsulated_resource.get_mimeclass()
		self.mimetype = self.encapsulated_resource.get_mimetype()
		self.source = "MediaProvider"
		self.type = self.encapsulated_resource.get_type()

		db_type = (
			_DbMpUpnpResource.CDS_TYPE_ITEM
			if (self.encapsulated_resource.get_type() & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM) else
			_DbMpUpnpResource.CDS_TYPE_CONTAINER
		)

		self.data_set(
			title = self.name,
			cds_type = db_type,
			mimeclass = self.mimeclass,
			mimetype = self.mimetype,
			resource_type = NamedLoader.RE_CAMEL_CASE_SPLITTER.sub("\\1-\\2", self.__class__.__name__).lower(),
			resource_title = self.name,
			resource = self.encapsulated_id
		)
	#

	def _insert(self):
	#
		"""
Insert the instance into the database.

:since: v0.1.00
		"""

		# pylint: disable=maybe-no-member

		DataLinker._insert(self)

		with self, self._database.no_autoflush:
		#
			if (self.local.db_instance.mimeclass == "directory"):
			#
				parent_object = self.load_parent()

				if (
					parent_object != None and
					isinstance(parent_object, _DbMpUpnpResource) and
					parent_object.mimetype != None
				): self.local.db_instance.mimetype = parent_object.mimetype
			#
		#
	#

	def is_encapsulated_resource(self, _id):
	#
		"""
Returns true if the given ID identifies this resource or the contained one.

:param _id: ID

:return: (bool) True if successful
:since:  v0.1.00
		"""

		return (_id == self.id or _id == self.encapsulated_id)
	#

	def _load(self):
	#
		"""
Load a matching MpEntry for the given UPnP CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.00
		"""

		with self:
		#
			entry_data = self.data_get("id", "title", "mimeclass", "mimetype", "resource_type", "resource_title", "resource", "size")

			self.name = entry_data['title']
			self.mimeclass = entry_data['mimeclass']
			self.mimetype = entry_data['mimetype']
			self.resource_title = entry_data['resource_title']
			self.encapsulated_id = entry_data['resource']
			self.size = entry_data['size']
			self.source = "MediaProvider"
			self.type = self.get_type()
			self.updatable = True

			if (entry_data['resource_type'] == "mp-entry" or entry_data['resource_type'].startswith("mp-entry-")):
			#
				if (self.id == None): self.id = "{0}:///{1}".format(entry_data['resource_type'], entry_data['id'])
			#
			else:
			#
				self.encapsulated_resource = Resource.load_cds_id(self.encapsulated_id, self.client_user_agent)
				if (self.id == None): self.id = self.encapsulated_id

				if (self.encapsulated_resource != None):
				#
					self.encapsulated_resource.set_didl_fields(self.didl_fields)
					self.encapsulated_resource.set_sort_criteria(self.sort_criteria)
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

		return Resource.load_cds_id(self.get_encapsulated_id(), self.client_user_agent, deleted = deleted)
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
			_return = (None if (db_parent_instance == None or (not isinstance(db_parent_instance, _DbMpUpnpResource))) else MpEntry(db_parent_instance))
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
		if (encapsulated_resource == None): raise ValueException("Encapsulated resource not accessible")

		self.data_set(
			mimeclass = encapsulated_resource.get_mimeclass(),
			mimetype = encapsulated_resource.get_mimetype(),
			refreshable = False,
			time_sortable = encapsulated_resource.get_timestamp(),
			size = encapsulated_resource.get_size()
		)
	#

	def save(self):
	#
		"""
Saves changes of the MpEntry into the database. Encapsulated resources
used for "init_cds_id()" will be cleared.

:since: v0.1.00
		"""

		DataLinker.save(self)

		with self.lock:
		#
			if (self.encapsulated_resource != None):
			#
				self.encapsulated_resource = None
				self.id = "{0}:///{1}".format(self.local.db_instance.resource_type, self.local.db_instance.id)
			#
		#
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

	def set_sort_criteria(self, sort_criteria):
	#
		"""
Sets the DIDL fields to be returned.

:param fields: DIDL fields list

:since: v0.1.01
		"""

		Resource.set_sort_criteria(self, sort_criteria)

		sort_definition = SortDefinition([ ( "cds_type", SortDefinition.ASCENDING ) ])

		criteria_list = ([ "+dc:title" ] if (len(self.sort_criteria) < 1) else self.sort_criteria)

		for criteria in criteria_list:
		#
			criteria_first_char = criteria[:1]
			if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]

			self.__class__._db_append_didl_field_sort_definition(
				sort_definition,
				criteria,
				(SortDefinition.ASCENDING if (criteria_first_char == "+") else SortDefinition.DESCENDING)
			)

			self._db_sort_tuples = sort_definition.get_list()
		#
	#

	def _supports_content_search(self):
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

		_return = query.order_by(asc(_DbMpUpnpResource.cds_type))

		if (sort_criteria == None): criteria_list = [ ]
		else: criteria_list = (sort_criteria if (type(sort_criteria) == list) else sort_criteria.split(","))

		for criteria in criteria_list:
		#
			criteria_first_char = criteria[:1]
			if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]

			if (criteria == "dc:date" or criteria == "upnp:recordedStartDateTime"): _return = _return.order_by(desc(_DbDataLinkerMeta.time_sortable) if (criteria_first_char == "-") else asc(_DbDataLinkerMeta.time_sortable))
			elif (criteria == "dc:title"): _return = _return.order_by(desc(_DbDataLinkerMeta.title) if (criteria_first_char == "-") else asc(_DbDataLinkerMeta.title))
		#

		return _return
	#

	@staticmethod
	def load_encapsulating_entry(_id, client_user_agent = None, cds = None, deleted = False):
	#
		"""
Load a matching MpEntry for the given UPnP CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.00
		"""

		_return = None

		resource = Resource.load_cds_id(_id, client_user_agent, cds, deleted)
		mimeclass = (None if (resource == None) else resource.get_mimeclass())

		if (mimeclass != None):
		#
			if (mimeclass == "directory"): entry_class_name = "dNG.pas.data.upnp.resources.MpEntry"
			else:
			#
				entry_class_name = "dNG.pas.data.upnp.resources.MpEntry{0}".format("".join([word.capitalize() for word in re.split("\\W", mimeclass.split("/")[0])]))
				if (not NamedLoader.is_defined(entry_class_name)): entry_class_name = "dNG.pas.data.upnp.resources.MpEntry"
			#

			_return = NamedLoader.get_instance(entry_class_name, False)
			if (_return != None and (not _return.init_cds_id(_id, client_user_agent, cds, deleted))): _return = None
		#

		return _return
	#

	@staticmethod
	def load_root_containers(sort_criteria = "+dc:title"):
	#
		with Connection.get_instance() as database:
		#
			result = database.execute(MpEntry._db_apply_sort_filter(database.query(_DbMpUpnpResource).filter(_DbMpUpnpResource.cds_type == _DbMpUpnpResource.CDS_TYPE_ROOT).join(_DbMpUpnpResource.rel_meta), sort_criteria))
			return ([ ] if (result == None) else MpEntry.buffered_iterator(_DbMpUpnpResource, result, MpEntry))
		#
	#
#

##j## EOF