# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.AudioMpegStream
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

from .abstract_stream import AbstractStream

class AudioMpegStream(AbstractStream):
#
	"""
"direct_resource" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

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

		_return = AbstractStream.init_cds_id(self, _id, client_user_agent, update_id)

		if (_return): self.didl_res_protocol = "http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP={0:0>2x};DLNA.ORG_FLAGS={1:0>8x}000000000000000000000000".format(AudioMpegStream.DLNA_SEEK_BYTES, AudioMpegStream.DLNA_STREAM | AudioMpegStream.DLNA_0150)
		return _return
	#
#

##j## EOF