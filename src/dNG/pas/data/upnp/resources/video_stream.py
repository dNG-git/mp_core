# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.VideoStream
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

from .abstract_dlna_http_stream import AbstractDlnaHttpStream

class VideoStream(AbstractDlnaHttpStream):
#
	"""
"VideoStream" represents an UPnP object with the mime class "video".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

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

		_return = AbstractDlnaHttpStream.init_cds_id(self, _id, client_user_agent, update_id, deleted)

		if (_return):
		#
			self.dlna_content_features = "DLNA.ORG_OP={0:0>2x};DLNA.ORG_CI=0;DLNA.ORG_FLAGS={1:0>8x}000000000000000000000000".format(
				AbstractDlnaHttpStream.DLNA_SEEK_BYTES,
				(
					AbstractDlnaHttpStream.DLNA_0150 |
					AbstractDlnaHttpStream.DLNA_HTTP_STALLING |
					AbstractDlnaHttpStream.DLNA_BACKGROUND_TRANSFER |
					AbstractDlnaHttpStream.DLNA_STREAMING_TRANSFER
				)
			)
		#

		return _return
	#
#

##j## EOF