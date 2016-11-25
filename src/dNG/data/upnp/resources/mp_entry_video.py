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

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.data.binary import Binary
from dNG.data.cache.file import File as CacheFile
from dNG.data.media.container_metadata import ContainerMetadata
from dNG.data.media.video_implementation import VideoImplementation
from dNG.data.upnp.variable import Variable
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.database.instances.mp_upnp_video_resource import MpUpnpVideoResource as _DbMpUpnpVideoResource
from dNG.runtime.exception_log_trap import ExceptionLogTrap

from .mp_entry import MpEntry

class MpEntryVideo(MpEntry):
#
	"""
"MpEntryVideo" is used for UPnP video database entries.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	_DB_INSTANCE_CLASS = _DbMpUpnpVideoResource
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""
	METADATA_MIN_SIZE = 131072
	"""
Minimum underlying VFS object size before trying to read video metadata
	"""

	def __init__(self, db_instance = None, user_agent = None, didl_fields = None):
	#
		"""
Constructor __init__(MpEntryVideo)

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

	def _generate_thumbnail_source(self):
	#
		"""
Generates a cached thumbnail source and returns its VFS URL.

:return: (str) Thumbnail source VFS URL; None if no thumbnail file exist
:since:  v0.2.00
		"""

		thumbnail_file = None

		with ExceptionLogTrap("pas_upnp"):
		#
			vfs_url = self.get_vfs_url()
			video = VideoImplementation.get_instance()

			if (vfs_url != ""):
			#
				if (vfs_url[:2] == "x-"): vfs_url = MpEntryVideo._get_http_upnp_stream_url(self.get_resource_id())
				# @TODO: Create hook to decide when to use the HTTP approach
				thumbnail_buffer = (video.get_thumbnail() if (video.open_url(vfs_url)) else None)
			#

			if (thumbnail_buffer is not None):
			#
				thumbnail_vfs_url = self._get_thumbnail_vfs_url()

				thumbnail_file = CacheFile()
				thumbnail_file.set_data_attributes(resource = thumbnail_vfs_url)
				thumbnail_file.write(thumbnail_buffer.read())
				thumbnail_file.save()
			#
		#

		return (None
		        if (thumbnail_file is None) else
		        thumbnail_file.get_vfs_url()
		       )
	#

	def get_thumbnail_source_vfs_url(self, generate_thumbnail = True):
	#
		"""
Returns the thumbnail source VFS URL if applicable.

:param generate_thumbnail: True to generate a missing thumbnail on the fly

:return: (str) Thumbnail source VFS URL; None if no thumbnail file exist
:since:  v0.2.00
		"""

		_return = None

		with self:
		#
			thumbnail_vfs_url = self._get_thumbnail_vfs_url()

			try: _return = CacheFile.load_resource(thumbnail_vfs_url).get_vfs_url()
			except NothingMatchedException: pass
		#

		if (_return is None and generate_thumbnail): _return = self._generate_thumbnail_source()

		return _return
	#

	def _get_thumbnail_vfs_url(self):
	#
		"""
Returns the thumbnail VFS URL used to store the thumbnail source.

:return: (str) Thumbnail VFS URL
:since:  v0.2.00
		"""

		with self: return "x-upnp-thumbnail:///{0}".format(quote(self.get_resource_id(), "/"))
	#

	def get_upnp_resource_metadata(self):
	#
		"""
Returns the metadata of the original source UPnP resource.

:return: (dict) Metadata of the original source UPnP resource
:since:  v0.2.00
		"""

		_return = { }

		entry_data = self.get_data_attributes("size", "duration", "width", "height", "bitrate", "bpp")

		if (entry_data['duration'] is not None): _return['duration'] = Variable.get_upnp_duration(entry_data['duration'])

		if (entry_data['width'] is not None
		    and entry_data['height'] is not None
		   ): _return['resolution'] = "{0:d}x{1:d}".format(entry_data['width'], entry_data['height'])

		if (entry_data['bitrate'] is not None): _return['bitrate'] = int(entry_data['bitrate'] / 8)
		elif (entry_data['duration'] is not None and entry_data['size'] is not None): _return['bitrate'] = int(entry_data['size'] / entry_data['duration'])

		if (entry_data['bpp'] is not None): _return['colorDepth'] = entry_data['bpp']

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryVideo.

:since: v0.2.00
		"""

		MpEntry.refresh_metadata(self)

		if (VideoImplementation.get_class() is not None):
		#
			if (self.get_size() > MpEntryVideo.METADATA_MIN_SIZE): self._refresh_video_metadata(self.get_vfs_url())
		#
	#

	def _refresh_video_metadata(self, vfs_url):
	#
		"""
Refresh metadata associated with this MpEntryVideo.

:param vfs_url: UPnP resource VFS URL

:since: v0.2.00
		"""

		metadata = None
		video = VideoImplementation.get_instance()

		if (vfs_url != ""):
		#
			if (vfs_url[:2] == "x-"): vfs_url = MpEntryVideo._get_http_upnp_stream_url(self.get_resource_id())
			# @TODO: Create hook to decide when to use the HTTP approach
			metadata = (video.get_metadata() if (video.open_url(vfs_url)) else None)
		#

		if (isinstance(metadata, ContainerMetadata) and metadata.get_video_streams_count() == 1):
		#
			self.mimeclass = metadata.get_mimeclass()
			self.mimetype = metadata.get_mimetype()

			video_metadata = metadata.get_video_streams(0)

			with self:
			#
				self.set_data_attributes(mimeclass = self.mimeclass,
				                         mimetype = self.mimetype,
				                         metadata = metadata.get_json(),
				                         duration = metadata.get_length(),
				                         width = video_metadata.get_width(),
				                         height = video_metadata.get_height(),
				                         codec = video_metadata.get_codec(),
				                         bitrate = video_metadata.get_bitrate(),
				                         bpp = video_metadata.get_bpp()
				                        )
			#

			if (self.get_thumbnail_source_vfs_url(False) is None): self._generate_thumbnail_source()
		#
	#

	def _rewrite_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to manipulate DIDL metadata for the client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since: v0.2.00
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

:since: v0.2.00
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