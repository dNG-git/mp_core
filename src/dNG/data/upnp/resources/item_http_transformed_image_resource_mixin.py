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

from dNG.data.text.link import Link

class ItemHttpTransformedImageResourceMixin(object):
#
	"""
"ItemHttpTransformedImageResourceMixin" uses the UPnP service "image" to
return a transformed UPnP image resource.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	TRANSFORMATION_ACTION = "transformed_resource"
	"""
@TODO: Fixme
	"""

	def __init__(self):
	#
		"""
Constructor __init__(ItemHttpTransformedImageResourceMixin)

:since: v0.2.00
		"""

		self.transformation_mimetype = None
		"""
DLNA "ORG_PN" value
		"""
		self.transformation_depth = None
		"""
DLNA "ORG_PN" value
		"""
		self.transformation_height = None
		"""
DLNA "ORG_PN" value
		"""
		self.transformation_width = None
		"""
DLNA "ORG_PN" value
		"""

		self.mimeclass = "image"
	#

	def get_mimetype(self):
	#
		"""
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class
:since:  v0.2.00
		"""

		return ("application/octet-stream" if (self.transformation_mimetype is None) else self.transformation_mimetype)
	#

	def _get_transformed_image_metadata(self):
	#
		"""
Returns specific metadata related the transformed image if prerequisites
are matched.

:return: (dict) Transformed image metadata
:since:  v0.2.00
		"""

		_return = { }

		if (self.transformation_width is not None
		    and self.transformation_height is not None
		   ): _return['resolution'] = "{0:d}x{1:d}".format(self.transformation_width, self.transformation_height)

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		self.content = [ ]

		if (self.transformation_mimetype is not None
		    and self.transformation_width is not None
		    and self.transformation_height is not None
		   ):
		#
			link_parameters = { "__virtual__": "/upnp/image",
			                    "a": self.__class__.TRANSFORMATION_ACTION,
			                    "dsd": { "urid": self.get_resource_id(),
			                             "umimetype": self.transformation_mimetype,
			                             "uwidth": self.transformation_width,
			                             "uheight": self.transformation_height
			                           }
			                  }

			if (self.transformation_depth is not None): link_parameters['dsd']['udepth'] = self.transformation_depth

			self.content.append(Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, link_parameters))

			_return = True
		#

		return _return
	#
#

##j## EOF