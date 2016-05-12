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

import re

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.data.media.image import Image
from dNG.pas.data.media.image_metadata import ImageMetadata
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.instances.mp_upnp_image_resource import MpUpnpImageResource as _DbMpUpnpImageResource
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.not_implemented_class import NotImplementedClass
from .mp_entry import MpEntry

class MpEntryImage(MpEntry):
#
	"""
"MpEntryImage" is used for UPnP image database entries.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	_DB_INSTANCE_CLASS = _DbMpUpnpImageResource
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""

	def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
	#
		"""
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		MpEntry._add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id)

		if (self.get_type() & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
		#
			entry_data = self.get_data_attributes("artist", "description", "creator")

			if (entry_data['artist'] is not None): xml_resource.add_node("{0} upnp:artist".format(xml_node_path), entry_data['artist'])
			if (entry_data['creator'] is not None): xml_resource.add_node("{0} dc:creator".format(xml_node_path), entry_data['creator'])
			if (entry_data['description'] is not None): xml_resource.add_node("{0} dc:description".format(xml_node_path), entry_data['description'])
		#
	#

	def _append_stream_content_metadata(self, resource):
	#
		"""
Appends audio metadata to the given stream resource.

:param resource: UPnP stream resource

:since: v0.1.01
		"""

		# pylint: disable=star-args

		if (isinstance(resource, AbstractStream) and resource.is_supported("metadata")):
		#
			entry_data = self.get_data_attributes("width", "height", "bpp")
			data = { }

			if (entry_data['width'] is not None and entry_data['height'] is not None):
			#
				data['resolution'] = "{0:d}x{1:d}".format(entry_data['width'],
				                                          entry_data['height']
				                                         )
			#

			if (entry_data['bpp'] is not None): data['colorDepth'] = entry_data['bpp']

			if (len(data) > 0): resource.set_metadata(**data)
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

		_return = MpEntry.get_content(self, position)

		if (self.type & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM):
		#
			encapsulated_id = self.get_encapsulated_id()
			if (encapsulated_id == _return.get_resource_id()): self._append_stream_content_metadata(_return)
		#

		return _return
	#

	def get_content_list(self):
	#
		"""
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		_return = MpEntry.get_content_list(self)

		if (self.type & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM):
		#
			encapsulated_id = self.get_encapsulated_id()

			for resource in _return:
			#
				if (encapsulated_id == resource.get_resource_id()): self._append_stream_content_metadata(resource)
			#
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

		_return = MpEntry.get_content_list_of_type(self, _type)

		if (self.type & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM):
		#
			for resource in _return: self._append_stream_content_metadata(resource)
		#

		return _return
	#

	def _filter_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to remove DIDL metadata not requested by the
client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		MpEntry._filter_metadata_of_didl_xml_node(self, xml_resource, xml_node_path)

		if (self.get_type() & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
		#
			didl_fields = self.get_didl_fields()

			if (len(didl_fields) > 0):
			#
				if ("upnp:artist" not in didl_fields): xml_resource.remove_node("{0} upnp:artist".format(xml_node_path))
				if ("dc:creator" not in didl_fields): xml_resource.remove_node("{0} dc:creator".format(xml_node_path))
				if ("dc:description" not in didl_fields): xml_resource.remove_node("{0} dc:description".format(xml_node_path))
			#
		#
	#

	def _init_item_content(self):
	#
		"""
Initializes the content of an UPnP CDS item entry.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		_return = False

		client_settings = self.get_client_settings()
		encapsulated_resource = self.load_encapsulated_resource()

		if (Settings.get("mp_core_transform_images_on_server", True)
		    and client_settings.get("upnp_stream_image_resized", False)
		    and encapsulated_resource.is_filesystem_resource()
		    and Image().is_supported("transformation")
		   ):
		#
			entry_data = self.get_data_attributes("width", "height")

			transformed_image_type = client_settings.get("upnp_stream_image_resized_type")
			transformed_image_width = client_settings.get("upnp_stream_image_resized_width")
			transformed_image_height = client_settings.get("upnp_stream_image_resized_height")

			if (transformed_image_type is not None
			    and transformed_image_width is not None
			    and transformed_image_height is not None
			    and ((entry_data['width'] is None or transformed_image_width < entry_data['width'])
			         or (entry_data['height'] is None or transformed_image_height < entry_data['height'])
			        )
			   ):
			#
				camel_case_type = "".join([word.capitalize() for word in re.split("\\W", transformed_image_type.split("/")[0])])
				transformed_image_class_name = "dNG.pas.data.upnp.resources.TransformedImage{0}Stream".format(camel_case_type)

				transformed_image_resource = NamedLoader.get_instance(transformed_image_class_name, False)

				if (transformed_image_resource is not None):
				#
					transformed_image_resource.set_transformed_source_path(encapsulated_resource.get_path())
					transformed_image_resource.set_transformed_image_width(transformed_image_width)
					transformed_image_resource.set_transformed_image_height(transformed_image_height)
					transformed_image_resource.init_cds_id("upnp-transformed-image:///{0}".format(quote(encapsulated_resource.get_resource_id())))

					self.content = [ transformed_image_resource ]
					_return = True
				#
			#
		#

		if (not _return): _return = MpEntry._init_item_content(self)

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryImage.

:since: v0.1.00
		"""

		with self:
		#
			MpEntry.refresh_metadata(self)

			encapsulated_resource = self.load_encapsulated_resource()

			if ((not issubclass(Image, NotImplementedClass))
			    and encapsulated_resource is not None
			    and encapsulated_resource.is_filesystem_resource()
			    and encapsulated_resource.get_path() is not None
			   ): self._refresh_image_metadata(encapsulated_resource.get_resource_id())
		#
	#

	def _refresh_image_metadata(self, resource_url):
	#
		"""
Refresh metadata associated with this MpEntryAudio.

:since: v0.1.00
		"""

		image = Image()
		metadata = (image.get_metadata() if (image.open_url(resource_url)) else None)

		if (isinstance(metadata, ImageMetadata)):
		#
			self.set_data_attributes(metadata = metadata.get_json(),
			                         artist = metadata.get_artist(),
			                         description = metadata.get_description(),
			                         width = metadata.get_width(),
			                         height = metadata.get_height(),
			                         bpp = metadata.get_bpp(),
			                         creator = metadata.get_producer()
			                        )

			self.save()
		#
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		with self:
		#
			MpEntry.set_data_attributes(self, **kwargs)

			if ("artist" in kwargs): self.local.db_instance.artist = Binary.utf8(kwargs['artist'])
			if ("description" in kwargs): self.local.db_instance.description = Binary.utf8(kwargs['description'])
			if ("width" in kwargs): self.local.db_instance.width = kwargs['width']
			if ("height" in kwargs): self.local.db_instance.height = kwargs['height']
			if ("bpp" in kwargs): self.local.db_instance.bpp = kwargs['bpp']
			if ("creator" in kwargs): self.local.db_instance.creator = Binary.utf8(kwargs['creator'])
		#
	#
#

##j## EOF