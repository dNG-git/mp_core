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

from dNG.data.xml_resource import XmlResource
from dNG.plugins.hook import Hook

class FeatureListMixin(object):
#
	"""
"getFeatureList" mixin to minimize duplicated code for this common UPnP
method.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def _get_feature_list(self, hook_class):
	#
		"""
Returns the list of supported UPnP ContentDirectory features.

:return: (str) FeatureList XML document
:since:  v0.2.00
		"""

		xml_resource = XmlResource()
		xml_resource.set_cdata_encoding(False)

		xml_resource.add_node("Features",
		                      attributes = { "xmlns": "urn:schemas-upnp-org:av:avs",
		                                     "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
		                                     "xsi:schemaLocation": "urn:schemas-upnp-org:av:avs http://www.upnp.org/schemas/av/avs.xsd"
		                                   }
		                     )

		xml_resource.set_cached_node("Features")

		Hook.call("{0}.getFeatures".format(hook_class), xml_resource = xml_resource)

		return "<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_resource.export_cache(True))
	#
#

##j## EOF