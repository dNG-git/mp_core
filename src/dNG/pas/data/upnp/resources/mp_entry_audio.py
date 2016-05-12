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

from dNG.pas.data.binary import Binary
from dNG.pas.data.media.audio import Audio
from dNG.pas.data.media.audio_metadata import AudioMetadata
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.database.instances.mp_upnp_audio_resource import MpUpnpAudioResource as _DbMpUpnpAudioResource
from dNG.pas.data.upnp.variable import Variable
from dNG.pas.runtime.not_implemented_class import NotImplementedClass
from .mp_entry import MpEntry

class MpEntryAudio(MpEntry):
#
	"""
"MpEntryAudio" is used for UPnP audio database entries.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	_DB_INSTANCE_CLASS = _DbMpUpnpAudioResource
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

		if (self.get_type() & MpEntryAudio.TYPE_CDS_ITEM == MpEntryAudio.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
		#
			entry_data = self.get_data_attributes("artist", "genre", "description", "album", "album_artist", "track_number")

			if (entry_data['album'] is not None): xml_resource.add_node("{0} upnp:album".format(xml_node_path), entry_data['album'])

			if (entry_data['album_artist'] is not None):
			#
				xml_resource.add_node("{0} upnp:albumArtist".format(xml_node_path), entry_data['album_artist'])
				xml_resource.add_node("{0} upnp:artist".format(xml_node_path), entry_data['album_artist'], { "role": "AlbumArtist" })
			#

			if (entry_data['artist'] is not None):
			#
				xml_resource.add_node("{0} dc:creator".format(xml_node_path), entry_data['artist'])
				xml_resource.add_node("{0} upnp:artist".format(xml_node_path), entry_data['artist'], { "role": "Performer" })
			#

			if (entry_data['description'] is not None): xml_resource.add_node("{0} dc:description".format(xml_node_path), entry_data['description'])
			if (entry_data['genre'] is not None): xml_resource.add_node("{0} upnp:genre".format(xml_node_path), entry_data['genre'])

			if (entry_data['track_number'] is not None):
			#
				xml_resource.add_node("{0} upnp:originalTrackNumber".format(xml_node_path),
				                      entry_data['track_number']
				                     )
			#
		#
	#

	def _append_stream_content_metadata(self, resource):
	#
		"""
Appends audio metadata to the given stream resource.

:since: v0.1.01
		"""

		# pylint: disable=star-args

		if (isinstance(resource, AbstractStream) and resource.is_supported("metadata")):
		#
			entry_data = self.get_data_attributes("size", "duration", "channels", "bitrate", "bps", "sample_frequency")
			data = { }

			if (entry_data['duration'] is not None): data['duration'] = Variable.get_upnp_duration(entry_data['duration'])
			if (entry_data['channels'] is not None): data['nrAudioChannels'] = entry_data['channels']

			if (entry_data['bitrate'] is not None): data['bitrate'] = int(entry_data['bitrate'] / 8)
			elif (entry_data['duration'] is not None and entry_data['size'] is not None): data['bitrate'] = int(entry_data['size'] / entry_data['duration'])

			if (entry_data['bps'] is not None): data['bitsPerSample'] = entry_data['bps']
			if (entry_data['sample_frequency'] is not None): data['sampleFrequency'] = entry_data['sample_frequency']

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

		if (self.get_type() & MpEntryAudio.TYPE_CDS_ITEM == MpEntryAudio.TYPE_CDS_ITEM and xml_resource.get_node(xml_node_path) is not None):
		#
			didl_fields = self.get_didl_fields()

			if (len(didl_fields) > 0):
			#
				if ("upnp:album" not in didl_fields): xml_resource.remove_node("{0} upnp:album".format(xml_node_path))
				if ("upnp:albumArtist" not in didl_fields): xml_resource.remove_node("{0} upnp:albumArtist".format(xml_node_path))
				if ("dc:creator" not in didl_fields): xml_resource.remove_node("{0} dc:creator".format(xml_node_path))
				if ("upnp:artist" not in didl_fields): xml_resource.remove_node("{0} upnp:artist".format(xml_node_path))
				if ("dc:description" not in didl_fields): xml_resource.remove_node("{0} dc:description".format(xml_node_path))
				if ("upnp:genre" not in didl_fields): xml_resource.remove_node("{0} upnp:genre".format(xml_node_path))
				if ("upnp:originalTrackNumber" not in didl_fields): xml_resource.remove_node("{0} upnp:originalTrackNumber".format(xml_node_path))
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

		if (self.type & MpEntryAudio.TYPE_CDS_ITEM == MpEntryAudio.TYPE_CDS_ITEM):
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

		if (self.type & MpEntryAudio.TYPE_CDS_ITEM == MpEntryAudio.TYPE_CDS_ITEM):
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

		if (self.type & MpEntryAudio.TYPE_CDS_ITEM == MpEntryAudio.TYPE_CDS_ITEM):
		#
			for resource in _return: self._append_stream_content_metadata(resource)
		#

		return _return
	#

	def refresh_metadata(self):
	#
		"""
Refresh metadata associated with this MpEntryAudio.

:since: v0.1.00
		"""

		with self:
		#
			MpEntry.refresh_metadata(self)

			encapsulated_resource = self.load_encapsulated_resource()

			if ((not issubclass(Audio, NotImplementedClass))
			    and encapsulated_resource is not None
			    and encapsulated_resource.is_filesystem_resource()
			    and encapsulated_resource.get_path() is not None
			   ): self._refresh_audio_metadata(encapsulated_resource.get_resource_id())
		#
	#

	def _refresh_audio_metadata(self, resource_url):
	#
		"""
Refresh metadata associated with this MpEntryAudio.

:since: v0.1.00
		"""

		audio = Audio()
		metadata = (audio.get_metadata() if (audio.open_url(resource_url)) else None)

		if (isinstance(metadata, AudioMetadata)):
		#
			self.set_data_attributes(title = metadata.get_title(),
			                         mimetype = metadata.get_mimetype(),
			                         metadata = metadata.get_json(),
			                         duration = metadata.get_length(),
			                         artist = metadata.get_artist(),
			                         genre = metadata.get_genre(),
			                         description = metadata.get_comment(),
			                         album = metadata.get_album(),
			                         album_artist = metadata.get_album_artist(),
			                         track_number = metadata.get_track(),
			                         codec = metadata.get_codec(),
			                         channels = metadata.get_channels(),
			                         bitrate = metadata.get_bitrate(),
			                         bps = metadata.get_bps(),
			                         sample_frequency = metadata.get_sample_rate()
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

			if ("duration" in kwargs): self.local.db_instance.duration = kwargs['duration']
			if ("artist" in kwargs): self.local.db_instance.artist = Binary.utf8(kwargs['artist'])
			if ("genre" in kwargs): self.local.db_instance.genre = Binary.utf8(kwargs['genre'])
			if ("description" in kwargs): self.local.db_instance.description = Binary.utf8(kwargs['description'])
			if ("album" in kwargs): self.local.db_instance.album = Binary.utf8(kwargs['album'])
			if ("album_artist" in kwargs): self.local.db_instance.album_artist = Binary.utf8(kwargs['album_artist'])
			if ("track_number" in kwargs): self.local.db_instance.track_number = kwargs['track_number']
			if ("codec" in kwargs): self.local.db_instance.codec = kwargs['codec']
			if ("channels" in kwargs): self.local.db_instance.channels = kwargs['channels']
			if ("bitrate" in kwargs): self.local.db_instance.bitrate = kwargs['bitrate']
			if ("bps" in kwargs): self.local.db_instance.bps = kwargs['bps']
			if ("sample_frequency" in kwargs): self.local.db_instance.sample_frequency = kwargs['sample_frequency']
			if ("encoder" in kwargs): self.local.db_instance.encoder = Binary.utf8(kwargs['encoder'])
		#
	#
#

##j## EOF