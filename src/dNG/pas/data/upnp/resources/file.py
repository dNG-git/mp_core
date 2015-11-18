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
from os import path
import os
import re

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
#
	from urllib import quote, unquote
	from urlparse import urlsplit
#

from dNG.pas.data.binary import Binary
from dNG.pas.data.mime_type import MimeType
from dNG.pas.data.upnp.resource import Resource
from .abstract_stream import AbstractStream
from .thumbnail_resource_mixin import ThumbnailResourceMixin

class File(Resource, ThumbnailResourceMixin):
#
	"""
"File" represents an UPnP directory or file in the local filesystem.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	RE_THUMBNAIL_SUFFIX = re.compile("\\.thumbnail\\.\\w+$", re.I)
	"""
RegExp for matching the file name format "<name>.thumbnail.<extension>"
	"""

	TYPE_CDS_ITEM_AUDIO = 16
	"""
UPnP CDS audio item type
	"""
	TYPE_CDS_ITEM_IMAGE = 32
	"""
UPnP CDS image item type
	"""
	TYPE_CDS_ITEM_VIDEO = 64
	"""
UPnP CDS video item type
	"""
	TYPE_CDS_STORAGE_FOLDER = 8
	"""
UPnP CDS storageFolder container type
	"""

	def __init__(self):
	#
		"""
Constructor __init__(File)

:since: v0.1.00
		"""

		Resource.__init__(self)
		ThumbnailResourceMixin.__init__(self)

		self.content_ids = [ ]
		"""
Filesystem entries
		"""
		self.path = None
		"""
Filesystem path
		"""

		self.supported_features['search_content'] = False
		self.supported_features['thumbnail_file'] = True
	#

	def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
	#
		"""
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		Resource._add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id)
		resource_type = self.get_type()

		if (resource_type & File.TYPE_CDS_CONTAINER == File.TYPE_CDS_CONTAINER):
		#
			xml_node_attributes = xml_resource.get_node_attributes(xml_node_path)

			if (xml_node_attributes is not None):
			#
				xml_node_attributes.update({ "upnp:storageUsed": "-1" })
				xml_resource.change_node_attributes(xml_node_path, xml_node_attributes)
			#
		#
	#

	def flush_content_cache(self):
	#
		"""
Flushes the content cache.

:since: v0.1.01
		"""

		Resource.flush_content_cache(self)
		self.content_ids = [ ]
	#

	def get_path(self):
	#
		"""
Returns the filesystem path.

:return: (str) Filesystem path
:since:  v0.1.00
		"""

		return self.path
	#

	def get_thumbnail_file_path_name(self):
	#
		"""
Returns the thumbnail file path and name if applicable.

:return: (str) File path and name; None if no thumbnail file exist
:since:  v0.1.02
		"""

		_return = None

		( file_path_name_without_ext, file_ext) = path.splitext(self.path)
		thumbnail_path_name = "{0}.thumbnail{1}".format(file_path_name_without_ext, file_ext)

		if (os.access(thumbnail_path_name, os.R_OK)): _return = thumbnail_path_name
		else:
		#
			thumbnail_path_name = None

			if (self.get_mimeclass() != "image"):
			#
				thumbnail_path_name = "{0}.png".format(file_path_name_without_ext)
				if (os.access(thumbnail_path_name, os.R_OK)): _return = thumbnail_path_name

				if (_return is None):
				#
					thumbnail_path_name = "{0}.jpg".format(file_path_name_without_ext)
					if (os.access(thumbnail_path_name, os.R_OK)): _return = thumbnail_path_name
				#
			#
			elif (self.is_thumbnail_transformation_supported()): _return = self.path
		#

		return _return
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.1.00
		"""

		if ((not self.deleted) and self.timestamp < 0): self.timestamp = int(os.stat(self.path).st_mtime)
		return self.timestamp
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.1.00
		"""

		if (self.content is None): self._init_content()
		return len(self.content_ids)
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

		if (_type is not None):
		#
			client_settings = self.get_client_settings()
			is_cds1_container_supported = client_settings.get("upnp_didl_cds1_container_classes_supported", True)
			is_cds1_object_supported = client_settings.get("upnp_didl_cds1_object_classes_supported", True)
		#

		if (is_cds1_container_supported
		    and _type & File.TYPE_CDS_STORAGE_FOLDER == File.TYPE_CDS_STORAGE_FOLDER
		   ): _return = "object.container.storageFolder"

		if (is_cds1_object_supported):
		#
			if (_type & File.TYPE_CDS_ITEM_AUDIO == File.TYPE_CDS_ITEM_AUDIO): _return = "object.item.audioItem.musicTrack"
			elif (_type & File.TYPE_CDS_ITEM_IMAGE == File.TYPE_CDS_ITEM_IMAGE): _return = "object.item.imageItem.photo"
			elif (_type & File.TYPE_CDS_ITEM_VIDEO == File.TYPE_CDS_ITEM_VIDEO): _return = "object.item.videoItem.movie"
		#

		if (_return is None): _return = Resource.get_type_class(self)
		return _return
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
			mimetype_definition = None
			url_elements = urlsplit(self.resource_id)
			url_elements_path = path.normpath(unquote(url_elements.path[1:]))

			"""
Rewrite ID to ensure we got a valid encoded path URL
			"""

			self.resource_id = "file:///{0}".format(quote(url_elements_path, "/"))

			if (os.access(url_elements_path, os.R_OK)):
			#
				self.path = url_elements_path
				# self.updatable = os.access(self.path, os.W_OK) # @TODO: Support CreateObject & co.

				if (path.isdir(self.path)):
				#
					self.mimeclass = "directory"
					self.mimetype = "text/directory"
					self.name = path.basename(self.path)
					self.type = File.TYPE_CDS_STORAGE_FOLDER | File.TYPE_CDS_CONTAINER
				#
				elif (path.isfile(self.path)):
				#
					fileinfo = path.splitext(path.basename(self.path))

					self.name = fileinfo[0]
					self.size = os.stat(self.path).st_size
					self.type = File.TYPE_CDS_ITEM

					mimetype_definition = MimeType.get_instance().get(fileinfo[1][1:])
				#
				else: _return = False
			#
			elif (deleted):
			#
				"""
Warning: We can only guess if a given path was a directory or file.
				"""

				fileinfo = path.splitext(path.basename(url_elements_path))

				self.deleted = True
				self.name = fileinfo[0]
				self.path = url_elements_path

				if (fileinfo[1] == ""):
				#
					self.mimeclass = "directory"
					self.mimetype = "text/directory"
					self.type = File.TYPE_CDS_STORAGE_FOLDER | File.TYPE_CDS_CONTAINER
				#
				else:
				#
					self.type = File.TYPE_CDS_ITEM

					mimetype_definition = MimeType.get_instance().get(fileinfo[1][1:])
				#
			#
			else: _return = False

			if (mimetype_definition is not None):
			#
				self.mimeclass = mimetype_definition['class']
				self.mimetype = mimetype_definition['type']

				if (mimetype_definition['class'] == "audio"): self.type = File.TYPE_CDS_ITEM_AUDIO | File.TYPE_CDS_ITEM
				elif (mimetype_definition['class'] == "image"): self.type = File.TYPE_CDS_ITEM_IMAGE | File.TYPE_CDS_ITEM
				elif (mimetype_definition['class'] == "video"): self.type = File.TYPE_CDS_ITEM_VIDEO | File.TYPE_CDS_ITEM
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

		with self._lock:
		#
			if (self.content is None):
			#
				self.content = [ ]

				if (self.type & File.TYPE_CDS_CONTAINER == File.TYPE_CDS_CONTAINER): self.content = self._init_content_directory_scan()
				elif (self.type & File.TYPE_CDS_ITEM == File.TYPE_CDS_ITEM): self.content = self._init_content_file_scan()
			#
		#

		return True
	#

	def _init_content_directory_scan(self):
	#
		"""
Initializes the content of a directory container.

:return: (list) Directory resources
:since:  v0.1.00
		"""

		_return = [ ]

		entries = { }
		mimetypes = MimeType.get_instance()

		if ((not self.deleted) and len(self.content_ids) < 1):
		#
			dir_names = [ ]
			file_names = [ ]

			for entry_name in os.listdir(self.path):
			#
				entry_path_name = path.join(self.path, Binary.str(entry_name))
				resource = File()

				if (resource.init_cds_id("file:///{0}".format(entry_path_name), self.client_user_agent)):
				#
					entry_name = entry_name.lower()
					entries[entry_name] = resource

					if (path.isdir(entry_path_name)): dir_names.append(entry_name)
					elif (path.isfile(entry_path_name)): file_names.append(entry_name)
				#
			#

			file_names_iterable = (file_names.copy() if (hasattr(file_names, "copy")) else copy(file_names))

			for file_name in file_names_iterable:
			#
				( file_name_without_ext, file_ext) = path.splitext(file_name)
				thumbnail_file_name = "{0}.thumbnail{1}".format(file_name_without_ext, file_ext)

				if (thumbnail_file_name in file_names): file_names.remove(file_name)
				else:
				#
					mimetype_definition = mimetypes.get(file_ext[1:])

					if (mimetype_definition is not None and "class" in mimetype_definition and mimetype_definition['class'] != "image"):
					#
						thumbnail_jpg_name = "{0}.jpg".format(file_name_without_ext)
						thumbnail_png_name = "{0}.png".format(file_name_without_ext)

						if (thumbnail_png_name in file_names): file_names.remove(thumbnail_png_name)
						elif (thumbnail_jpg_name in file_names): file_names.remove(thumbnail_jpg_name)
					#
				#
			#

			dir_names.sort()
			file_names.sort()
			entry_names_normalized = (dir_names + file_names)

			for file_name in entry_names_normalized: self.content_ids.append(entries[file_name].get_resource_id())
		#
		else:
		#
			entry_names_normalized = [ ]

			for content_id in self.content_ids:
			#
				resource = File()

				if (resource.init_cds_id(content_id, self.client_user_agent)):
				#
					content_path = resource.get_path()

					entry_name = path.basename(content_path).lower()
					entries[entry_name] = resource
					entry_names_normalized.append(entry_name)
				#
			#
		#

		for file_name in entry_names_normalized: _return.append(entries[file_name])

		return _return
	#

	def _init_content_file_scan(self):
	#
		"""
Initializes the content of a file item.

:return: (list) File resources
:since:  v0.1.00
		"""

		_return = [ ]

		resource_stream = self._get_stream_resource()

		if (resource_stream is not None):
		#
			resource_stream.set_parent_resource_id(self.get_resource_id())

			size = self.get_size()
			if (size is not None and isinstance(resource_stream, AbstractStream)): resource_stream.set_size(size)

			resource_stream.init_cds_id("file:///{0}".format(self.path), self.client_user_agent)

			_return.append(resource_stream)

			thumbnail_path_name = self.get_thumbnail_file_path_name()
			if (thumbnail_path_name is not None): self.append_thumbnail_resources(_return, thumbnail_path_name)
		#

		return _return
	#

	def is_filesystem_resource(self):
	#
		"""
Returns true if the resource is represented in the filesystem.

:return: (bool) True if filesystem resource
:since:  v0.1.00
		"""

		return (self.path is not None)
	#
#

##j## EOF