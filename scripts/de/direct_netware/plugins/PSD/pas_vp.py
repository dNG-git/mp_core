# -*- coding: utf-8 -*-
##j## BOF

"""
de.direct_netware.plugins.PSD.pas_vp

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    vp
@subpackage core
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;gpl
            GNU General Public License 2
"""
"""n// NOTE
----------------------------------------------------------------------------
v'place media center
A device oriented media center solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?vp

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
http://www.direct-netware.de/redirect.php?licenses;gpl
----------------------------------------------------------------------------
#echo(pasVpCoreVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from de.direct_netware.classes.pas_globals import direct_globals
from de.direct_netware.classes.pas_pluginmanager import direct_pluginmanager

def plugin_deregistration ():
#
	"""
Deregister plugin hooks.

@since v0.1.00
	"""

	pass
#

def plugin_registration ():
#
	"""
Register plugin hooks.

@since v0.1.00
	"""

	if ((direct_globals['basic_functions'].settings_get ("{0}/settings/pas_vp.xml".format (direct_globals['settings']['path_data']),use_cache = False)) and (direct_globals['settings']['pas_vp_mc_services'] != None)):
	#
		direct_pluginmanager ("de.vplace.plugins")
	#
#

##j## EOF