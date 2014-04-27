# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.tasks.mp.ResourceRefreshMetadata
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

from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.database.connection import Connection
from dNG.pas.tasks.abstract_lrt_hook import AbstractLrtHook

class ResourceRefreshMetadata(AbstractLrtHook):
#
	"""
"ResourceRefreshMetadata" is responsible of refreshing the resource's
metadata.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, _id):
	#
		"""
Constructor __init__(ResourceRefreshMetadata)

:since: v0.1.00
		"""

		AbstractLrtHook.__init__(self)

		self.encapsulating_id = _id
		"""
UPnP resource
		"""

		self.context_id = "dNG.pas.tasks.mp.ResourceRefreshMetadata"
	#

	def _run_hook(self):
	#
		"""
Hook execution

:since: v0.1.00
		"""

		with Connection.get_instance():
		#
			encapsulating_resource = MpEntry.load_encapsulating_entry(self.encapsulating_id)

			if (encapsulating_resource != None):
			#
				encapsulating_resource.refresh_metadata()
				encapsulating_resource.save()

				if (self.log_handler != None): self.log_handler.info("mp.ResourceRefreshMetadata refreshed entry '{0}'".format(self.encapsulating_id))
			#
		#
	#
#

##j## EOF