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

# pylint: disable=unused-argument

from socket import getfqdn
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid_of_namespace

from dNG.pas.data.settings import Settings
from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.data.upnp.search.common_mp_entry_segment import CommonMpEntrySegment
from dNG.pas.database.connection import Connection
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.upnp.control_point import ControlPoint
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.instance_lock import InstanceLock
from dNG.pas.tasks.mp.resource_scanner import ResourceScanner

_instances = [ ]
_lock = InstanceLock()

def get_root_resource_content(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getRootResourceContent"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if ("container" in params):
	#
		client_user_agent = params['container'].get_client_user_agent()

		with Connection.get_instance():
		#
			for resource in MpEntry.load_root_containers(client_user_agent):
			#
				resource.set_client_user_agent(client_user_agent)
				resource.set_didl_fields(params['container'].get_didl_fields())

				params['container'].add_content(resource)
			#
		#
	#

	return last_return
#

def get_search_segments(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getSearchSegments"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return is None): _return = [ ]
	else: _return = last_return

	criteria_definition = params.get("criteria_definition")

	if (criteria_definition is None
	    or CommonMpEntrySegment.is_search_criteria_definition_supported(criteria_definition)
	   ): _return.append(CommonMpEntrySegment())
	else: pass

	return _return
#

def get_searchable_didl_fields(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getSearchableDidlFields"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return is None): _return = [ ]
	else: _return = last_return

	_return.append("@id")
	_return.append("@refID")
	_return.append("dc:date")
	_return.append("dc:description")
	_return.append("dc:title")
	_return.append("res@size")
	_return.append("upnp:artist")
	_return.append("upnp:class")
	_return.append("upnp:genre")
	_return.append("upnp:recordedStartDateTime")

	return _return
#

def get_sortable_didl_fields(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getSortableDidlFields"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return is None): _return = [ ]
	else: _return = last_return

	_return.append("@id")
	_return.append("dc:date")
	_return.append("dc:title")
	_return.append("res@size")
	_return.append("upnp:recordedStartDateTime")

	return _return
#

def on_control_point_shutdown(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.onShutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	# global: _lock
	global _instances

	with _lock: _instances = [ ]

	return last_return
#

def on_control_point_startup(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	# global: _instances, _lock

	with _lock:
	#
		if (len(_instances) < 1):
		#
			upnp_control_point = ControlPoint.get_instance()

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.mp.ApiEndpointDevice")
			udn = Settings.get("mp_core_api_endpoint_server_udn")
			if (udn is None): udn = str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}/mp/ApiEndpoint".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_core_api_endpoint_server_name")
				if (device_name is not None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.add_device(device)
			#

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.MediaServer")
			udn = Settings.get("mp_core_media_server_udn")
			if (udn is None): udn = str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}/mp/MediaServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_core_media_server_name")
				if (device_name is not None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.add_device(device)
			#

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.RemoteUiServerDevice")
			udn = Settings.get("mp_core_remote_ui_server_udn")
			if (udn is None): udn = str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}/mp/RemoteUIServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_core_remote_ui_server_name")
				if (device_name is not None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.add_device(device)
			#

			with Connection.get_instance():
			#
				for entry in MpEntry.load_root_containers():
				#
					entry_id = entry.get_resource_id()

					MemoryTasks.get_instance().add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(entry_id),
					                               ResourceScanner(entry_id),
					                               0
					                              )
				#
			#
		#
	#

	return last_return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.upnp.ControlPoint.onShutdown", on_control_point_shutdown)
	Hook.register("dNG.pas.upnp.ControlPoint.onStartup", on_control_point_startup)
	Hook.register("dNG.pas.upnp.Resource.getRootResourceContent", get_root_resource_content)
	Hook.register("dNG.pas.upnp.Resource.getSearchSegments", get_search_segments)
	Hook.register("dNG.pas.upnp.Resource.getSearchableDidlFields", get_searchable_didl_fields)
	Hook.register("dNG.pas.upnp.Resource.getSortableDidlFields", get_sortable_didl_fields)

	Hook.register("dNG.mp.upnp.MpResource.applyValueDerivedDbCondition", CommonMpEntrySegment.apply_value_derived_db_condition)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.upnp.ControlPoint.onShutdown", on_control_point_shutdown)
	Hook.unregister("dNG.pas.upnp.ControlPoint.onStartup", on_control_point_startup)
	Hook.unregister("dNG.pas.upnp.Resource.getRootResourceContent", get_root_resource_content)
	Hook.unregister("dNG.pas.upnp.Resource.getSearchSegments", get_search_segments)
	Hook.unregister("dNG.pas.upnp.Resource.getSearchableDidlFields", get_searchable_didl_fields)
	Hook.unregister("dNG.pas.upnp.Resource.getSortableDidlFields", get_sortable_didl_fields)

	Hook.unregister("dNG.mp.upnp.MpResource.applyValueDerivedDbCondition", CommonMpEntrySegment.apply_value_derived_db_condition)
#

##j## EOF