# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.XMSMediaReceiverRegistrar
"""
"""n// NOTE
----------------------------------------------------------------------------
MediaProvider
A device centric multimedia solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?mp;core

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
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.pas.controller.abstract_request import AbstractRequest
from dNG.pas.data.upnp.device import Device
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.module.named_loader import NamedLoader
from .abstract_service import AbstractService

class XMSMediaReceiverRegistrar(AbstractService):
#
	"""
Implementation for "urn:microsoft.com:service:X_MS_MediaReceiverRegistrar:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	def is_authorized(self, device_id = ""):
	#
		"""
Returns true for all devices previously processed.

:return: (int) True if the device is known
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.is_authorized({1})- (#echo(__LINE__)#)".format(self, device_id))
		_return = UpnpException("pas_http_core_403", 801)

		upnp_control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")

		if (device_id == ""):
		#
			request = AbstractRequest.get_instance()
			client_host = (None if (request == None) else request.get_client_host())

			if (client_host != None): _return = (upnp_control_point.rootdevice_get_for_host(client_host) != None)
		#
		else: _return = (upnp_control_point.rootdevice_get(Device.get_identifier(device_id)) != None)

		return _return
	#

	def is_validated(self, device_id = ""):
	#
		"""
Returns true for all devices previously processed.

:return: (int) True if the device is known
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.is_validated({1})- (#echo(__LINE__)#)".format(self, device_id))
		return (False if (self.is_authorized(device_id)) else UpnpException("pas_http_core_403", 801))
	#

	def register_device(self, register_input):
	#
		"""
Returns true for all devices previously processed.

:return: (int) True if the device is known
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.register_device(register_input)- (#echo(__LINE__)#)".format(self))
		return UpnpException("pas_http_core_500", 501)
	#

	def init_service(self, device, service_id = None, configid = None):
	#
		"""
Initialize a host service.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		if (service_id == None): service_id = "X_MS_MediaReceiverRegistrar"
		AbstractService.init_service(self, device, service_id, configid)

		self.actions = {
			"IsAuthorized": {
				"argument_variables": [ { "name": "DeviceID", "variable": "A_ARG_TYPE_DeviceID" } ],
				"return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
				"result_variables": [ ]
			},
			"RegisterDevice": {
				"argument_variables": [ { "name": "RegisterInput", "variable": "A_ARG_TYPE_GenericData" } ],
				"return_variable": { "name": "RegisterResponse", "variable": "A_ARG_TYPE_GenericData" },
				"result_variables": [ ]
			},
			"IsValidated": {
				"argument_variables": [ { "name": "DeviceID", "variable": "A_ARG_TYPE_DeviceID" } ],
				"return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
				"result_variables": [ ]
			}
		}

		self.service_id = service_id
		self.spec_major = 1
		self.spec_minor = 1
		self.type = "X_MS_MediaReceiverRegistrar"
		self.upnp_domain = "microsoft.com"
		self.version = "1"

		self.variables = {
			"A_ARG_TYPE_DeviceID": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_Result": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "boolean"
			},
			"AuthorizationGrantedUpdateID": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"AuthorizationDeniedUpdateID": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			# Unused but required
			"A_ARG_TYPE_UpdateID": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"A_ARG_TYPE_GenericData": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "bin.base64"
			},
			"ValidationRevokedUpdateID": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"ValidationSucceededUpdateID": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			}
		}

		return True
	#
#

##j## EOF