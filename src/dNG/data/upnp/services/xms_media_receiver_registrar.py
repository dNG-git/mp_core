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

import socket

from dNG.controller.abstract_request import AbstractRequest
from dNG.data.upnp.gena_event import GenaEvent
from dNG.data.upnp.upnp_exception import UpnpException
from dNG.net.upnp.control_point import ControlPoint

from .abstract_service import AbstractService

class XMSMediaReceiverRegistrar(AbstractService):
#
	"""
Implementation for "urn:microsoft.com:service:X_MS_MediaReceiverRegistrar:1".

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	def _handle_gena_registration(self, sid):
	#
		"""
Handles the registration of an UPnP device at GENA with the given SID.

:param sid: UPnP SID

:since: v0.2.00
		"""

		event = GenaEvent(GenaEvent.TYPE_PROPCHANGE)

		event.set_variables(AuthorizationDeniedUpdateID = 1,
		                    AuthorizationGrantedUpdateID = 1,
		                    ValidationRevokedUpdateID = 1,
		                    ValidationSucceededUpdateID = 1
		                   )

		event.set_sid(sid)
		event.set_usn(self.get_usn())
		event.schedule()
	#

	def init_host(self, device, service_id = None, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
		"""

		self.type = "X_MS_MediaReceiverRegistrar"
		self.upnp_domain = "microsoft.com"
		self.version = "1"

		if (service_id is None): service_id = "X_MS_MediaReceiverRegistrar"
		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.2.00
		"""

		is_authorized = { "argument_variables": [ { "name": "DeviceID", "variable": "A_ARG_TYPE_DeviceID" } ],
		                  "return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
		                  "result_variables": [ ]
		                }

		is_validated = { "argument_variables": [ { "name": "DeviceID", "variable": "A_ARG_TYPE_DeviceID" } ],
		                 "return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
		                 "result_variables": [ ]
		               }

		register_device = { "argument_variables": [ { "name": "RegisterInput", "variable": "A_ARG_TYPE_GenericData" } ],
		                    "return_variable": { "name": "RegisterResponse", "variable": "A_ARG_TYPE_GenericData" },
		                    "result_variables": [ ]
		                  }

		self.actions = { "IsAuthorized": is_authorized,
		                 "RegisterDevice": register_device,
		                 "IsValidated": is_validated
		               }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.2.00
		"""

		self.variables = { "A_ARG_TYPE_DeviceID": { "is_sending_events": True,
		                                            "is_multicasting_events": False,
		                                            "type": "string"
		                                          },
		                   "A_ARG_TYPE_Result": { "is_sending_events": False,
		                                          "is_multicasting_events": False,
		                                          "type": "boolean"
		                                        },
		                   "AuthorizationGrantedUpdateID": { "is_sending_events": True,
		                                                     "is_multicasting_events": False,
		                                                     "type": "ui4"
		                                                   },
		                   "AuthorizationDeniedUpdateID": { "is_sending_events": True,
		                                                    "is_multicasting_events": False,
		                                                    "type": "ui4"
		                                                  },
		                   "A_ARG_TYPE_UpdateID": { "is_sending_events": False, # Unused but required
		                                            "is_multicasting_events": False,
		                                            "type": "ui4"
		                                          },
		                   "A_ARG_TYPE_GenericData": { "is_sending_events": False,
		                                               "is_multicasting_events": False,
		                                               "type": "bin.base64"
		                                             },
		                   "ValidationRevokedUpdateID": { "is_sending_events": False,
		                                                  "is_multicasting_events": False,
		                                                  "type": "ui4"
		                                                },
		                   "ValidationSucceededUpdateID": { "is_sending_events": False,
		                                                    "is_multicasting_events": False,
		                                                    "type": "ui4"
		                                                  }
		                 }
	#

	def is_authorized(self, device_id = ""):
	#
		"""
Returns true for all allowed devices or if the given device ID is matched.

:return: (mixed) True if the device is known; UpnpException if the source
         can not be identified
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.is_authorized({1})- (#echo(__LINE__)#)", self, device_id, context = "mp_server")
		_return = UpnpException("pas_http_core_403", 801)

		upnp_control_point = ControlPoint.get_instance()

		if (device_id == ""):
		#
			request = AbstractRequest.get_instance()
			client_host = (None if (request is None) else request.get_client_host())

			if (client_host is not None):
			#
				_return = False
				ip_address_list = socket.getaddrinfo(client_host, None, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

				for ip_address_data in ip_address_list:
				#
					ip = ip_address_data[4][0]

					if (upnp_control_point.is_ip_allowed(ip)):
					#
						_return = True
						break
					#
				#
			#
		#
		else: _return = (upnp_control_point.get_rootdevice(XMSMediaReceiverRegistrar.get_identifier(device_id)) is not None)

		return _return
	#

	def is_validated(self, device_id = ""):
	#
		"""
Returns true for all devices previously processed.

:return: (int) True if the device is known
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.is_validated({1})- (#echo(__LINE__)#)", self, device_id, context = "mp_server")
		return (True if (self.is_authorized(device_id)) else UpnpException("pas_http_core_403", 801))
	#

	def register_device(self, register_input):
	#
		"""
Returns true for all devices previously processed.

:return: (int) True if the device is known
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.register_device()- (#echo(__LINE__)#)", self, context = "mp_server")
		return UpnpException("pas_http_core_500", 501)
	#

	def query_state_variable(self, var_name):
	#
		"""
UPnP call for "QueryStateVariable".

:param var_name: Variable to be returned

:return: (mixed) Variable value
:since:  v0.2.00
		"""

		if (var_name not in ( "AuthorizationGrantedUpdateID",
		                      "AuthorizationDeniedUpdateID",
		                      "ValidationRevokedUpdateID",
		                      "ValidationSucceededUpdateID"
		                    )
		   ): raise UpnpException("pas_http_core_404", 404)

		return "1"
	#
#

##j## EOF