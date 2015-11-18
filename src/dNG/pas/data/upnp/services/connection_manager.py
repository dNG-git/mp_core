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
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def get_feature_list(self):
	#
		"""
Returns the list of supported UPnP ContentDirectory features.

:return: (str) FeatureList XML document
:since:  v0.1.02
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_feature_list()- (#echo(__LINE__)#)", self, context = "mp_server")
		return self._get_feature_list("dNG.pas.upnp.service.ConnectionManager")
	#

	def get_version(self):
	#
		"""
Returns the UPnP service type version.

:return: (str) Service type version
:since:  v0.1.00
		"""

		client_settings = self.get_client_settings()
		is_versioning_supported = client_settings.get("upnp_spec_versioning_supported", True)

		return (AbstractService.get_version(self) if (is_versioning_supported) else 1)
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

		self.type = "ConnectionManager"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "3"

		if (service_id is None): service_id = "ConnectionManager"
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

		get_feature_list = { "argument_variables": [ ],
		                     "return_variable": { "name": "FeatureList", "variable": "FeatureList" },
		                     "result_variables": [ ]
		                   }

		self.actions = { "GetProtocolInfo": get_protocol_info,
		                 "GetCurrentConnectionIDs": get_current_connection_ids,
		                 "GetCurrentConnectionInfo": get_current_connection_info,
		                 "GetFeatureList": get_feature_list
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
		                                           "type": "string"
		                                         },
		                   "SinkProtocolInfo": { "is_sending_events": True,
		                                         "is_multicasting_events": False,
		                                         "type": "string"
		                                       },
		                   "CurrentConnectionIDs": { "is_sending_events": True,
		                                             "is_multicasting_events": False,
		                                             "type": "string"
		                                           },
		                   "FeatureList": { "is_sending_events": False,
		                                    "is_multicasting_events": False,
		                                    "type": "string"
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
		                                                     "type": "string"
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