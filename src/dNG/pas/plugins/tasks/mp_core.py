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

# pylint: disable=unused-argument

from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.plugins.hook import Hook
from dNG.pas.tasks.mp.resource_scanner import ResourceScanner
from dNG.pas.tasks.mp.root_container_deleter import RootContainerDeleter

def on_root_container_added(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.onRootContainerAdded"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return == None): _return = True
	else: _return = last_return

	if (_return and "container_id" in params):
	#
		MemoryTasks.get_instance().add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(params['container_id']),
		                               ResourceScanner(params['container_id']),
		                               0
		                              )
	#

	return _return
#

def on_root_container_deleted(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.Resource.onRootContainerDeleted"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	if (last_return == None): _return = True
	else: _return = last_return

	if (_return and "container_id" in params): RootContainerDeleter(params['container_id']).run()

	return _return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.upnp.Resource.onRootContainerAdded", on_root_container_added)
	Hook.register("dNG.pas.upnp.Resource.onRootContainerDeleted", on_root_container_deleted)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.upnp.Resource.onRootContainerAdded", on_root_container_added)
	Hook.unregister("dNG.pas.upnp.Resource.onRootContainerDeleted", on_root_container_deleted)
#

##j## EOF