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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
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

try: from urllib.parse import unquote
except ImportError: from urllib import unquote

from dNG.data.mime_type import MimeType
from dNG.runtime.io_exception import IOException
from dNG.runtime.value_exception import ValueException
from dNG.vfs.implementation import Implementation
from dNG.vfs.file.object import Object as VfsFileObject

from .abstract import Abstract

class File(Abstract):
#
	"""
"File" represents an UPnP directory or file in the local filesystem.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
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

:since: v0.2.00
		"""

		Abstract.__init__(self)

		self.vfs_object = None
		"""
VFS object
		"""

		self.supported_features['search_content'] = False
	#

	def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
	#
		"""
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.2.00
		"""

		Abstract._add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id)
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

	def _get_resource_path_name(self):
	#
		"""
Get the UPnP resource ID based path and name of the underlying filesystem
object.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.2.00
		"""

		return unquote(self.resource_id[4 + self.resource_id.index("://"):])
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.2.00
		"""

		if ((not self.deleted)
		    and self.timestamp < 0
		   ): self.timestamp = int(os.stat(self._get_resource_path_name()).st_mtime)

		return self.timestamp
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.2.00
		"""

		if (self.content is None): self._init_content()
		return (0 if (self.content is None) else len(self.content))
	#

	def get_type_class(self):
	#
		"""
Returns the UPnP resource type class.

:return: (str) UPnP resource type class; None if unknown
:since:  v0.2.00
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

		if (_return is None): _return = Abstract.get_type_class(self)
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
:since:  v0.2.00
		"""

		Abstract.init_cds_id(self, _id, client_user_agent, deleted)
		_return = (self.resource_id is not None)

		if (_return):
		#
			try:
			#
				vfs_object = Implementation.load_vfs_url(self.resource_id, True)
				if (not isinstance(vfs_object, VfsFileObject)): raise ValueException("VFS URL given is invalid for the UPNP file resource")

				self.vfs_object = vfs_object
			#
			except IOException: _return = False

			mimetype_definition = None

			if (not _return):
			#
				if (self.deleted):
				#
					resource_path_name = self._get_resource_path_name()
					resource_name = path.basename(resource_path_name)

					self.deleted = True

					if (resource_name == ""):
					#
						self.mimeclass = "directory"
						self.mimetype = "text/directory"
						self.name = path.basename(path.dirname(resource_path_name))
						self.type = File.TYPE_CDS_STORAGE_FOLDER | File.TYPE_CDS_CONTAINER
					#
					else:
					#
						resource_file_data = path.splitext(resource_name)
						self.name = resource_file_data[0]
						self.type = File.TYPE_CDS_ITEM

						mimetype_definition = MimeType.get_instance().get(resource_file_data[1][1:])
					#
				#
			#
			elif (self.vfs_object.is_directory()):
			#
				self.mimeclass = "directory"
				self.mimetype = "text/directory"
				self.name = self.vfs_object.get_name()
				self.type = File.TYPE_CDS_STORAGE_FOLDER | File.TYPE_CDS_CONTAINER
			#
			else:
			#
				resource_path_name = self._get_resource_path_name()

				resource_file_data = path.splitext(self.vfs_object.get_name())

				self.name = resource_file_data[0]
				self.size = os.stat(resource_path_name).st_size
				self.type = File.TYPE_CDS_ITEM

				mimetype_definition = MimeType.get_instance().get(resource_file_data[1][1:])
			#

			if (mimetype_definition is not None):
			#
				self.mimeclass = mimetype_definition['class']
				self.mimetype = mimetype_definition['type']

				if (mimetype_definition['class'] == "audio"): self.type |= File.TYPE_CDS_ITEM_AUDIO
				elif (mimetype_definition['class'] == "image"): self.type |= File.TYPE_CDS_ITEM_IMAGE
				elif (mimetype_definition['class'] == "video"): self.type |= File.TYPE_CDS_ITEM_VIDEO
			#
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
		"""

		_return = (self.type is not None)

		if (self.content is None and _return):
		# Thread safety
			with self._lock:
			#
				if (self.content is None):
				#
					_return = (self._init_directory_content()
					           if (self.type & File.TYPE_CDS_CONTAINER == File.TYPE_CDS_CONTAINER) else
					           Abstract._init_content(self)
					          )
				#
			#
		#

		return _return
	#

	def _init_directory_content(self):
	#
		"""
Initializes the content of a directory container.

:return: (list) Directory resources
:since:  v0.2.00
		"""

		if (self.content is None):
		#
			entries = { }
			mimetypes = MimeType.get_instance()

			dir_names = [ ]
			file_names = [ ]

			for vfs_child_object in self.vfs_object.scan():
			#
				resource = File()
				vfs_child_vfs_url = vfs_child_object.get_url()

				if (isinstance(vfs_child_object, VfsFileObject)
				    and resource.init_cds_id(vfs_child_vfs_url, self.client_user_agent)
				   ):
				#
					vfs_child_path_name = unquote(vfs_child_vfs_url[4 + vfs_child_vfs_url.index("://"):])

					vfs_child_name = path.basename(vfs_child_path_name).lower()
					entries[vfs_child_name] = resource

					if (vfs_child_object.is_directory()): dir_names.append(vfs_child_name)
					elif (vfs_child_object.is_file()): file_names.append(vfs_child_name)
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
			#

			dir_names.sort()
			file_names.sort()
			entry_names_normalized = (dir_names + file_names)

			self.content = [ entries[file_name] for file_name in entry_names_normalized ]
		#

		return True
	#
#

##j## EOF