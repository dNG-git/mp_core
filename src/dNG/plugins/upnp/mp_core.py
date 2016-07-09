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

from dNG.data.settings import Settings
from dNG.data.tasks.memory import Memory as MemoryTasks
from dNG.data.upnp.resources.file import File
from dNG.data.upnp.resources.item_dlna_http_resource import ItemDlnaHttpResource
from dNG.data.upnp.resources.mp_entry import MpEntry
from dNG.data.upnp.search.common_mp_entry_segment import CommonMpEntrySegment
from dNG.database.connection import Connection
from dNG.module.named_loader import NamedLoader
from dNG.net.upnp.control_point import ControlPoint
from dNG.plugins.hook import Hook
from dNG.runtime.instance_lock import InstanceLock

from mp.tasks.resource_scanner import ResourceScanner

_instances = [ ]
_lock = InstanceLock()

def get_item_resource_content(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getItemResourceContent"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
	"""

	if ("item" in params):
	#
		resource = None

		if (isinstance(params['item'], File)):
		#
			resource = ItemDlnaHttpResource()

			if (resource.init_cds_id(params['item'].get_resource_id(),
			                         params['item'].get_client_user_agent()
			                        )
			   ):
			#
				resource.set_stream_vfs_url(params['item'].get_vfs_url())

				resource.set_mimeclass(params['item'].get_mimeclass())
				resource.set_mimetype(params['item'].get_mimetype())
				resource.set_size(params['item'].get_size())
			#
			else: resource = None
		#
		elif (isinstance(params['item'], MpEntry)):
		#
			with Connection.get_instance():
			#
				resource = ItemDlnaHttpResource()

				if (resource.init_cds_id(params['item'].get_resource_id(),
				                         params['item'].get_client_user_agent()
				                        )
				   ):
				#
					resource.set_stream_vfs_url(params['item'].get_vfs_url())

					resource.set_mimeclass(params['item'].get_mimeclass())
					resource.set_mimetype(params['item'].get_mimetype())
					resource.set_size(params['item'].get_size())

					if (params['item'].is_supported("res_metadata")): resource.set_metadata(params['item'].get_res_metadata())
				#
				else: resource = None
			#
		#

		if (resource is not None): params['item'].add_content(resource)
	#

	return last_return
#

def get_root_resource_content(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.getRootResourceContent"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
	"""

	if ("container" in params):
	#
		client_user_agent = params['container'].get_client_user_agent()

		with Connection.get_instance():
		#
			for resource in MpEntry.load_root_containers():
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

:since: v0.2.00
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

:since: v0.2.00
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

:since: v0.2.00
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

:since: v0.2.00
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

:since: v0.2.00
	"""

	# global: _instances, _lock

	with _lock:
	#
		if (len(_instances) < 1):
		#
			upnp_control_point = ControlPoint.get_instance()

			device = NamedLoader.get_instance("dNG.data.upnp.devices.mp.ApiEndpointDevice")
			udn = Settings.get("mp_core_api_endpoint_server_udn")
			if (udn is None): udn = str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}/mp/ApiEndpoint".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_core_api_endpoint_server_name")
				if (device_name is not None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.add_device(device)
			#

			device = NamedLoader.get_instance("dNG.data.upnp.devices.MediaServer")
			udn = Settings.get("mp_core_media_server_udn")
			if (udn is None): udn = str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}/mp/MediaServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_core_media_server_name")
				if (device_name is not None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.add_device(device)
			#

			device = NamedLoader.get_instance("dNG.data.upnp.devices.RemoteUiServerDevice")
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

					if (not entry.is_supported("auto_maintenance")):
					#
						MemoryTasks.get_instance().add("mp.tasks.ResourceScanner.{0}".format(entry_id),
						                               ResourceScanner(entry_id),
						                               0
						                              )
					#
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

:since: v0.2.00
	"""

	Hook.register("dNG.pas.upnp.ControlPoint.onShutdown", on_control_point_shutdown)
	Hook.register("dNG.pas.upnp.ControlPoint.onStartup", on_control_point_startup)
	Hook.register("dNG.pas.upnp.Resource.getItemResourceContent", get_item_resource_content)
	Hook.register("dNG.pas.upnp.Resource.getRootResourceContent", get_root_resource_content)
	Hook.register("dNG.pas.upnp.Resource.getSearchSegments", get_search_segments)
	Hook.register("dNG.pas.upnp.Resource.getSearchableDidlFields", get_searchable_didl_fields)
	Hook.register("dNG.pas.upnp.Resource.getSortableDidlFields", get_sortable_didl_fields)

	Hook.register("mp.upnp.MpResource.applyValueDerivedDbCondition", CommonMpEntrySegment.apply_value_derived_db_condition)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.2.00
	"""

	Hook.unregister("dNG.pas.upnp.ControlPoint.onShutdown", on_control_point_shutdown)
	Hook.unregister("dNG.pas.upnp.ControlPoint.onStartup", on_control_point_startup)
	Hook.unregister("dNG.pas.upnp.Resource.getItemResourceContent", get_item_resource_content)
	Hook.unregister("dNG.pas.upnp.Resource.getRootResourceContent", get_root_resource_content)
	Hook.unregister("dNG.pas.upnp.Resource.getSearchSegments", get_search_segments)
	Hook.unregister("dNG.pas.upnp.Resource.getSearchableDidlFields", get_searchable_didl_fields)
	Hook.unregister("dNG.pas.upnp.Resource.getSortableDidlFields", get_sortable_didl_fields)

	Hook.unregister("mp.upnp.MpResource.applyValueDerivedDbCondition", CommonMpEntrySegment.apply_value_derived_db_condition)
#

##j## EOF