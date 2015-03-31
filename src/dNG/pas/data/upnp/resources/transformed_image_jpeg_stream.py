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

from .abstract_transformed_image_stream import AbstractTransformedImageStream

class TransformedImageJpegStream(AbstractTransformedImageStream):
#
	"""
"TransformedImageJpegStream" represents an transformed UPnP image object
with the mime type "image/jpeg".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(TransformedImageJpegStream)

:since: v0.1.02
		"""

		AbstractTransformedImageStream.__init__(self)

		self.mimetype = "image/jpeg"
	#

	def get_dlna_org_pn(self):
	#
		"""
Returns the DLNA "ORG_PN" value of the transformed image.

:return: (str) DLNA "ORG_PN" value
:since:  v0.1.02
		"""

		if (self.transformed_image_width <= 640
		    and self.transformed_image_width <= 480
		   ): _return = "JPEG_SM"
		elif (self.transformed_image_width <= 1024
		      and self.transformed_image_width <= 768
		     ): _return = "JPEG_MED"
		elif (self.transformed_image_width <= 4096
		      and self.transformed_image_height <= 4096
		     ): _return = "JPEG_LRG"
		else:
		#
			_return = "JPEG_RES_{0:d}_{1:d}".format(self.transformed_image_width,
			                                        self.transformed_image_height
			                                       )
		#

		return _return
	#
#

##j## EOF