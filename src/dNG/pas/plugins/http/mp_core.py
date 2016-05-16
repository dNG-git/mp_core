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

from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.text.l10n import L10n
from dNG.pas.plugins.hook import Hook

def init_control_l10n(params, last_return = None):
#
	"""
Called for "dNG.pas.http.l10n.upnp.Control.init"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	L10n.init("mp_core")
	return last_return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.http.l10n.upnp.Control.init", init_control_l10n)
	Hook.register("dNG.pas.http.Server.onStartup", on_startup)
	Hook.register("dNG.pas.http.Wsgi.onStartup", on_startup)
#

def on_startup(params, last_return = None):
#
	"""
Called for "dNG.pas.http.Server.onStartup" and "dNG.pas.http.Wsgi.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.02
	"""

	VirtualConfig.set_virtual_path("/apis/mp/endpoint_configuration/", { "ohandler": "http_json", "m": "mp", "s": "app_endpoint", "a": "api_get_configuration", "path": "version" })

	return last_return
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.http.l10n.upnp.Control.init", init_control_l10n)
	Hook.unregister("dNG.pas.http.Server.onStartup", on_startup)
	Hook.unregister("dNG.pas.http.Wsgi.onStartup", on_startup)
#

##j## EOF