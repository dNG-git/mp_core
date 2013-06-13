# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.File
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
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader

class File(Resource):
#
	"""
"Resource" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	TYPE_CDS_ITEM_AUDIO = 16
	"""
UPnP CDS bookmark container type
	"""
	TYPE_CDS_ITEM_IMAGE = 32
	"""
UPnP CDS bookmark container type
	"""
	TYPE_CDS_ITEM_VIDEO = 64
	"""
UPnP CDS bookmark container type
	"""
	TYPE_CDS_STORAGE_FOLDER = 8
	"""
UPnP CDS storageFolder container type
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Resource)

:since: v0.1.00
		"""

		Resource.__init__(self)

		self.path = None
		"""
Filesystem path
		"""
		self.content_ids = [ ]
		"""
Filesystem entries
		"""
	#

	def _content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		mime_types = MimeType.get_instance()
		self.content = [ ]

		if (self.type & File.TYPE_CDS_CONTAINER == File.TYPE_CDS_CONTAINER):
		#
			entries = { }

			if (len(self.content_ids) < 1):
			#
				dir_names = [ ]
				file_names = [ ]

				for entry_name in os.listdir(self.path):
				#
					entry_pathname = path.normpath("{0}/{1}".format(self.path, Binary.str(entry_name)))
					resource = File()

					if (resource.init_cds_id("file:///{0}".format(entry_pathname), self.client_user_agent)):
					#
						entry_name = entry_name.lower()
						entries[entry_name] = resource

						if (path.isdir(entry_pathname)): dir_names.append(entry_name)
						elif (path.isfile(entry_pathname)): file_names.append(entry_name)
					#
				#

				file_names_ignored = [ ]

				for file_name in file_names:
				#
					if (re.search("\\.thumbnail\\.\\w+$", file_name) == None):
					#
						file_ext = path.splitext(file_name)[1]
						mime_type_definition = mime_types.get(file_ext[1:])

						if (mime_type_definition != None and "type" in mime_type_definition and mime_type_definition['type'] != "image"):
						#
							thumbnail_name = "{0}.png".format(file_name[0:-1 * len(file_ext)])
							if (thumbnail_name in file_names): file_names_ignored.append(thumbnail_name)

							thumbnail_name = "{0}.jpg".format(file_name[0:-1 * len(file_ext)])
							if (thumbnail_name in file_names): file_names_ignored.append(thumbnail_name)
						#
					#
					else: file_names_ignored.append(file_name)
				#

				for file_name in file_names_ignored: file_names.remove(file_name)

				dir_names.sort()
				file_names.sort()
				entry_names_normalized = (dir_names + file_names)

				for file_name in entry_names_normalized: self.content_ids.append(entries[file_name].get_id())
			#
			else:
			#
				entry_names_normalized = [ ]

				for entry_id in self.content_ids:
				#
					resource = File()

					if (resource.init_cds_id(entry_id, self.client_user_agent)):
					#
						url_elements = urlsplit(entry_id)
						url_elements_path = path.normpath(unquote(url_elements.path[1:]))

						entry_name = path.basename(url_elements_path).lower()
						entries[entry_name] = resource
						entry_names_normalized.append(entry_name)

						if (path.isdir(entry_pathname)): dir_names.append(entry_name)
						elif (path.isfile(entry_pathname)): file_names.append(entry_name)
					#
				#
			#

			entries_limit = len(self.content_ids)

			if (self.content_limit != None):
			#
				if ((self.content_offset + self.content_limit) < len(self.content_ids)): entries_limit = self.content_offset + self.content_limit
				entries_offset = self.content_offset
			#
			else: entries_offset = 0

			for position in range(entries_offset, entries_limit): self.content.append(entries[entry_names_normalized[position]])
		#
		else:
		#
			path_ext = path.splitext(self.path)[1]
			mime_type_definition = mime_types.get(path_ext[1:])
			resource_stream = (None if (mime_type_definition == None) else NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Stream".format("".join([word.capitalize() for word in re.split("[\\W_]+", mime_type_definition['mimetype'])])), False))

			if (resource_stream != None):
			#
				resource_stream.init_cds_id("file:///{0}".format(self.path), self.client_user_agent)
				self.content.append(resource_stream)

				resource_thumbnail_pathname = re.sub("(\\.\\w+)$", ".thumbnail.\\1", self.path)

				if (not os.access(resource_thumbnail_pathname, os.R_OK)):
				#
					if (mime_type_definition['type'] != "image"):
					#
						resource_thumbnail_pathname = "{0}.png".format(self.path[0:-1 * len(path_ext)])
						if (not os.access(resource_thumbnail_pathname, os.R_OK)): resource_thumbnail_pathname = None

						if (resource_thumbnail_pathname == None):
						#
							resource_thumbnail_pathname = "{0}.jpg".format(self.path[0:-1 * len(path_ext)])
							if (not os.access(resource_thumbnail_pathname, os.R_OK)): resource_thumbnail_pathname = None
						#
					#
					else: resource_thumbnail_pathname = None
				#

				if (resource_thumbnail_pathname != None):
				#
					path_ext = path.splitext(resource_thumbnail_pathname)[1]
					mime_type_definition = mime_types.get(path_ext[1:])
					resource_thumbnail = (None if (mime_type_definition == None) else NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Thumbnail".format("".join([word.capitalize() for word in re.split("[\\W_]+", mime_type_definition['mimetype'])])), False))

					if (resource_thumbnail != None):
					#
						resource_thumbnail.init_cds_id("file:///{0}".format(resource_thumbnail_pathname), self.client_user_agent)
						self.content.append(resource_thumbnail)
					#
				#
			#
		#

		return True
	#

	def get_id(self):
	#
		"""
Returns the UPnP resource ID.

:return: (str) UPnP resource ID
:since:  v0.1.00
		"""

		scheme_delimiter = 1 + self.id.find(":")
		return self.id[:scheme_delimiter] + quote(self.id[scheme_delimiter:], "/")
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

	def get_mime_type(self):
	#
		"""
Returns the UPnP resource mime type.

:return: (str) UPnP resource mime type; None if unknown
:since:  v0.1.00
		"""

		if (self.mime_type == None):
		#
			if (path.isdir(self.path)): self.mime_type = "text/directory"
			else:
			#
				file_ext = path.splitext(self.path)[1]
				mime_type_definition = MimeType.get_instance().get(file_ext[1:])
				if (mime_type_definition != None): self.mime_type = mime_type_definition['mimetype']
			#
		#

		return self.mime_type
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.1.00
		"""

		if (self.timestamp < 0): self.timestamp = int(os.stat(self.path).st_mtime)
		return self.timestamp
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.1.00
		"""

		if (self.content == None): self._content_init()
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

		if (self.type == None): is_supported = False
		else:
		#
			client = Client.load_user_agent(self.client_user_agent)
			is_supported = (True if (client == None or client.get("upnp_didl_cds1_classes_supported", True)) else False)
		#

		if (is_supported):
		#
			if (self.type & File.TYPE_CDS_ITEM_AUDIO == File.TYPE_CDS_ITEM_AUDIO): _return = "object.item.audioItem.musicTrack"
			elif (self.type & File.TYPE_CDS_ITEM_IMAGE == File.TYPE_CDS_ITEM_IMAGE): _return = "object.item.imageItem.photo"
			elif (self.type & File.TYPE_CDS_ITEM_VIDEO == File.TYPE_CDS_ITEM_VIDEO): _return = "object.item.videoItem.movie"
			elif (self.type & File.TYPE_CDS_STORAGE_FOLDER == File.TYPE_CDS_STORAGE_FOLDER): _return = "object.container.storageFolder"
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
		url_elements_path = path.normpath(unquote(url_elements.path[1:]))

		if (os.access(url_elements_path, os.R_OK)):
		#
			self.path = url_elements_path
			self.updatable = os.access(self.path, os.W_OK)

			if (path.isdir(self.path)):
			#
				self.name = path.basename(self.path)
				self.type = File.TYPE_CDS_STORAGE_FOLDER | File.TYPE_CDS_CONTAINER

				_return = True
			#
			elif (path.isfile(self.path)):
			#
				self.name = path.splitext(path.basename(self.path))[0]
				self.size = os.stat(self.path).st_size

				path_ext = path.splitext(self.path)[1]
				mime_type_definition = MimeType.get_instance().get(path_ext[1:])

				if (mime_type_definition != None):
				#
					if (mime_type_definition['type'] == "audio"): self.type = File.TYPE_CDS_ITEM_AUDIO | File.TYPE_CDS_ITEM
					elif (mime_type_definition['type'] == "image"): self.type = File.TYPE_CDS_ITEM_IMAGE | File.TYPE_CDS_ITEM
					elif (mime_type_definition['type'] == "video"): self.type = File.TYPE_CDS_ITEM_VIDEO | File.TYPE_CDS_ITEM
				#

				if (self.type == None): self.type = File.TYPE_CDS_ITEM
				_return = True
			#
		#

		return _return
	#

	def is_filesystem_resource(self):
	#
		"""
Returns true if the resource is a local filesystem one.

:return: (bool) True if local filesystem resource
:since:  v0.1.00
		"""

		return (False if (self.path == None) else True)
	#

	def metadata_add_didl_xml_node(self, xml_writer, xml_node_path, resource):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.00
		"""

		Resource.metadata_add_didl_xml_node(self, xml_writer, xml_node_path, resource)
		resource_type = resource.get_type()

		if (resource_type & File.TYPE_CDS_STORAGE_FOLDER == File.TYPE_CDS_STORAGE_FOLDER):
		#
			xml_node = xml_writer.node_get(xml_node_path, False)
			if ("xml.item" in xml_node): xml_node = xml_node['xml.item']

			if (xml_node != False):
			#
				xml_node['attributes'].update({ "upnp:storageUsed": "-1" })
				xml_writer.node_change_attributes(xml_node_path, xml_node['attributes'])
			#
		#
	#
#

##j## EOF