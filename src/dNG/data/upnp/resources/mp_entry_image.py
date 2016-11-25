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

from dNG.data.binary import Binary
from dNG.data.media.image_implementation import ImageImplementation
from dNG.data.media.image_metadata import ImageMetadata
from dNG.database.instances.mp_upnp_image_resource import MpUpnpImageResource as _DbMpUpnpImageResource

from .mp_entry import MpEntry

class MpEntryImage(MpEntry):
#
	"""
"MpEntryImage" is used for UPnP image database entries.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	_DB_INSTANCE_CLASS = _DbMpUpnpImageResource
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""
	METADATA_MIN_SIZE = 20480
	"""
Minimum underlying VFS object size before trying to read image metadata
	"""

	def __init__(self, db_instance = None, user_agent = None, didl_fields = None):
	#
		"""
Constructor __init__(MpEntryImage)

:param db_instance: Encapsulated SQLAlchemy database instance
:param user_agent: Client user agent
:param didl_fields: DIDL fields list

:since: v0.2.00
		"""

		MpEntry.__init__(self, db_instance, user_agent, didl_fields)

		self.supported_features['thumbnail_source_vfs_url'] = True
		self.supported_features['upnp_resource_metadata'] = True
	#

	def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
	#
		"""
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since: v0.2.00
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

	def _filter_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to remove DIDL metadata not requested by the
client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since: v0.2.00
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

	def get_thumbnail_source_vfs_url(self, generate_thumbnail = True):
	#
		"""
Returns the thumbnail source VFS URL if applicable.

:param generate_thumbnail: True to generate a missing thumbnail on the fly

:return: (str) Thumbnail source VFS URL; None if no thumbnail file exist
:since:  v0.2.00
		"""

		return self.get_vfs_url()
	#

	def get_upnp_resource_metadata(self):
	#
		"""
Returns the metadata of the original source UPnP resource.

:return: (dict) Metadata of the original source UPnP resource
:since:  v0.2.00
		"""

		_return = { }

		entry_data = self.get_data_attributes("width", "height", "bpp")

		if (entry_data['width'] is not None and entry_data['height'] is not None):
		#
			_return['resolution'] = "{0:d}x{1:d}".format(entry_data['width'],
			                                             entry_data['height']
			                                            )
		#

		if (entry_data['bpp'] is not None): _return['colorDepth'] = entry_data['bpp']

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryImage.

:since: v0.2.00
		"""

		MpEntry.refresh_metadata(self)

		if (ImageImplementation.get_class() is not None):
		#
			if (self.get_size() > MpEntryImage.METADATA_MIN_SIZE): self._refresh_image_metadata(self.get_vfs_url())
		#
	#

	def _refresh_image_metadata(self, vfs_url):
	#
		"""
Refresh metadata associated with this MpEntryAudio.

:param vfs_url: UPnP resource VFS URL

:since: v0.2.00
		"""

		image = ImageImplementation.get_instance()
		metadata = None

		if (vfs_url != ""):
		#
			if (vfs_url[:2] == "x-"): vfs_url = MpEntryImage._get_http_upnp_stream_url(self.get_resource_id())
			metadata = (image.get_metadata() if (image.open_url(vfs_url)) else None)
		#

		if (isinstance(metadata, ImageMetadata)):
		#
			self.mimeclass = metadata.get_mimeclass()
			self.mimetype = metadata.get_mimetype()

			self.set_data_attributes(mimeclass = self.mimeclass,
			                         mimetype = self.mimetype,
			                         metadata = metadata.get_json(),
			                         artist = metadata.get_artist(),
			                         description = metadata.get_description(),
			                         width = metadata.get_width(),
			                         height = metadata.get_height(),
			                         bpp = metadata.get_bpp(),
			                         creator = metadata.get_producer()
			                        )
		#
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.2.00
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