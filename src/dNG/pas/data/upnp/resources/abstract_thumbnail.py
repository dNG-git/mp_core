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

try: from urllib.parse import unquote, urlsplit
except ImportError:
#
	from urllib import unquote
	from urlparse import urlsplit
#

from dNG.pas.data.text.link import Link
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.io_exception import IOException
from .abstract_transformed_image_stream import AbstractTransformedImageStream

class AbstractThumbnail(AbstractTransformedImageStream):
#
	"""
"AbstractThumbnail" represents an UPnP thumbnail object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	SCHEME = "upnp-thumbnail"
	"""
URL scheme for transformed images
	"""

	def get_transformed_image_settings(self):
	#
		"""
Returns the transformation settings.

:return: (dict) Transformation settings
:since:  v0.1.02
		"""

		_return = AbstractTransformedImageStream.get_transformed_image_settings(self)

		customized_settings = Hook.call("dNG.pas.upnp.resources.Thumbnail.getGeneratedSettings",
		                                settings = _return,
		                                client_user_agent = self.client_user_agent
		                               )

		if (customized_settings is not None): _return = customized_settings
		return _return
	#

	def get_transformed_image_url(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.02
		"""

		if (self.transformed_source_resource_id is None): raise IOException("Source resource ID of transformed image URL is invalid")

		transformation_settings = self.get_transformed_image_settings()

		link_parameters = { "__virtual__": "/upnp/image",
		                    "a": "resource_thumbnail",
		                    "dsd": { "urid": self.transformed_source_resource_id,
		                             "umimetype": transformation_settings['mimetype'],
		                             "uwidth": transformation_settings['width'],
		                             "uheight": transformation_settings['height'],
		                             "utype_id": self.__class__.__name__
		                           }
		                  }

		return Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, link_parameters)
	#

	def _init_transformed_image_resource(self, deleted = False):
	#
		"""
Initialize a UPnP CDS resource instance.

:param _id: UPnP CDS ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		_return = False

		source_resource_id = None
		url_elements = urlsplit(self.resource_id)

		if (url_elements.scheme == "upnp-thumbnail"):
		#
			source_resource_id = self.get_parent_resource_id()
			if (source_resource_id is None): source_resource_id = unquote(url_elements.path[1:])
		#

		source_resource = (None
		                   if (source_resource_id is None) else
		                   Resource.load_cds_id(source_resource_id, self.client_user_agent, deleted = deleted)
		                  )

		if (source_resource is not None and source_resource.is_supported("thumbnail_file")):
		#
			self.name = source_resource.get_name()

			self.transformed_source_path = source_resource.get_thumbnail_file_path_name()
			self.transformed_source_resource_id = source_resource_id

			_return = AbstractTransformedImageStream._init_transformed_image_resource(self, deleted)
		#

		return _return
	#
#

##j## EOF