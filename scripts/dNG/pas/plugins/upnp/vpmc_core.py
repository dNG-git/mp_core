# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.upnp.vpmc_server
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

from socket import getfqdn
from threading import RLock
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid

from dNG.pas.data.settings import Settings
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.vpmc_entry import VpmcEntry
from dNG.pas.database.connection import Connection
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks
from dNG.pas.tasks.upnp.vpmc_entry_scanner import VpmcEntryScanner

_instances = [ ]
_synchronized = RLock()

def plugin_control_point_shutdown(params, last_return):
#
	"""
Called for "dNG.pas.upnp.control_point.shutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	global _instances, _synchronized
	_return = False

	with _synchronized:
	#
		if (len(_instances) > 0):
		#
			upnp_control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")

			for device in _instances: upnp_control_point.device_remove(device)
			_instances = [ ]

			_return = True
		#
	#

	return _return
#

def plugin_control_point_startup(params, last_return):
#
	"""
Called for "dNG.pas.upnp.control_point.startup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	global _instances, _synchronized
	_return = False

	with _synchronized:
	#
		if (len(_instances) < 1):
		#
			upnp_control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.MediaServer")
			udn = Settings.get("vpmc_media_server_udn")
			if (udn == None): udn = str(uuid(NAMESPACE_URL, "upnp://{0}/vpmc/MediaServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("vpmc_media_server_name")
				if (device_name != None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.device_add(device)
			#

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.RemoteUiServerDevice")
			udn = Settings.get("vpmc_remote_ui_server_udn")
			if (udn == None): udn = str(uuid(NAMESPACE_URL, "upnp://{0}/vpmc/RemoteUIServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("vpmc_remote_ui_server_udn")
				if (device_name != None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.device_add(device)
			#

			with Connection.get_instance():
			#
				for entry in VpmcEntry.load_root_containers(): VpmcEntryScanner(entry)
			#
		#

		_return = True
	#

	return _return
#

def plugin_resource_get_db_didl_fields(params, last_return):
#
	"""
Called for
"dNG.pas.upnp.service.content_directory.get_searchable_didl_fields" and
"dNG.pas.upnp.service.content_directory.get_sortable_didl_fields"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return == None): _return = [ ]
	else: _return = last_return

	_return.append("dc:date")
	_return.append("dc:title")
	_return.append("upnp:recordedStartDateTime")

	return last_return
#

def plugin_resource_get_root_containers(params, last_return):
#
	"""
Called for "dNG.pas.upnp.resource.get_root_containers"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if ("container" in params):
	#
		client_user_agent = params['container'].client_get_user_agent()

		with Connection.get_instance():
		#
			for entry in VpmcEntry.load_root_containers(client_user_agent):
			#
				resource_data = entry.data_get("resource")
				resource = (None if (resource_data == None) else Resource.load_cds_id(resource_data['resource'], client_user_agent))

				if (resource != None):
				#
					resource.set_didl_fields(params['container'].get_didl_fields)
					params['container'].content_add(resource)
				#
			#
		#
	#

	return last_return
#

def plugin_deregistration():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hooks.unregister("dNG.pas.upnp.control_point.shutdown", plugin_control_point_shutdown)
	Hooks.unregister("dNG.pas.upnp.control_point.startup", plugin_control_point_startup)
	Hooks.unregister("dNG.pas.upnp.resource.get_root_containers", plugin_resource_get_root_containers)
	Hooks.unregister("dNG.pas.upnp.service.content_directory.get_searchable_didl_fields", plugin_resource_get_db_didl_fields)
	Hooks.unregister("dNG.pas.upnp.service.content_directory.get_sortable_didl_fields", plugin_resource_get_db_didl_fields)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.upnp.control_point.shutdown", plugin_control_point_shutdown)
	Hooks.register("dNG.pas.upnp.control_point.startup", plugin_control_point_startup)
	Hooks.register("dNG.pas.upnp.resource.get_root_containers", plugin_resource_get_root_containers)
	Hooks.register("dNG.pas.upnp.service.content_directory.get_searchable_didl_fields", plugin_resource_get_db_didl_fields)
	Hooks.register("dNG.pas.upnp.service.content_directory.get_sortable_didl_fields", plugin_resource_get_db_didl_fields)
#

##j## EOF