# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from .abstract_service import AbstractService

class ConnectionManager(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:ConnectionManager:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def call_hook(self, hook, json_arguments):
	#
		"""
Calls the given hook and returns the result.

:return: (mixed) Data returned by the called hook
:since:  v0.1.00
		"""

		json_parser = direct_json_parser()
		arguments = ({ } if (json_arguments.strip() == "") else json_parser.json_to_data(json_arguments))

		result = direct_hooks.call(hook, **arguments)
		return json_parser.data_to_json(result)
	#

	def init_host(self, device, service_id = None, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.spec_major = 1
		self.spec_minor = 1
		self.type = "ConnectionManager"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"

		if (service_id == None): service_id = "ConnectionManager"
		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		get_protocol_info = { "argument_variables": [ ],
		                      "return_variable": { "name": "Source", "variable": "SourceProtocolInfo" },
		                      "result_variables": [ { "name": "Sink", "variable": "SinkProtocolInfo" } ]
		                    }

		get_current_connection_ids = { "argument_variables": [ ],
		                               "return_variable": { "name": "ConnectionIDs", "variable": "CurrentConnectionIDs" },
		                               "result_variables": [ ]
		                             }

		get_current_connection_info = { "argument_variables": [ { "name": "ConnectionID", "variable": "A_ARG_TYPE_ConnectionID" } ],
		                                "return_variable": { "name": "RcsID", "variable": "A_ARG_TYPE_RcsID" },
		                                "result_variables": [ { "name": "AVTransportID", "variable": "A_ARG_TYPE_AVTransportID" },
		                                                      { "name": "ProtocolInfo", "variable": "A_ARG_TYPE_ProtocolInfo" },
		                                                      { "name": "PeerConnectionManager", "variable": "A_ARG_TYPE_ConnectionManager" },
		                                                      { "name": "PeerConnectionID", "variable": "A_ARG_TYPE_ConnectionID" },
		                                                      { "name": "Direction", "variable": "A_ARG_TYPE_Direction" },
		                                                      { "name": "Status", "variable": "A_ARG_TYPE_ConnectionStatus" }
		                                                    ]
		                              }

		self.actions = { "GetProtocolInfo": get_protocol_info,
		                 "GetCurrentConnectionIDs": get_current_connection_ids,
		                 "GetCurrentConnectionInfo": get_current_connection_info
		               }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		self.variables = { "SourceProtocolInfo": { "is_sending_events": True,
		                                           "is_multicasting_events": False,
		                                           "type": "string",
		                                           "value": ""
		                                         },
		                   "SinkProtocolInfo": { "is_sending_events": True,
		                                         "is_multicasting_events": False,
		                                         "type": "string",
		                                         "value": ""
		                                       },
		                   "CurrentConnectionIDs": { "is_sending_events": True,
		                                             "is_multicasting_events": False,
		                                             "type": "string",
		                                             "value": ""
		                                           },
		                   "A_ARG_TYPE_ConnectionStatus": { "is_sending_events": False,
		                                                    "is_multicasting_events": False,
		                                                    "type": "string",
		                                                    "values_allowed": [ "OK",
		                                                                        "ContentFormatMismatch",
		                                                                        "InsufficientBandwidth",
		                                                                        "UnreliableChannel",
		                                                                        "Unknown"
		                                                                      ]
		                                                  },
		                   "A_ARG_TYPE_ConnectionManager": { "is_sending_events": False,
		                                                     "is_multicasting_events": False,
		                                                     "type": "string",
		                                                     "value": ""
		                                                   },
		                   "A_ARG_TYPE_Direction": { "is_sending_events": False,
		                                             "is_multicasting_events": False,
		                                             "type": "string",
		                                             "values_allowed": [ "Output", "Input" ]
		                                           },
		                   "A_ARG_TYPE_ProtocolInfo": { "is_sending_events": False,
		                                                "is_multicasting_events": False,
		                                                "type": "string"
		                                              },
		                   "A_ARG_TYPE_ConnectionID": { "is_sending_events": False,
		                                                "is_multicasting_events": False,
		                                                "type": "i4"
		                                              },
		                   "A_ARG_TYPE_AVTransportID": { "is_sending_events": False,
		                                                 "is_multicasting_events": False,
		                                                 "type": "i4"
		                                               },
		                   "A_ARG_TYPE_RcsID": { "is_sending_events": False,
		                                         "is_multicasting_events": False,
		                                         "type": "i4"
		                                       }
		                 }
	#
#

##j## EOF