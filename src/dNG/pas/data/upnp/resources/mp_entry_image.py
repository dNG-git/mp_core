# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from dNG.pas.data.binary import Binary
from dNG.pas.data.media.image import Image
from dNG.pas.data.media.image_metadata import ImageMetadata
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.instances.mp_upnp_image_resource import MpUpnpImageResource as _DbMpUpnpImageResource
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
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

		if (self.get_type() & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) != None):
		#
			entry_data = self.get_data_attributes("artist", "description", "creator")

			if (entry_data['artist'] != None): xml_resource.add_node("{0} upnp:artist".format(xml_node_path), entry_data['artist'])
			if (entry_data['creator'] != None): xml_resource.add_node("{0} dc:creator".format(xml_node_path), entry_data['creator'])
			if (entry_data['description'] != None): xml_resource.add_node("{0} dc:description".format(xml_node_path), entry_data['description'])
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

			if (entry_data['width'] != None and entry_data['height'] != None):
			#
				data['resolution'] = "{0:d}x{1:d}".format(entry_data['width'],
				                                          entry_data['height']
				                                         )
			#

			if (entry_data['bpp'] != None): data['colorDepth'] = entry_data['bpp']

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
		if (self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM): self._append_stream_content_metadata(_return)

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

		if (self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
		#
			for resource in _return: self._append_stream_content_metadata(resource)
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

		if (self.type & MpEntry.TYPE_CDS_ITEM == MpEntry.TYPE_CDS_ITEM):
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

		if (self.get_type() & MpEntryImage.TYPE_CDS_ITEM == MpEntryImage.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) != None):
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

	def _init_encapsulated_resource(self):
	#
		"""
Initialize an new encapsulated UPnP resource.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbMpUpnpImageResource)
		MpEntry._init_encapsulated_resource(self)
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryImage.

:since: v0.1.00
		"""

		MpEntry.refresh_metadata(self)

		encapsulated_resource = self.load_encapsulated_resource()

		if ((not issubclass(Image, NotImplementedClass))
		    and encapsulated_resource != None
		    and encapsulated_resource.is_filesystem_resource()
		    and encapsulated_resource.get_path() != None
		   ):
		#
			image = Image()
			metadata = (image.get_metadata() if (image.open_url(encapsulated_resource.get_id())) else None)

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
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbMpUpnpImageResource)

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