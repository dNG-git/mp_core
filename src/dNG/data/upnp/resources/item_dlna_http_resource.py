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

from .abstract_item_http_resource import AbstractItemHttpResource
from .dlna_item_resource_mixin import DlnaItemResourceMixin

class ItemDlnaHttpResource(DlnaItemResourceMixin, AbstractItemHttpResource):
#
	"""
"ItemDlnaHttpResource" represents an UPnP object with the mime class "video".

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(DlnaItemResourceMixin)

:since: v0.2.00
		"""

		AbstractItemHttpResource.__init__(self)
		DlnaItemResourceMixin.__init__(self)
	#

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.
:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources
:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
		"""

		_return = AbstractItemHttpResource.init_cds_id(self, _id, client_user_agent, deleted)
		if (_return): self._refresh_dlna_information()

		return _return
	#

	def _refresh_dlna_content_features(self):
	#
		"""
Initializes the UPnP DLNA content features variable.

:since: v0.2.00
		"""

		dlna_content_features = "DLNA.ORG_OP={0:0>2x};DLNA.ORG_CI=0;DLNA.ORG_FLAGS={1:0>8x}000000000000000000000000"

		mimeclass = self.get_mimeclass()

		if (mimeclass in ( "audio", "video" )):
		#
			self.dlna_content_features = dlna_content_features.format(ItemDlnaHttpResource.DLNA_SEEK_BYTES,
			                                                          (ItemDlnaHttpResource.DLNA_0150
			                                                           | ItemDlnaHttpResource.DLNA_HTTP_STALLING
			                                                           | ItemDlnaHttpResource.DLNA_BACKGROUND_TRANSFER
			                                                           | ItemDlnaHttpResource.DLNA_STREAMING_TRANSFER
			                                                          )
			                                                         )
		#
		elif (mimeclass == "image"):
		#
			self.dlna_content_features = dlna_content_features.format(ItemDlnaHttpResource.DLNA_SEEK_BYTES,
			                                                          (ItemDlnaHttpResource.DLNA_0150
			                                                           | ItemDlnaHttpResource.DLNA_HTTP_STALLING
			                                                           | ItemDlnaHttpResource.DLNA_BACKGROUND_TRANSFER
			                                                           | ItemDlnaHttpResource.DLNA_INTERACTIVE_TRANSFER
			                                                          )
			                                                         )
		#
		else:
		#
			self.dlna_content_features = dlna_content_features.format(ItemDlnaHttpResource.DLNA_SEEK_BYTES,
			                                                          (ItemDlnaHttpResource.DLNA_0150
			                                                           | ItemDlnaHttpResource.DLNA_HTTP_STALLING
			                                                          )
			                                                         )
		#
	#

	def _refresh_dlna_information(self):
	#
		"""
Refreshes all DLNA information of this UPnP item DLNA HTTP resource.

:since: v0.2.00
		"""

		self._refresh_dlna_content_features()
		self._refresh_dlna_res_protocol()
	#

	def _refresh_dlna_res_protocol(self):
	#
		"""
Initializes the UPnP DLNA res protocol variable.

:since: v0.2.00
		"""

		self.didl_res_protocol = "http-get:*:{0}:{1}".format(self.get_mimetype(),
		                                                     self.get_dlna_content_features()
		                                                    )
	#

	def set_mimeclass(self, mimeclass):
	#
		"""
Sets the UPnP resource mime class.

:param mimeclass: UPnP resource mime class

:since: v0.2.00
		"""

		AbstractItemHttpResource.set_mimeclass(self, mimeclass)
		self._refresh_dlna_information()
	#

	def set_mimetype(self, mimetype):
	#
		"""
Sets the UPnP resource mime type.
:param mimetype: UPnP resource mime type
:since: v0.2.00
		"""

		AbstractItemHttpResource.set_mimetype(self, mimetype)
		self._refresh_dlna_res_protocol()
	#
#

##j## EOF