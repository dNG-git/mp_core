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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
"""

from dNG.data.upnp.resources.mp_entry import MpEntry
from dNG.database.transaction_context import TransactionContext
from dNG.tasks.abstract_lrt_hook import AbstractLrtHook

class ResourceMetadataRefresh(AbstractLrtHook):
#
	"""
"ResourceMetadataRefresh" is responsible of refreshing the resource's
metadata.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, _id):
	#
		"""
Constructor __init__(ResourceMetadataRefresh)

:since: v0.2.00
		"""

		AbstractLrtHook.__init__(self)

		self.id = _id
		"""
UPnP resource ID
		"""

		self.context_id = "mp.tasks.ResourceMetadataRefresh"
	#

	def _run_hook(self):
	#
		"""
Hook execution

:since: v0.2.00
		"""

		resource = MpEntry.load_encapsulating_entry(self.id)
		"""
We need to free the synchronized database lock (SQLite) here or otherwise
"refresh_metadata()" will fail for certain UPnP resource types.
		"""

		if (resource is not None):
		#
			resource.refresh_metadata()

			with TransactionContext():
			#
				resource.set_data_attributes(refreshable = False)
				resource.save()
			#

			resource.close()
			if (self.log_handler is not None): self.log_handler.info("mp.ResourceMetadataRefresh refreshed entry '{0}'", self.id, context = "mp_server")
		#
	#
#

##j## EOF