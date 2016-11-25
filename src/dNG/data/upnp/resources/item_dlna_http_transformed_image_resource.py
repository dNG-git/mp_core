# -*- coding: utf-8 -*-

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

from .item_dlna_http_resource import ItemDlnaHttpResource
from .item_http_transformed_image_resource_mixin import ItemHttpTransformedImageResourceMixin

class ItemDlnaHttpTransformedImageResource(ItemDlnaHttpResource, ItemHttpTransformedImageResourceMixin):
    """
"ItemDlnaHttpTransformedImageResource" represents an UPnP image resource
most likely with a changed resolution.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(ItemDlnaThumbnailHttpResource)

:since: v0.2.00
        """

        ItemDlnaHttpResource.__init__(self)
        ItemHttpTransformedImageResourceMixin.__init__(self)

        self.use_parent_resource_data = False
    #

    def get_metadata(self, **kwargs):
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

    def init_cds_id(self, _id, client_user_agent = None, deleted = False):
        """
Initialize a UPnP resource by CDS ID.
:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources
:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
        """

        _return = ItemDlnaHttpResource.init_cds_id(self, _id, client_user_agent, deleted)

        if (_return):
            self._init_parent_resource()

            if (self.parent_resource is None
                or (not self.parent_resource.get_mimeclass() == "image")
               ): _return = False
        #

        return _return
    #

    _init_content = ItemHttpTransformedImageResourceMixin._init_content
    """
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
    """
#
