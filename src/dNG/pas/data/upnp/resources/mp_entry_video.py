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
from dNG.pas.data.media.container_metadata import ContainerMetadata
from dNG.pas.data.media.video import Video
from dNG.pas.data.upnp.variable import Variable
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.instances.mp_upnp_video_resource import MpUpnpVideoResource as _DbMpUpnpVideoResource
from dNG.pas.runtime.not_implemented_class import NotImplementedClass
from .mp_entry import MpEntry

class MpEntryVideo(MpEntry):
#
	"""
"MpEntryVideo" is used for UPnP video database entries.

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

		if (self.get_type() & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) != None):
		#
			entry_data = self.get_data_attributes("description", "genre", "actor", "author", "director", "producer", "publisher")

			if (entry_data['actor'] != None): xml_resource.add_node("{0} upnp:actor".format(xml_node_path), entry_data['actor'])
			if (entry_data['author'] != None): xml_resource.add_node("{0} upnp:author".format(xml_node_path), entry_data['author'])
			if (entry_data['description'] != None): xml_resource.add_node("{0} dc:description".format(xml_node_path), entry_data['description'])

			if (entry_data['director'] != None):
			#
				xml_resource.add_node("{0} dc:creator".format(xml_node_path), entry_data['director'])
				xml_resource.add_node("{0} upnp:director".format(xml_node_path), entry_data['director'])
			#

			if (entry_data['genre'] != None): xml_resource.add_node("{0} upnp:genre".format(xml_node_path), entry_data['genre'])
			if (entry_data['producer'] != None): xml_resource.add_node("{0} upnp:producer".format(xml_node_path), entry_data['producer'])
			if (entry_data['publisher'] != None): xml_resource.add_node("{0} dc:publisher".format(xml_node_path), entry_data['publisher'])
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
			entry_data = self.get_data_attributes("size", "duration", "width", "height", "bitrate", "bpp")
			data = { }

			if (entry_data['duration'] != None): data['duration'] = Variable.get_upnp_duration(entry_data['duration'])

			if (entry_data['width'] != None
			    and entry_data['height'] != None
			   ): data['resolution'] = "{0:d}x{1:d}".format(entry_data['width'], entry_data['height'])

			if (entry_data['bitrate'] != None): data['bitrate'] = int(entry_data['bitrate'] / 8)
			elif (entry_data['duration'] != None and entry_data['size'] != None): data['bitrate'] = int(entry_data['size'] / entry_data['duration'])

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

		if (self.get_type() & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) != None):
		#
			didl_fields = self.get_didl_fields()

			if (len(didl_fields) > 0):
			#
				if ("upnp:actor" not in didl_fields): xml_resource.remove_node("{0} upnp:actor".format(xml_node_path))
				if ("upnp:author" not in didl_fields): xml_resource.remove_node("{0} upnp:author".format(xml_node_path))
				if ("dc:description" not in didl_fields): xml_resource.remove_node("{0} dc:description".format(xml_node_path))
				if ("dc:creator" not in didl_fields): xml_resource.remove_node("{0} dc:creator".format(xml_node_path))
				if ("upnp:director" not in didl_fields): xml_resource.remove_node("{0} upnp:director".format(xml_node_path))
				if ("upnp:genre" not in didl_fields): xml_resource.remove_node("{0} upnp:genre".format(xml_node_path))
				if ("upnp:producer" not in didl_fields): xml_resource.remove_node("{0} upnp:producer".format(xml_node_path))
				if ("dc:publisher" not in didl_fields): xml_resource.remove_node("{0} dc:publisher".format(xml_node_path))
			#
		#
	#

	def _init_encapsulated_resource(self):
	#
		"""
Initialize an new encapsulated UPnP resource.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbMpUpnpVideoResource)
		MpEntry._init_encapsulated_resource(self)
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryVideo.

:since: v0.1.00
		"""

		MpEntry.refresh_metadata(self)

		encapsulated_resource = self.load_encapsulated_resource()

		if ((not issubclass(Video, NotImplementedClass))
		    and encapsulated_resource != None
		    and encapsulated_resource.is_filesystem_resource()
		    and encapsulated_resource.get_path() != None
		   ):
		#
			video = Video()
			metadata = (video.get_metadata() if (video.open_url(encapsulated_resource.get_id())) else None)

			if (isinstance(metadata, ContainerMetadata) and metadata.get_video_streams_count() == 1):
			#
				video_metadata = metadata.get_video_streams(0)

				self.set_data_attributes(title = metadata.get_title(),
				                         mimetype = metadata.get_mimetype(),
				                         metadata = metadata.get_json(),
				                         duration = metadata.get_length(),
				                         width = video_metadata.get_width(),
				                         height = video_metadata.get_height(),
				                         codec = video_metadata.get_codec(),
				                         bitrate = video_metadata.get_bitrate(),
				                         bpp = video_metadata.get_bpp()
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

		self._ensure_thread_local_instance(_DbMpUpnpVideoResource)

		with self:
		#
			MpEntry.set_data_attributes(self, **kwargs)

			if ("duration" in kwargs): self.local.db_instance.duration = kwargs['duration']
			if ("description" in kwargs): self.local.db_instance.description = Binary.utf8(kwargs['description'])
			if ("genre" in kwargs): self.local.db_instance.genre = Binary.utf8(kwargs['genre'])
			if ("series" in kwargs): self.local.db_instance.series = Binary.utf8(kwargs['series'])
			if ("episode" in kwargs): self.local.db_instance.episode = kwargs['episode']
			if ("actor" in kwargs): self.local.db_instance.actor = Binary.utf8(kwargs['actor'])
			if ("author" in kwargs): self.local.db_instance.author = Binary.utf8(kwargs['author'])
			if ("director" in kwargs): self.local.db_instance.director = Binary.utf8(kwargs['director'])
			if ("producer" in kwargs): self.local.db_instance.producer = Binary.utf8(kwargs['producer'])
			if ("publisher" in kwargs): self.local.db_instance.publisher = Binary.utf8(kwargs['publisher'])
			if ("width" in kwargs): self.local.db_instance.width = kwargs['width']
			if ("height" in kwargs): self.local.db_instance.height = kwargs['height']
			if ("codec" in kwargs): self.local.db_instance.codec = kwargs['codec']
			if ("bitrate" in kwargs): self.local.db_instance.bitrate = kwargs['bitrate']
			if ("bpp" in kwargs): self.local.db_instance.bpp = kwargs['bpp']
			if ("encoder" in kwargs): self.local.db_instance.encoder = Binary.utf8(kwargs['encoder'])
		#
	#
#

##j## EOF