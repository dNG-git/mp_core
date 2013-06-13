# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.database.instances.VpmcUpnpResource
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

from sqlalchemy import Column, ForeignKey, TEXT, VARCHAR

from .data_linker import DataLinker

class VpmcUpnpResource(DataLinker):
#
	"""
"VpmcResource" represents an database resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	DB_TYPE_CONTAINER = 2
	"""
Database container entry
	"""
	DB_TYPE_ITEM = 3
	"""
Database item entry
	"""
	DB_TYPE_ROOT = 1
	"""
Database root container entry
	"""

	__tablename__ = "{0}_vpmc_upnp_resource".format(DataLinker.get_table_prefix())
	"""
SQLAlchemy table name
	"""

	id = Column(VARCHAR(32), ForeignKey(DataLinker.id), primary_key = True)
	"""
vpmc_entry_resource.id
	"""
	mime_type = Column(VARCHAR(255), index = True, server_default = "application/x-unknown", nullable = False)
	"""
vpmc_entry_resource.mime_type
	"""
	resource = Column(TEXT(), server_default = "", nullable = False, unique = True)
	"""
vpmc_entry_resource.resource
	"""

	__mapper_args__ = { "polymorphic_identity": "VpmcUpnpResource" }

	def __init__(self, *args, **kwargs):
	#
		"""
Constructor __init__(VpmcUpnpResource)

:since: v0.1.00
		"""

		DataLinker.__init__(self, *args, **kwargs)

		if (self.type == None): self.type = VpmcUpnpResource.DB_TYPE_ITEM
	#
#

##j## EOF