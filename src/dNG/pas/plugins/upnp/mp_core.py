# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.upnp.mp_core
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

# pylint: disable=unused-argument

from socket import getfqdn
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid

from dNG.pas.data.settings import Settings
from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.database.connection import Connection
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks
from dNG.pas.runtime.instance_lock import InstanceLock
from dNG.pas.tasks.mp.resource_scanner import ResourceScanner

_instances = [ ]
_lock = InstanceLock()

def plugin_control_point_shutdown(params, last_return):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.shutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	# global: _lock
	global _instances

	_return = False

	with _lock:
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
Called for "dNG.pas.upnp.ControlPoint.startup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	# global: _lock
	global _instances

	_return = False

	with _lock:
	#
		if (len(_instances) < 1):
		#
			upnp_control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.MediaServer")
			udn = Settings.get("mp_media_server_udn")
			if (udn == None): udn = str(uuid(NAMESPACE_URL, "upnp://{0}/mp/MediaServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_media_server_name")
				if (device_name != None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.device_add(device)
			#

			device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.RemoteUiServerDevice")
			udn = Settings.get("mp_remote_ui_server_udn")
			if (udn == None): udn = str(uuid(NAMESPACE_URL, "upnp://{0}/mp/RemoteUIServer".format(getfqdn())))

			if (device.init_device(upnp_control_point, udn)):
			#
				device_name = Settings.get("mp_remote_ui_server_udn")
				if (device_name != None): device.set_name(device_name)

				_instances.append(device)
				upnp_control_point.device_add(device)
			#

			with Connection.get_instance():
			#
				for entry in MpEntry.load_root_containers(): MemoryTasks.get_instance().task_add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(entry.get_id()), ResourceScanner(entry), 0)
			#
		#

		_return = True
	#

	return _return
#

def plugin_resource_get_searchable_didl_fields(params, last_return):
#
	"""
Called for "dNG.pas.upnp.Resource.getSearchableDidlFields"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return == None): _return = [ ]
	else: _return = last_return

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

def plugin_resource_get_sortable_didl_fields(params, last_return):
#
	"""
Called for "dNG.pas.upnp.Resource.getSortableDidlFields"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return == None): _return = [ ]
	else: _return = last_return

	_return.append("dc:date")
	_return.append("dc:title")
	_return.append("res@size")
	_return.append("upnp:recordedStartDateTime")

	return _return
#

def plugin_resource_get_root_content(params, last_return):
#
	"""
Called for "dNG.pas.upnp.Resource.getRootResourceContent"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if ("container" in params):
	#
		client_user_agent = params['container'].client_get_user_agent()

		with Connection.get_instance():
		#
			for resource in MpEntry.load_root_containers(client_user_agent):
			#
				resource.client_set_user_agent(client_user_agent)
				resource.set_didl_fields(params['container'].get_didl_fields())

				params['container'].content_add(resource)
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

	Hooks.unregister("dNG.pas.upnp.ControlPoint.shutdown", plugin_control_point_shutdown)
	Hooks.unregister("dNG.pas.upnp.ControlPoint.startup", plugin_control_point_startup)
	Hooks.unregister("dNG.pas.upnp.Resource.getRootResourceContent", plugin_resource_get_root_content)
	Hooks.unregister("dNG.pas.upnp.Resource.getSearchableDidlFields", plugin_resource_get_searchable_didl_fields)
	Hooks.unregister("dNG.pas.upnp.Resource.getSortableDidlFields", plugin_resource_get_sortable_didl_fields)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.upnp.ControlPoint.shutdown", plugin_control_point_shutdown)
	Hooks.register("dNG.pas.upnp.ControlPoint.startup", plugin_control_point_startup)
	Hooks.register("dNG.pas.upnp.Resource.getRootResourceContent", plugin_resource_get_root_content)
	Hooks.register("dNG.pas.upnp.Resource.getSearchableDidlFields", plugin_resource_get_searchable_didl_fields)
	Hooks.register("dNG.pas.upnp.Resource.getSortableDidlFields", plugin_resource_get_sortable_didl_fields)
#

##j## EOF