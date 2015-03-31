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

# pylint: disable=import-error,no-name-in-module

from os import path
import re

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.pas.data.mime_type import MimeType
from dNG.pas.data.media.image import Image
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.exception_log_trap import ExceptionLogTrap
from dNG.pas.runtime.not_implemented_class import NotImplementedClass
from .thumbnail_mixin import ThumbnailMixin

class ThumbnailResourceMixin(ThumbnailMixin):
#
	"""
"ThumbnailResourceMixin" provides thumbnail "res" entries for UPnP
resources.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def _append_generated_thumbnail_resources(self, resource_list):
	#
		"""
Appends generated thumbnail resources created when first accessed.

:param resource_list: UPnP resource list
:param thumbnail_file_path_name: Thumbnail file path and name

:since: v0.1.02
		"""

		icon_mimetypes = ( "image/png", "image/jpeg" )

		for icon_mimetype in icon_mimetypes:
		#
			camel_case_mimeclass = "".join([word.capitalize() for word in re.split("[\\W_]+", icon_mimetype)])
			resource_thumbnail = NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Thumbnail".format(camel_case_mimeclass), False)

			if (resource_thumbnail is not None
			    and resource_thumbnail.init_cds_id("upnp-thumbnail:///{0}".format(quote(self.get_resource_id())),
			                                       self.client_user_agent
			                                      )
			   ): resource_list.append(resource_thumbnail)
		#
	#

	def append_thumbnail_resources(self, resource_list, thumbnail_file_path_name):
	#
		"""
Appends thumbnail resources for the file path and name given.

:param resource_list: UPnP resource list
:param thumbnail_file_path_name: Thumbnail file path and name

:since: v0.1.02
		"""

		if (thumbnail_file_path_name is not None):
		#
			with ExceptionLogTrap("pas_upnp"):
			#
				if (self.is_thumbnail_transformation_supported()): self._append_generated_thumbnail_resources(resource_list)
				else: self._append_thumbnail_file_resource(resource_list, thumbnail_file_path_name)
			#
		#
	#

	def _append_thumbnail_file_resource(self, resource_list, thumbnail_file_path_name):
	#
		"""
Appends a file resource for the file path and name given.

:param resource_list: UPnP resource list
:param thumbnail_file_path_name: Thumbnail file path and name

:since: v0.1.02
		"""

		if (thumbnail_file_path_name is not None):
		#
			path_ext = path.splitext(thumbnail_file_path_name)[1]
			mimetype_definition = MimeType.get_instance().get(path_ext[1:])
			camel_case_mimeclass = "".join([word.capitalize() for word in re.split("[\\W_]+", mimetype_definition['type'])])

			resource_thumbnail = (None
			                      if (mimetype_definition is None) else
			                      NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Thumbnail".format(camel_case_mimeclass), False)
			                     )

			if (resource_thumbnail is not None
			    and resource_thumbnail.init_cds_id("file:///{0}".format(thumbnail_file_path_name), self.client_user_agent)
			   ): resource_list.append(resource_thumbnail)
		#
	#

	def is_thumbnail_transformation_supported(self):
	#
		"""
Returns true if thumbnail images can be created by transforming another
source image.

:return: (bool) True if supported
:since:  v0.1.02
		"""

		return (self.is_supported("thumbnail_file")
		        and (not issubclass(Image, NotImplementedClass))
		        and Image().is_supported("transformation")
		       )
	#
#

##j## EOF