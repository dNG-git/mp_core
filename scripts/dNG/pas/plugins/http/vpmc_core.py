# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.http.vpmc_core
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

from dNG.pas.data.text.l10n import L10n
from dNG.pas.controller.abstract_request import AbstractRequest
from dNG.pas.plugins.hooks import Hooks

def plugin_control_init_l10n(params, last_return):
#
	"""
Called for "dNG.pas.http.l10n.upnp.control.init"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	L10n.init("vpmc_core")
	return last_return
#

def plugin_theme_check_candidates(params, last_return):
#
	"""
Called for "dNG.pas.http.theme.check_candidates"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	_return = last_return

	if (_return == None and "theme" in params):
	#
		request = AbstractRequest.get_instance()
		user_agent = (request.get_header("User-Agent") if (request.supports_headers()) else None)

		if (user_agent != None):
		#
			if ("(Kobo Touch)" in user_agent): _return = "vpmc_small_ereader"
		#
	#

	return _return
#

def plugin_deregistration():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hooks.unregister("dNG.pas.http.l10n.upnp.control.init", plugin_control_init_l10n)
	Hooks.unregister("dNG.pas.http.theme.check_candidates", plugin_theme_check_candidates)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.http.l10n.upnp.control.init", plugin_control_init_l10n)
	Hooks.register("dNG.pas.http.theme.check_candidates", plugin_theme_check_candidates)
#

##j## EOF