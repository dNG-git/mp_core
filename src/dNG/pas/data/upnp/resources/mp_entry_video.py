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
from dNG.pas.runtime.exception_log_trap import ExceptionLogTrap
try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.pas.data.binary import Binary
from dNG.pas.data.cache.file import File as CacheFile
from dNG.pas.data.media.container_metadata import ContainerMetadata
from dNG.pas.data.media.video import Video
from dNG.pas.data.upnp.variable import Variable
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
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
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	_DB_INSTANCE_CLASS = _DbMpUpnpVideoResource
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

		if (self.get_type() & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
		#
			entry_data = self.get_data_attributes("title", "description", "genre", "series", "actor", "author", "director", "producer", "publisher")

			if (entry_data['actor'] is not None): xml_resource.add_node("{0} upnp:actor".format(xml_node_path), entry_data['actor'])
			if (entry_data['author'] is not None): xml_resource.add_node("{0} upnp:author".format(xml_node_path), entry_data['author'])
			if (entry_data['description'] is not None): xml_resource.add_node("{0} dc:description".format(xml_node_path), entry_data['description'])

			if (entry_data['director'] is not None):
			#
				xml_resource.add_node("{0} dc:creator".format(xml_node_path), entry_data['director'])
				xml_resource.add_node("{0} upnp:director".format(xml_node_path), entry_data['director'])
			#

			if (entry_data['genre'] is not None): xml_resource.add_node("{0} upnp:genre".format(xml_node_path), entry_data['genre'])
			if (entry_data['producer'] is not None): xml_resource.add_node("{0} upnp:producer".format(xml_node_path), entry_data['producer'])
			if (entry_data['publisher'] is not None): xml_resource.add_node("{0} dc:publisher".format(xml_node_path), entry_data['publisher'])
			if (entry_data['series'] is not None): xml_resource.add_node("{0} upnp:seriesTitle".format(xml_node_path), entry_data['series'])
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

			if (entry_data['duration'] is not None): data['duration'] = Variable.get_upnp_duration(entry_data['duration'])

			if (entry_data['width'] is not None
			    and entry_data['height'] is not None
			   ): data['resolution'] = "{0:d}x{1:d}".format(entry_data['width'], entry_data['height'])

			if (entry_data['bitrate'] is not None): data['bitrate'] = int(entry_data['bitrate'] / 8)
			elif (entry_data['duration'] is not None and entry_data['size'] is not None): data['bitrate'] = int(entry_data['size'] / entry_data['duration'])

			if (entry_data['bpp'] is not None): data['colorDepth'] = entry_data['bpp']

			if (len(data) > 0): resource.set_metadata(**data)
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

:since:  v0.1.01
		"""

		MpEntry._filter_metadata_of_didl_xml_node(self, xml_resource, xml_node_path)

		if (self.get_type() & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
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
				if ("upnp:programTitle" not in didl_fields): xml_resource.remove_node("{0} upnp:programTitle".format(xml_node_path))
				if ("dc:publisher" not in didl_fields): xml_resource.remove_node("{0} dc:publisher".format(xml_node_path))
				if ("upnp:seriesTitle" not in didl_fields): xml_resource.remove_node("{0} upnp:seriesTitle".format(xml_node_path))
				"""
					if ("upnp:episodeNumber" not in didl_fields): xml_resource.remove_node("{0} upnp:episodeNumber".format(xml_node_path))
					if ("upnp:episodeSeason" not in didl_fields): xml_resource.remove_node("{0} upnp:episodeSeason".format(xml_node_path))
				"""
			#
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

		if (self.type & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM):
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

		if (self.type & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM):
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

		if (self.type & MpEntryVideo.TYPE_CDS_ITEM == MpEntryVideo.TYPE_CDS_ITEM):
		#
			for resource in _return: self._append_stream_content_metadata(resource)
		#

		return _return
	#

	def get_thumbnail_file_path_name(self):
	#
		"""
Returns the thumbnail file path and name if applicable.

:return: (str) File path and name; None if no thumbnail file exist
:since:  v0.1.02
		"""

		_return = MpEntry.get_thumbnail_file_path_name(self)

		if (_return is None):
		#
			thumbnail_url = "upnp-thumbnail:///{0}".format(quote(self.get_resource_id()))

			with ExceptionLogTrap("pas_upnp"):
			#
				try:
				#
					cache_file = CacheFile.load_resource(thumbnail_url)
					_return = cache_file.get_path_name()
				#
				except NothingMatchedException: pass
			#
		#

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryVideo.

:since: v0.1.00
		"""

		with self:
		#
			MpEntry.refresh_metadata(self)

			encapsulated_resource = self.load_encapsulated_resource()

			is_video_metadata_refreshable = (encapsulated_resource is not None
			                                 and encapsulated_resource.is_filesystem_resource()
			                                 and encapsulated_resource.get_path() is not None
			                                )
		#

		if (is_video_metadata_refreshable): self._refresh_video_metadata(encapsulated_resource.get_resource_id())
	#

	def _refresh_video_metadata(self, resource_url):
	#
		"""
Refresh metadata associated with this MpEntryVideo.

:since: v0.1.00
		"""

		video = (None if (issubclass(Video, NotImplementedClass)) else Video())
		metadata = (video.get_metadata() if (video is not None and video.open_url(resource_url)) else None)

		if (isinstance(metadata, ContainerMetadata) and metadata.get_video_streams_count() == 1):
		#
			thumbnail_buffer = None
			video_metadata = metadata.get_video_streams(0)

			if (self.get_thumbnail_file_path_name() is None): thumbnail_buffer = video.get_thumbnail()

			with self:
			#
				self.set_data_attributes(mimeclass = metadata.get_mimeclass(),
				                         mimetype = metadata.get_mimetype(),
				                         metadata = metadata.get_json(),
				                         duration = metadata.get_length(),
				                         width = video_metadata.get_width(),
				                         height = video_metadata.get_height(),
				                         codec = video_metadata.get_codec(),
				                         bitrate = video_metadata.get_bitrate(),
				                         bpp = video_metadata.get_bpp()
				                        )

				thumbnail_url = "upnp-thumbnail:///{0}".format(quote(self.get_resource_id()))

				if (thumbnail_buffer is not None):
				#
					thumbnail_file = CacheFile()
					thumbnail_file.set_data_attributes(resource = thumbnail_url)
					thumbnail_file.write(thumbnail_buffer.read())
					thumbnail_file.save()
				#
			#
		#
	#

	def _rewrite_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to manipulate DIDL metadata for the client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		MpEntry._rewrite_metadata_of_didl_xml_node(self, xml_resource, xml_node_path)

		if (xml_resource.count_node("{0} upnp:seriesTitle".format(xml_node_path)) > 0):
		#
			title = xml_resource.get_node("{0} dc:title".format(xml_node_path))
			xml_resource.add_node("{0} upnp:programTitle".format(xml_node_path), title)
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