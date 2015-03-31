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

from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.services.abstract_service import AbstractService

class ApiEndpointService(AbstractService):
#
	"""
Implementation for "urn:schemas-mediaprovider-net:service:ApiEndpointService:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def get_configuration(self, hook, api_version):
	#
		"""
Returns ApiEndpoint settings based on the given API version.

:param api_version: API version requested

:return: (dict) ApiEndpoint settings
:since:  v0.1.02
		"""

		raise UpnpException("core_unsupported_command")
	#

	def init_host(self, device, service_id = None, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		self.service_id = service_id
		self.type = "ApiEndpointService"
		self.upnp_domain = "schemas-mediaprovider-net"
		self.version = "1"

		if (service_id is None): service_id = "ApiEndpointService"
		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.1.02
		"""

		get_configuration = { "argument_variables": [ { "name": "ApiVersion", "variable": "A_ARG_TYPE_ApiVersion" } ],
		                      "return_variable": { "name": "EndpointData", "variable": "A_ARG_TYPE_Json" },
		                      "result_variables": [ ]
		                    }

		self.actions = { "GetConfiguration": get_configuration }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.1.02
		"""

		self.variables = { "A_ARG_TYPE_ApiVersion": { "is_sending_events": False,
		                                              "is_multicasting_events": False,
		                                              "type": "ui8"
		                                            },
		                   "A_ARG_TYPE_Json": { "is_sending_events": False,
		                                        "is_multicasting_events": False,
		                                        "type": "string",
		                                        "value": ""
		                                      }
		                 }
	#
#

##j## EOF