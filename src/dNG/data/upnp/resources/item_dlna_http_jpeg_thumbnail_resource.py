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

from .abstract_item_dlna_http_thumbnail_resource import AbstractItemDlnaHttpThumbnailResource

class ItemDlnaHttpJpegThumbnailResource(AbstractItemDlnaHttpThumbnailResource):
#
	"""
"ItemDlnaHttpJpegThumbnailResource" represents an UPnP "JPEG_TN" thumbnail
resource.

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
Constructor __init__(ItemDlnaHttpJpegThumbnailResource)

:since: v0.2.00
		"""

		AbstractItemDlnaHttpThumbnailResource.__init__(self)

		self.dlna_org_pn = "JPEG_TN"
		self.mimetype = "image/jpeg"

		self.transformation_mimetype = "image/jpeg"
		self.transformation_width = 160
		self.transformation_height = 160
		self.transformation_depth = 24
	#
#

##j## EOF