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

from dNG.runtime.io_exception import IOException

from .item_dlna_http_resource import ItemDlnaHttpResource
from .item_http_transformed_image_resource_mixin import ItemHttpTransformedImageResourceMixin

class AbstractItemDlnaHttpThumbnailResource(ItemDlnaHttpResource, ItemHttpTransformedImageResourceMixin):
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

	TRANSFORMATION_ACTION = "resource_thumbnail"
	"""
@TODO: Fixme
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractItemDlnaHttpThumbnailResource)

:since: v0.2.00
		"""

		ItemDlnaHttpResource.__init__(self)
		ItemHttpTransformedImageResourceMixin.__init__(self)

		self.dlna_org_pn = None
		"""
DLNA "ORG_PN" value
		"""

		self.use_parent_resource_data = False

		self.supported_features['thumbnail_source_vfs_url'] = True
	#

	def get_metadata(self, **kwargs):
	#
		"""
Sets additional metadata used for "_add_metadata_to_didl_xml_node()" of this
UPnP resource.

:since: v0.2.00
		"""

		_return = ItemDlnaHttpResource.get_metadata(self)
		_return.update(self._get_transformed_image_metadata())

		return _return
	#

	get_mimetype = ItemHttpTransformedImageResourceMixin.get_mimetype
	"""
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class
:since:  v0.2.00
	"""

	def get_thumbnail_source_vfs_url(self, generate_thumbnail = True):
	#
		"""
Returns the thumbnail source VFS URL if applicable.

:param generate_thumbnail: True to generate a missing thumbnail on the fly

:return: (str) Thumbnail source VFS URL; None if no thumbnail file exist
:since:  v0.2.00
		"""

		self._init_parent_resource()

		if (self.parent_resource is None
		    or (not self.parent_resource.is_supported("thumbnail_source_vfs_url"))
		   ): raise IOException("Requested the thumbnail source VFS for an unsupported UPnP resource")

		return self.parent_resource.get_thumbnail_source_vfs_url(generate_thumbnail)
	#

	_init_content = ItemHttpTransformedImageResourceMixin._init_content
	"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
	"""

	def _refresh_dlna_content_features(self):
	#
		"""
Initializes the UPnP DLNA content features variable.

:since: v0.2.00
		"""

		ItemDlnaHttpResource._refresh_dlna_content_features(self)

		if (self.dlna_org_pn is not None):
		#
			self.dlna_content_features = "DLNA.ORG_PN={0};{1}".format(self.dlna_org_pn,
			                                                          self.dlna_content_features
			                                                         )
		#
	#
#

##j## EOF