# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.AbstractDlnaStream
"""
"""n// NOTE
----------------------------------------------------------------------------
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
----------------------------------------------------------------------------
NOTE_END //n"""

from .http_block_stream import HttpBlockStream

class AbstractDlnaHttpStream(HttpBlockStream):
#
	"""
This abstract class provides all constants required for DLNA 1.50 compliant
HTTP streams.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	DLNA_0150 = 1048576
	"""
Flag for DLNA 1.50 compatibility.
	"""
	DLNA_BACKGROUND_TRANSFER = 4194304
	"""
Flag for background transfer mode.
	"""
	DLNA_INTERACTIVE_TRANSFER = 8388608
	"""
Flag for interactive transfer mode.
	"""
	DLNA_HTTP_STALLING = 2097152
	"""
Flag for the method of stalling the HTTP data flow on pause.
	"""
	DLNA_IS_CONTAINER = 268435456
	"""
Flag for container or playlist elements.
	"""
	DLNA_LOP_BYTES = 536870912
	"""
Flag for limited seek ability by byte range.
	"""
	DLNA_LOP_TIME = 1073741824
	"""
Flag for limited seek ability by time.
	"""
	DLNA_RSTP_PAUSE_SUPPORT = 33554432
	"""
Flag for streams.
	"""
	DLNA_S0_INCREASING = 134217728
	"""
Flag for stream with changing start time.
	"""
	DLNA_SEEK_BYTES = 1
	"""
Flag for seek ability by byte range.
	"""
	DLNA_SEEK_TIME = 2
	"""
Flag for seek ability by time.
	"""
	DLNA_SERVERSIDE_FLOW_CONTROL = 2147483648
	"""
Flag for server-side data flow control corresponding to the current
playback speed.
	"""
	DLNA_SN_INCREASING = 67108864
	"""
Flag for stream with changing end time.
	"""
	DLNA_STREAM = 16777216
	"""
Flag for streams.
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractStream)

:since: v0.1.00
		"""

		HttpBlockStream.__init__(self)

		self.dlna_content_features = "*"
		"""
UPnP DLNA content features
		"""

		self.supported_features['dlna_content_features'] = True
	#

	def dlna_get_content_features(self):
	#
		"""
Return the UPnP DLNA content features known used for the 4th-field.

:return: (str) UPnP DLNA compliant content features
:since:  v0.1.01
		"""

		return self.dlna_content_features
	#

	def init_cds_id(self, _id, client_user_agent = None, update_id = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		_return = HttpBlockStream.init_cds_id(self, _id, client_user_agent, update_id, deleted)

		if (_return):
		#
			self.dlna_content_features = "DLNA.ORG_OP={0:0>2x};DLNA.ORG_FLAGS={1:0>8x}000000000000000000000000".format(
				AbstractDlnaHttpStream.DLNA_SEEK_BYTES,
				AbstractDlnaHttpStream.DLNA_0150 | AbstractDlnaHttpStream.DLNA_HTTP_STALLING
			)

			self.didl_res_protocol = "http-get:*:{0}:{1}".format(
				self.get_mimetype(),
				self.dlna_content_features
			)
		#

		return _return
	#
#

##j## EOF