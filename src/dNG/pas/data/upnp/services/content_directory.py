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

from dNG.pas.data.upnp.gena_event import GenaEvent
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.update_id_registry import UpdateIdRegistry
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.plugins.hook import Hook
from .abstract_service import AbstractService

_py_filter = filter
"""
Remapped filter builtin
"""

class ContentDirectory(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:ContentDirectory:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=redefined-builtin,unused-argument

	def __init__(self):
	#
		"""
Constructor __init__(ContentDirectory)

:since: v0.1.03
		"""

		AbstractService.__init__(self)

		self.container_update_ids = { }
		"""
Container update IDs
		"""
	#

	def browse(self, object_id, browse_flag, filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.browse({1}, {2}, {3}, {4:d}, {5:d}, {6})- (#echo(__LINE__)#)", self, object_id, browse_flag, filter, starting_index, requested_count, sort_criteria, context = "mp_server")
		_return = UpnpException("pas_http_core_404", 701)

		if (browse_flag == "BrowseDirectChildren"):
		#
			result = self._browse_tree(object_id, filter, starting_index, requested_count = requested_count, sort_criteria = sort_criteria)
			if (result != None): _return = result
		#
		elif (browse_flag == "BrowseMetadata"):
		#
			result = self._get_metadata(object_id, filter)
			if (result != None): _return = result
		#

		return _return
	#

	def _browse_tree(self, object_id, _filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		_return = None

		resource = Resource.load_cds_id(object_id, self.client_user_agent, self)

		if (resource != None):
		#
			if (_filter != "" and _filter != "*"):
			#
				filter_list = [ ]
				for filter_value in _filter.split(","): filter_list.append(filter_value.strip())
				resource.set_didl_fields(filter_list)
			#

			resource.set_sort_criteria(sort_criteria)

			if (requested_count > 0):
			#
				resource.set_content_offset(starting_index)
				resource.set_content_limit(requested_count)
			#

			_return = resource.get_content_didl_xml()
		#

		return _return
	#

	def _get_container_update_ids(self):
	#
		"""
Returns the CSV list of UPnP ContainerUpdateIDs.

:return: (str) CSV list of UPnP ContainerUpdateIDs
:since:  v0.1.03
		"""

		ids = self.container_update_ids.copy()
		return ",".join([ "{0},{1}".format(container_id, ids[container_id]) for container_id in ids ])
	#

	def _get_metadata(self, object_id, _filter = "*"):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		_return = None

		resource = Resource.load_cds_id(object_id, self.client_user_agent, self)

		if (resource != None):
		#
			if (_filter != "" and _filter != "*"):
			#
				filter_list = [ ]
				for filter_value in _filter.split(","): filter_list.append(filter_value.strip())
				resource.set_didl_fields(filter_list)
			#

			_return = resource.get_metadata_didl_xml()
		#

		return _return
	#

	def get_search_capabilities(self):
	#
		"""
Returns the system-wide UPnP search capabilities available.

:return: (int) UPnP search capabilities value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_search_capabilities()- (#echo(__LINE__)#)", self, context = "mp_server")
		_return = UpnpException("pas_http_core_404", 701)

		resource = Resource.load_cds_id("0", self.client_user_agent, self)
		if (resource != None): _return = resource.get_search_capabilities()

		return _return
	#

	def get_sort_capabilities(self):
	#
		"""
Returns the system-wide UPnP sort capabilities available.

:return: (int) UPnP sort capabilities value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_sort_capabilities()- (#echo(__LINE__)#)", self, context = "mp_server")
		_return = UpnpException("pas_http_core_404", 701)

		resource = Resource.load_cds_id("0", self.client_user_agent, self)
		if (resource != None): _return = resource.get_sort_capabilities()

		return _return
	#

	def get_system_update_id(self):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		return UpdateIdRegistry.get("upnp://{0}/system_update_id".format(self.get_udn()))
	#

	def _handle_gena_registration(self, sid):
	#
		"""
Handles the registration of an UPnP device at GENA with the given SID.

:param sid: UPnP SID

:since: v0.1.03
		"""

		event = GenaEvent(GenaEvent.TYPE_PROPCHANGE)

		event.set_variables(ContainerUpdateIDs = self._get_container_update_ids(),
		                    SystemUpdateID = self.get_system_update_id()
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
:since:  v0.1.00
		"""

		self.spec_major = 1
		self.spec_minor = 1
		self.type = "ContentDirectory"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"

		if (service_id == None): service_id = "ContentDirectory"

		Hook.register_weakref("dNG.pas.upnp.Resource.onUpdateIdChanged", self._on_updated_id)

		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		browse = { "argument_variables": [ { "name": "ObjectID", "variable": "A_ARG_TYPE_ObjectID" },
		                                   { "name": "BrowseFlag", "variable": "A_ARG_TYPE_BrowseFlag" },
		                                   { "name": "Filter", "variable": "A_ARG_TYPE_Filter" },
		                                   { "name": "StartingIndex", "variable": "A_ARG_TYPE_Index" },
		                                   { "name": "RequestedCount", "variable": "A_ARG_TYPE_Count" },
		                                   { "name": "SortCriteria", "variable": "A_ARG_TYPE_SortCriteria" }
		                                 ],
		           "return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
		           "result_variables": [ { "name": "NumberReturned", "variable": "A_ARG_TYPE_Count" },
		                                 { "name": "TotalMatches", "variable": "A_ARG_TYPE_Count" },
		                                 { "name": "UpdateID", "variable": "A_ARG_TYPE_UpdateID" }
		                               ]
		         }

		get_feature_list = { "argument_variables": [ ],
		                     "return_variable": { "name": "FeatureList", "variable": "FeatureList" },
		                     "result_variables": [ ]
		                   }

		get_search_capabilities = { "argument_variables": [ ],
		                            "return_variable": { "name": "SearchCaps", "variable": "SearchCapabilities" },
		                            "result_variables": [ ]
		                          }

		get_service_reset_token = { "argument_variables": [ ],
		                            "return_variable": { "name": "ResetToken", "variable": "ServiceResetToken" },
		                            "result_variables": [ ]
		                          }

		get_sort_capabilities = { "argument_variables": [ ],
		                          "return_variable": { "name": "SortCaps", "variable": "SortCapabilities" },
		                          "result_variables": [ ]
		                        }

		get_system_update_id = { "argument_variables": [ ],
		                         "return_variable": { "name": "Id", "variable": "SystemUpdateID" },
		                         "result_variables": [ ]
		                       }

		search = { "argument_variables": [ { "name": "ContainerID", "variable": "A_ARG_TYPE_ObjectID" },
		                                   { "name": "SearchCriteria", "variable": "A_ARG_TYPE_SearchCriteria" },
		                                   { "name": "Filter", "variable": "A_ARG_TYPE_Filter" },
		                                   { "name": "StartingIndex", "variable": "A_ARG_TYPE_Index" },
		                                   { "name": "RequestedCount", "variable": "A_ARG_TYPE_Count" },
		                                   { "name": "SortCriteria", "variable": "A_ARG_TYPE_SortCriteria" }
		                                 ],
		           "return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
		           "result_variables": [ { "name": "NumberReturned", "variable": "A_ARG_TYPE_Count" },
		                                 { "name": "TotalMatches", "variable": "A_ARG_TYPE_Count" },
		                                 { "name": "UpdateID", "variable": "A_ARG_TYPE_UpdateID" }
		                               ]
		         }

		self.actions = { "GetFeatureList": get_feature_list,
		                 "GetSearchCapabilities": get_search_capabilities,
		                 "GetServiceResetToken": get_service_reset_token,
		                 "GetSortCapabilities": get_sort_capabilities,
		                 "GetSystemUpdateID": get_system_update_id,
		                 "Browse": browse,
		                 "Search": search
		               }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		self.variables = { "SearchCapabilities": { "is_sending_events": False,
		                                           "is_multicasting_events": False,
		                                           "type": "string",
		                                           "value": ""
		                                         },
		                   "SortCapabilities": { "is_sending_events": False,
		                                         "is_multicasting_events": False,
		                                         "type": "string",
		                                         "value": ""
		                                       },
		                   "SystemUpdateID": { "is_sending_events": True,
		                                       "is_multicasting_events": False,
		                                       "type": "ui4",
		                                       "value": self.get_system_update_id()
		                                     },
		                   "ContainerUpdateIDs": { "is_sending_events": True,
		                                           "is_multicasting_events": False,
		                                           "type": "string",
		                                           "value": self._get_container_update_ids()
		                                         },
		                   "ServiceResetToken": { "is_sending_events": False,
		                                          "is_multicasting_events": False,
		                                          "type": "string",
		                                          "value": ""
		                                        },
		                   "FeatureList": { "is_sending_events": False,
		                                    "is_multicasting_events": False,
		                                    "type": "string",
		                                    "value": ""
		                                  },
		                   "A_ARG_TYPE_ObjectID": { "is_sending_events": False,
		                                            "is_multicasting_events": False,
		                                            "type": "string"
		                                          },
		                   "A_ARG_TYPE_Result": { "is_sending_events": False,
		                                          "is_multicasting_events": False,
		                                          "type": "string"
		                                        },
		                   "A_ARG_TYPE_SearchCriteria": { "is_sending_events": False,
		                                                  "is_multicasting_events": False,
		                                                  "type": "string"
		                                                },
		                   "A_ARG_TYPE_BrowseFlag": { "is_sending_events": False,
		                                              "is_multicasting_events": False,
		                                              "type": "string",
		                                              "values_allowed": [ "BrowseMetadata", "BrowseDirectChildren" ]
		                                            },
		                   "A_ARG_TYPE_Filter": { "is_sending_events": False,
		                                          "is_multicasting_events": False,
		                                          "type": "string"
		                                        },
		                   "A_ARG_TYPE_SortCriteria": { "is_sending_events": False,
		                                                "is_multicasting_events": False,
		                                                "type": "string"
		                                              },
		                   "A_ARG_TYPE_Index": { "is_sending_events": False,
		                                         "is_multicasting_events": False,
		                                         "type": "ui4"
		                                       },
		                   "A_ARG_TYPE_Count": { "is_sending_events": False,
		                                         "is_multicasting_events": False,
		                                         "type": "ui4"
		                                       },
		                   "A_ARG_TYPE_UpdateID": { "is_sending_events": False,
		                                            "is_multicasting_events": False,
		                                            "type": "ui4"
		                                          }
		                 }
	#

	def _on_updated_id(self, params, last_return = None):
	#
		"""
Called after an UPnP UpdateID value has been changed.

:return: (mixed) Return value
:since:  v0.1.03
		"""

		if ("id" in params and "value" in params):
		#
			_id = "upnp://{0}/system_update_id".format(self.get_udn())

			if (params['id'] != _id):
			#
				self.container_update_ids[params['id']] = params['value']
				UpdateIdRegistry.set(_id, "++")
			#

			event = GenaEvent(GenaEvent.TYPE_PROPCHANGE)

			event.set_variables(ContainerUpdateIDs = self._get_container_update_ids(),
			                    SystemUpdateID = self.get_system_update_id()
			                   )

			event.set_usn(self.get_usn())
			event.schedule()
		#

		return last_return
	#

	def search(self, container_id, search_criteria = "", filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.search({1}, {2}, {3}, {4:d}, {5:d}, {6})- (#echo(__LINE__)#)", self, container_id, search_criteria, filter, starting_index, requested_count, sort_criteria, context = "mp_server")

		resource = Resource.load_cds_id(container_id, self.client_user_agent, self)

		if (resource == None): _return = UpnpException("pas_http_core_404", 701)
		elif (not resource.is_supported("search_content")): _return = UpnpException("pas_http_core_501", 720)
		else:
		#
			if (filter != "" and filter != "*"):
			#
				filter_list = [ ]
				for filter_value in filter.split(","): filter_list.append(filter_value.strip())
				resource.set_didl_fields(filter_list)
			#

			resource.set_sort_criteria(sort_criteria)

			if (requested_count > 0):
			#
				resource.set_content_offset(starting_index)
				resource.set_content_limit(requested_count)
			#

			_return = resource.search_content_didl_xml(search_criteria)
		#

		return _return
	#
#

##j## EOF