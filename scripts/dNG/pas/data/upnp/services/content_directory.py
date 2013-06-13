# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.ContentDirectory
"""
"""n// NOTE
----------------------------------------------------------------------------
Video's place (media center edition)
A device centric multimedia solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?vpmc;core

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
#echo(vpmcCoreVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.plugins.hooks import Hooks
from .abstract_service import AbstractService

class ContentDirectory(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:ContentDirectory:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	update_id = 1
	"""
UPnP SystemUpdateID
	"""

	def browse(self, object_id, browse_flag, filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Service.browse({0}, {1}, {2}, {3:d}, {4:d}, {5})- (#echo(__LINE__)#)".format(object_id, browse_flag, filter, starting_index, requested_count, sort_criteria))
		_return = UpnpException("pas_http_error_404", 701)

		if (browse_flag == "BrowseDirectChildren"):
		#
			result = self.browse_tree(object_id, filter, starting_index, requested_count, sort_criteria)
			if (result != None): _return= result
		#
		elif (browse_flag == "BrowseMetadata"):
		#
			result = self.get_metadata(object_id, filter)
			if (result != None): _return= result
		#

		return _return
	#

	def browse_tree(self, object_id, _filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		resource = Resource.load_cds_id(object_id, self.client_user_agent, self)

		if (resource != None):
		#
			if (_filter != "" and _filter != "*"):
			#
				filter_list = [ ]
				for filter_value in _filter.split(","): filter_list.append(filter_value.strip())
				resource.set_didl_fields(filter_list)
			#

			if (requested_count > 0):
			#
				resource.content_set_offset(starting_index)
				resource.content_set_limit(requested_count)
			#

			return resource.content_get_didl_xml()
		#
		else: return None
	#

	def get_metadata(self, object_id, _filter = "*"):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		resource = Resource.load_cds_id(object_id, self.client_user_agent, self)

		if (resource != None):
		#
			if (_filter != "" and _filter != "*"):
			#
				filter_list = [ ]
				for filter_value in _filter.split(","): filter_list.append(filter_value.strip())
				resource.set_didl_fields(filter_list)
			#

			return resource.metadata_get_didl_xml()
		#
		else: return None
	#

	def get_search_capabilities(self):
	#
		"""
Returns the UPnP search capabilities.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		didl_fields = Hooks.call("dNG.pas.upnp.service.content_directory.get_searchable_didl_fields", client_user_agent = self.client_user_agent)
		if ((type(didl_fields) != list) or len(didl_fields) < 1): didl_fields = None

		if (didl_fields == None): _return = ""
		else: _return = ",".join(self._get_unique_list(didl_fields))

		return _return
	#

	def get_sort_capabilities(self):
	#
		"""
Returns the UPnP sort capabilities.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		didl_fields = Hooks.call("dNG.pas.upnp.service.content_directory.get_sortable_didl_fields", client_user_agent = self.client_user_agent)
		if ((type(didl_fields) != list) or len(didl_fields) < 1): didl_fields = None

		if (didl_fields == None): _return = ""
		else: _return = ",".join(self._get_unique_list(didl_fields))

		return _return
	#

	def get_system_update_id(self):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		return ContentDirectory.update_id
	#

	def init_service(self, device, service_id = None, configid = None):
	#
		"""
Initialize a host service.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		if (service_id == None): service_id = "ContentDirectory"
		AbstractService.init_service(self, device, service_id, configid)

		self.actions = {
			"GetSearchCapabilities": {
				"argument_variables": [ ],
				"return_variable": { "name": "SearchCaps", "variable": "SearchCapabilities" },
				"result_variables": [ ]
			},
			"GetSortCapabilities": {
				"argument_variables": [ ],
				"return_variable": { "name": "SortCaps", "variable": "SortCapabilities" },
				"result_variables": [ ]
			},
			"GetSystemUpdateID": {
				"argument_variables": [ ],
				"return_variable": { "name": "Id", "variable": "SystemUpdateID" },
				"result_variables": [ ]
			},
			"Browse": {
				"argument_variables": [
					{ "name": "ObjectID", "variable": "A_ARG_TYPE_ObjectID" },
					{ "name": "BrowseFlag", "variable": "A_ARG_TYPE_BrowseFlag" },
					{ "name": "Filter", "variable": "A_ARG_TYPE_Filter" },
					{ "name": "StartingIndex", "variable": "A_ARG_TYPE_Index" },
					{ "name": "RequestedCount", "variable": "A_ARG_TYPE_Count" },
					{ "name": "SortCriteria", "variable": "A_ARG_TYPE_SortCriteria" }
				],
				"return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
				"result_variables": [
					{ "name": "NumberReturned", "variable": "A_ARG_TYPE_Count" },
					{ "name": "TotalMatches", "variable": "A_ARG_TYPE_Count" },
					{ "name": "UpdateID", "variable": "A_ARG_TYPE_UpdateID" }
				]
			}
		}

		self.service_id = service_id
		self.spec_major = 1
		self.spec_minor = 1
		self.type = "ContentDirectory"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"

		self.variables = {
			"A_ARG_TYPE_ObjectID": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_Result": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_BrowseFlag": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"values_allowed": [ "BrowseMetadata", "BrowseDirectChildren" ]
			},
			"A_ARG_TYPE_Filter": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_SortCriteria": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_Index": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"A_ARG_TYPE_Count": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"A_ARG_TYPE_UpdateID": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "ui4"
			},
			"SearchCapabilities": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
			"SortCapabilities": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
			"SystemUpdateID": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "ui4",
				"value": self.update_id
			}
		}

		return True
	#
#

##j## EOF