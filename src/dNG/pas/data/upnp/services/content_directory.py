# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.ContentDirectory
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

from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.resource import Resource
from .abstract_service import AbstractService

class ContentDirectory(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:ContentDirectory:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=redefined-builtin,unused-argument

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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.browse({1}, {2}, {3}, {4:d}, {5:d}, {6})- (#echo(__LINE__)#)".format(self, object_id, browse_flag, filter, starting_index, requested_count, sort_criteria))
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
				resource.content_set_offset(starting_index)
				resource.content_set_limit(requested_count)
			#

			_return = resource.content_get_didl_xml()
		#

		return _return
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

			_return = resource.metadata_get_didl_xml()
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_search_capabilities()- (#echo(__LINE__)#)".format(self))
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_sort_capabilities()- (#echo(__LINE__)#)".format(self))
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
			"GetFeatureList": {
				"argument_variables": [ ],
				"return_variable": { "name": "FeatureList", "variable": "FeatureList" },
				"result_variables": [ ]
			},
			"GetSearchCapabilities": {
				"argument_variables": [ ],
				"return_variable": { "name": "SearchCaps", "variable": "SearchCapabilities" },
				"result_variables": [ ]
			},
			"GetServiceResetToken": {
				"argument_variables": [ ],
				"return_variable": { "name": "ResetToken", "variable": "ServiceResetToken" },
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
			},
			"X_BrowseByLetter": {
				"argument_variables": [
					{ "name": "ObjectID", "variable": "A_ARG_TYPE_ObjectID" },
					{ "name": "BrowseFlag", "variable": "A_ARG_TYPE_BrowseFlag" },
					{ "name": "Filter", "variable": "A_ARG_TYPE_Filter" },
					{ "name": "StartingLetter", "variable": "A_ARG_TYPE_BrowseLetter" },
					{ "name": "RequestedCount", "variable": "A_ARG_TYPE_Count" },
					{ "name": "SortCriteria", "variable": "A_ARG_TYPE_SortCriteria" }
				],
				"return_variable": { "name": "Result", "variable": "A_ARG_TYPE_Result" },
				"result_variables": [
					{ "name": "NumberReturned", "variable": "A_ARG_TYPE_Count" },
					{ "name": "TotalMatches", "variable": "A_ARG_TYPE_Count" },
					{ "name": "UpdateID", "variable": "A_ARG_TYPE_UpdateID" },
					{ "name": "StartingIndex", "variable": "A_ARG_TYPE_Index" }
				]
			},
			"Search": {
				"argument_variables": [
					{ "name": "ContainerID", "variable": "A_ARG_TYPE_ObjectID" },
					{ "name": "SearchCriteria", "variable": "A_ARG_TYPE_SearchCriteria" },
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
			},
			"ServiceResetToken": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
			"FeatureList": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
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
			"A_ARG_TYPE_SearchCriteria": {
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
			# Added for X_BrowseByLetter
			"A_ARG_TYPE_BrowseLetter": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			}
		}

		return True
	#

	def search(self, container_id, search_criteria = "", filter = "*", starting_index = 0, requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.search({1}, {2}, {3}, {4:d}, {5:d}, {6})- (#echo(__LINE__)#)".format(self, container_id, search_criteria, filter, starting_index, requested_count, sort_criteria))

		resource = Resource.load_cds_id(container_id, self.client_user_agent, self)

		if (resource == None): _return = UpnpException("pas_http_core_404", 701)
		elif (not resource.is_supported("content_search")): _return = UpnpException("pas_http_core_501", 720)
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
				resource.content_set_offset(starting_index)
				resource.content_set_limit(requested_count)
			#

			_return = resource.content_search_didl_xml(search_criteria)
		#

		return _return
	#

	def x_browse_by_letter(self, object_id, browse_flag, filter = "*", starting_letter = "", requested_count = 0, sort_criteria = ""):
	#
		"""
Returns the current UPnP SystemUpdateID value.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		return self.search(object_id, "dc:title startsWith \"{0}\"".format(starting_letter.replace("\"", "\\\"")), filter, requested_count = requested_count, sort_criteria = sort_criteria)
	#
#

##j## EOF