# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.vpmc_entry
"""
"""n// NOTE
----------------------------------------------------------------------------
Video's place (media center edition)
A device centric multimedia solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?vpmc;core

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
#echo(vpmcCoreVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql.functions import count as sql_count
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.database.connection import Connection
from dNG.pas.database.instances.data_linker_meta import DataLinkerMeta
from dNG.pas.database.instances.vpmc_upnp_resource import VpmcUpnpResource
from dNG.pas.module.named_loader import NamedLoader

class VpmcEntry(Resource, DataLinker):
#
	"""
"VpmcResource" represents an database resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	DB_TYPE_CONTAINER = VpmcUpnpResource.DB_TYPE_CONTAINER
	"""
Database container entry
	"""
	DB_TYPE_ITEM = VpmcUpnpResource.DB_TYPE_ITEM
	"""
Database item entry
	"""
	DB_TYPE_ROOT = VpmcUpnpResource.DB_TYPE_ROOT
	"""
Database root container entry
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
UPnP CDS bookmark container type
	"""
	TYPE_CDS_ITEM_IMAGE = 128
	"""
UPnP CDS bookmark container type
	"""
	TYPE_CDS_ITEM_VIDEO = 256
	"""
UPnP CDS bookmark container type
	"""

	def __init__(self, db_instance = None, user_agent = None, didl_fields = None):
	#
		"""
Constructor __init__(Resource)

:param user_agent: Client user agent
:param fields: DIDL fields list

:since: v0.1.00
		"""

		Resource.__init__(self)

		DataLinker.__init__(self, db_instance)

		self.encapsulated_resource = None
		"""
UPnP resource audio bits per sample
		"""
		self.path = None
		"""
UPnP resource audio bits per sample
		"""

		if (isinstance(self.local.db_instance, VpmcUpnpResource)):
		#
			entry_data = self.data_get("title", "resource", "mime_type")

			self.id = entry_data['resource']
			self.name = entry_data['title']
			self.mime_type = entry_data['mime_type']
			self.source = "video's place (media center)"
			self.type = self.get_type()
			self.updatable = True

			if (user_agent != None): self.client_set_user_agent(user_agent)
			if (didl_fields != None): self.set_didl_fields(didl_fields)
		#
	#

	def content_add(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		_return = False

		if (isinstance(resource, Resource) and resource.get_type() != None):
		#
			with self.synchronized:
			#
				with self:
				#
					matched_entry = self.local.db_instance.rel_children.from_self(sql_count(VpmcUpnpResource.id)).filter(VpmcUpnpResource.resource == resource.get_id()).scalar()

					if (matched_entry < 1):
					#
						self.object_add(resource)
						self.set_update_id("++")
					#
				#

				_return = True
			#
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

		_return = False

		if (isinstance(resource, Resource) and resource.get_type() != None):
		#
			with self.synchronized:
			#
				with self:
				#
					matched_entry = self.local.db_instance.rel_children.from_self(sql_count(VpmcUpnpResource.id)).filter(VpmcUpnpResource.resource == resource.get_id()).scalar()

					if (matched_entry > 0):
					#
						self.object_remove(resource)
						self.set_update_id("--")

						_return = True
					#
				#
			#
		#

		return _return
	#

	def content_get(self, position = None):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		_return = None

		if (self.local.db_instance == None): raise RuntimeError("Database instance is not correctly initialized", 22)

		if (self.encapsulated_resource != None): encapsulated_resource = self.encapsulated_resource
		else: encapsulated_resource = (self.get_encapsulated_resource() if (self.type & VpmcEntry.TYPE_CDS_ITEM == VpmcEntry.TYPE_CDS_ITEM) else None)

		if (encapsulated_resource == None):
		#
			with self:
			#
				db_query = self.local.db_instance.rel_children.join(VpmcUpnpResource.rel_meta)
				self.content = [ ]
				children_length = self.local.db_instance.rel_meta.objects

				if (children_length > 0):
				#
					db_query = VpmcEntry._db_apply_sort_order(db_query, "+dc:title")

					child_first = (0 if (self.content_offset == None or self.content_offset >= children_length) else self.content_offset)
					child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
					if (child_last == None or child_last >= children_length): child_last = children_length

					if (child_first > 0): db_query = db_query.offset(child_first)
					if (child_first <= child_last): db_query = db_query.limit(child_last - child_first)

					_return = list(VpmcEntry.iterator(VpmcUpnpResource, self._connection.execute(db_query), VpmcEntry))
				#
				else: _return = [ ]
			#
		#
		else: _return = encapsulated_resource.content_get()

		return _return
	#

	def content_get_type(self, _type = None):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		if (_type & VpmcEntry.TYPE_CDS_CONTAINER == VpmcEntry.TYPE_CDS_CONTAINER): db_type = VpmcUpnpResource.DB_TYPE_CONTAINER
		elif (_type & VpmcEntry.TYPE_CDS_ITEM == VpmcEntry.TYPE_CDS_ITEM): db_type = VpmcUpnpResource.DB_TYPE_ITEM
		else: db_type = None

		if (db_type == None): _return = self.content_get()
		elif (self.encapsulated_resource != None): _return = self.encapsulated_resource.content_get_type(_type)
		else:
		#
			with self:
			#
				db_query = self.local.db_instance.rel_children.filter(VpmcUpnpResource.type == db_type).join(VpmcUpnpResource.rel_meta)
				_return = [ ]
				children_length = self.local.db_instance.rel_meta.objects

				if (children_length > 0):
				#
					db_query = VpmcEntry._db_apply_sort_order(db_query, "+dc:title")

					child_first = (0 if (self.content_offset == None or self.content_offset >= children_length) else self.content_offset)
					child_last = (self.content_limit if (child_first < 1) else self.content_offset + self.content_limit)
					if (child_last == None or child_last >= children_length): child_last = children_length

					if (child_first > 0): db_query = db_query.offset(child_first)
					if (child_first <= child_last): db_query = db_query.limit(1 + child_last - child_first)

					_return = list(VpmcEntry.iterator(VpmcUpnpResource, self._connection.execute(db_query), VpmcEntry, self.client_user_agent, self.didl_fields))
				#
			#
		#

		return _return
	#

	def _content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		raise RuntimeError("Not implemented", 38)
	#

	def data_set(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		if (self.local.db_instance == None): self.local.db_instance = VpmcUpnpResource()

		with self:
		#
			DataLinker.data_set(self, **kwargs)

			if ("mime_type" in kwargs): self.local.db_instance.mime_type = kwargs['mime_type']
			if ("resource" in kwargs): self.local.db_instance.resource = kwargs['resource']
		#
	#

	def get_encapsulated_id(self):
	#
		"""
Returns the ID of the encapsulated resource.

		"""

		with self: url_elements = urlsplit(self.local.db_instance.resource)
		return "{0}:///{1}".format(url_elements.netloc, url_elements.path[1:])
	#

	def get_encapsulated_resource(self):
	#
		"""
Returns the ID of the encapsulated resource.

		"""

		return Resource.load_cds_id(self.get_encapsulated_id(), self.client_user_agent)
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
			with self: _return = self.local.db_instance.rel_meta.sorting_date
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
			entry_data = self.data_get("type")

			if (entry_data['type'] == VpmcEntry.DB_TYPE_ITEM):
			#
				entry_type = self.mime_type.split("/")[0]

				if (entry_type == "audio"): _return = VpmcEntry.TYPE_CDS_ITEM_AUDIO | VpmcEntry.TYPE_CDS_ITEM
				elif (entry_type == "image"): _return = VpmcEntry.TYPE_CDS_ITEM_IMAGE | VpmcEntry.TYPE_CDS_ITEM
				elif (entry_type == "video"): _return = VpmcEntry.TYPE_CDS_ITEM_VIDEO | VpmcEntry.TYPE_CDS_ITEM
				else: _return = VpmcEntry.TYPE_CDS_ITEM
			#
			elif (self.mime_type == "text/x-directory-upnp-audio"): _return = VpmcEntry.TYPE_CDS_CONTAINER | VpmcEntry.TYPE_CDS_CONTAINER_AUDIO
			elif (self.mime_type == "text/x-directory-upnp-image"): _return = VpmcEntry.TYPE_CDS_CONTAINER | VpmcEntry.TYPE_CDS_CONTAINER_IMAGE
			elif (self.mime_type == "text/x-directory-upnp-video"): _return = VpmcEntry.TYPE_CDS_CONTAINER | VpmcEntry.TYPE_CDS_CONTAINER_VIDEO
			else: _return = VpmcEntry.TYPE_CDS_CONTAINER

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

		if (self.type == None): is_supported = False
		else:
		#
			client = Client.load_user_agent(self.client_user_agent)
			is_supported = (True if (client == None or client.get("upnp_didl_cds1_classes_supported", True)) else False)
		#

		if (is_supported):
		#
			if (self.type & VpmcEntry.TYPE_CDS_CONTAINER_AUDIO == VpmcEntry.TYPE_CDS_CONTAINER_AUDIO): _return = "object.container.genre.musicGenre"
			elif (self.type & VpmcEntry.TYPE_CDS_CONTAINER_IMAGE == VpmcEntry.TYPE_CDS_CONTAINER_IMAGE): _return = "object.container.album.photoAlbum"
			elif (self.type & VpmcEntry.TYPE_CDS_CONTAINER_VIDEO == VpmcEntry.TYPE_CDS_CONTAINER_VIDEO): _return = "object.container.genre.movieGenre"
			elif (self.type & VpmcEntry.TYPE_CDS_ITEM_AUDIO == VpmcEntry.TYPE_CDS_ITEM_AUDIO): _return = "object.item.audioItem.musicTrack"
			elif (self.type & VpmcEntry.TYPE_CDS_ITEM_IMAGE == VpmcEntry.TYPE_CDS_ITEM_IMAGE): _return = "object.item.imageItem.photo"
			elif (self.type & VpmcEntry.TYPE_CDS_ITEM_VIDEO == VpmcEntry.TYPE_CDS_ITEM_VIDEO): _return = "object.item.videoItem.movie"
		#

		if (_return == None): _return = Resource.get_type_class(self)
		return _return
	#

	def init_cds_id(self, _id, client_user_agent = None, update_id = None):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		_return = Resource.init_cds_id(self, _id, client_user_agent, update_id)

		url_elements = urlsplit(self.id)

		if (url_elements.scheme == "vpmc-entry"):
		#
			if (self.local.db_instance == None):
			#
				with Connection.get_instance() as database: self.local.db_instance = database.query(VpmcUpnpResource).filter(VpmcUpnpResource.resource == self.id).first()
			#

			if (self.local.db_instance != None):
			#
				with self:
				#
					entry_data = self.data_get("title", "mime_type")

					self.name = entry_data['title']
					self.mime_type = entry_data['mime_type']
					self.source = "video's place (media center)"
					self.type = self.get_type()
					self.updatable = True

					_return = True
				#
			#
		#
		elif (url_elements.netloc == ""):
		#
			self.encapsulated_resource = Resource.load_cds_id(self.id, client_user_agent)

			if (self.encapsulated_resource != None):
			#
				self.id = "vpmc-entry://{0}{1}".format(url_elements.scheme, url_elements.path)
				if (url_elements.query != ""): self.id = "{0}?{1}".format(self.id, url_elements.query)
				if (url_elements.fragment != ""): self.id = "{0}#{1}".format(self.id, url_elements.fragment)

				if (self.local.db_instance == None):
				#
					with Connection.get_instance() as database:
					#
						self.local.db_instance = database.query(VpmcUpnpResource).filter(VpmcUpnpResource.resource == self.id).first()

						if (self.local.db_instance == None):
						#
							self.local.db_instance = VpmcUpnpResource()

							self.name = self.encapsulated_resource.get_name()
							self.mime_type = self.encapsulated_resource.get_mime_type()
							self.type = self.encapsulated_resource.get_type()

							db_type = (VpmcEntry.DB_TYPE_ITEM if (self.encapsulated_resource.get_type() & VpmcEntry.TYPE_CDS_ITEM == VpmcEntry.TYPE_CDS_ITEM) else VpmcEntry.DB_TYPE_CONTAINER)

							self.data_set(
								type = db_type,
								title = self.name,
								mime_type = self.mime_type,
								resource = self.id
							)
						#
						else:
						#
							entry_data = self.data_get("title", "mime_type")

							self.name = entry_data['title']
							self.mime_type = entry_data['mime_type']
							self.type = self.get_type()
						#
					#
				#

				self.source = "video's place (media center)"
				self.updatable = self.encapsulated_resource.get_updatable()

				_return = True
			#
		#

		return _return
	#

	def _insert(self):
	#
		"""
Insert the instance into the database.

:param count: Count "get()" request

:since: v0.1.00
		"""

		DataLinker._insert(self)

		with self:
		#
			if (self.local.db_instance.mime_type == "text/directory" and isinstance(self.local.db_instance.rel_parent, VpmcUpnpResource)):
			#
				if (self.local.db_instance.rel_parent.mime_type != None): self.local.db_instance.mime_type = self.local.db_instance.rel_parent.mime_type
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

		if (_id == self.id): _return = True
		else:
		#
			url_elements = urlsplit(self.id)
			_return = (url_elements.scheme == "vpmc-entry" and url_elements.netloc != "" and _id == "{0}:///{1}".format(url_elements.netloc, url_elements.path[1:]))
		#

		return _return
	#

	def load_parent(self):
	#
		"""
Load the parent instance.

:return: (object) Parent VpmcEntry instance
:since:  v0.1.00
		"""

		with self:
		#
			db_parent_instance = self.local.db_instance.rel_parent
			_return = (None if (db_parent_instance == None or (not isinstance(db_parent_instance, VpmcUpnpResource))) else VpmcEntry(db_parent_instance))
		#

		return _return
	#

	def save(self):
	#
		"""
Saves changes of the VpmcEntry into the database. Encapsulated resources
used for "init_cds_id()" will be cleared.

:since: v0.1.00
		"""

		if (DataLinker.save(self)): self.encapsulated_resource = None
	#

	@staticmethod
	def _db_apply_sort_order(query, _filter):
	#
		_return = query.order_by(asc(VpmcUpnpResource.type))

		filters = ([ ] if (_filter == None) else _filter.split(","))

		for _filter in filters:
		#
			filter_first_char = _filter[:1]
			if (filter_first_char == "+" or filter_first_char == "-"): _filter = _filter[1:]

			if (_filter == "dc:date"): _return = _return.order_by(desc(DataLinkerMeta.sorting_date) if (filter_first_char == "-") else asc(DataLinkerMeta.sorting_date))
			elif (_filter == "dc:title"): _return = _return.order_by(desc(DataLinkerMeta.title) if (filter_first_char == "-") else asc(DataLinkerMeta.title)).order_by(asc(VpmcUpnpResource.title_alt))
			elif (_filter == "upnp:recordedStartDateTime"): _return = _return.order_by(desc(DataLinkerMeta.sorting_date) if (filter_first_char == "-") else asc(DataLinkerMeta.sorting_date))
		#

		return _return
	#

	@staticmethod
	def load_encapsulated_entry(_id, client_user_agent = None, cds = None):
	#
		"""
Load a matching VpmcEntry resource for the given UPnP resource CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS

:return: (object) Resource object; None on error
:since:  v0.1.00
		"""

		_return = None

		resource = Resource.load_cds_id(_id, client_user_agent)
		mime_type = (None if (resource == None) else resource.get_mime_type())

		if (mime_type != None):
		#
			if (mime_type == "text/directory"): entry_class_name = "dNG.pas.data.upnp.resources.VpmcEntry"
			else:
			#
				entry_class_name = "dNG.pas.data.upnp.resources.VpmcEntry{0}".format("".join([word.capitalize() for word in re.split("\\W", mime_type.split("/")[0])]))
				if (not NamedLoader.is_defined(entry_class_name)): entry_class_name = "dNG.pas.data.upnp.resources.VpmcEntry"
			#

			_return = NamedLoader.get_instance(entry_class_name, False)
			if (_return != None and (not _return.init_cds_id(_id, client_user_agent, cds))): _return = None
		#

		return _return
	#

	@staticmethod
	def load_root_containers(_filter = "+dc:title"):
	#
		database = Connection.get_instance()
		result = database.execute(VpmcEntry._db_apply_sort_order(database.query(VpmcUpnpResource).filter(VpmcUpnpResource.type == VpmcEntry.DB_TYPE_ROOT).join(VpmcUpnpResource.rel_meta), _filter))

		return ([ ] if (result == None) else VpmcEntry.iterator(VpmcUpnpResource, result, VpmcEntry))
	#
#

##j## EOF