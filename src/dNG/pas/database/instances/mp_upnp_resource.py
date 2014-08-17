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

from sqlalchemy.orm import foreign, relationship, remote
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BIGINT, BOOLEAN, INT, TEXT, VARCHAR

from .data_linker import DataLinker
from .key_store import KeyStore

class MpUpnpResource(DataLinker):
#
	"""
"MpUPnPResource" represents an database UPnP resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	CDS_TYPE_CONTAINER = 2
	"""
Database container entry
	"""
	CDS_TYPE_ITEM = 3
	"""
Database item entry
	"""
	CDS_TYPE_ROOT = 1
	"""
Database root container entry
	"""

	__tablename__ = "{0}_mp_upnp_resource".format(DataLinker.get_table_prefix())
	"""
SQLAlchemy table name
	"""
	db_instance_class = "dNG.pas.data.upnp.resources.MpEntry"
	"""
Encapsulating SQLAlchemy database instance class name
	"""
	db_schema_version = 1
	"""
Database schema version
	"""

	id = Column(VARCHAR(32), ForeignKey(DataLinker.id), primary_key = True)
	"""
mp_upnp_resource.id
	"""
	cds_type = Column(INT, server_default = "1", nullable = False)
	"""
mp_upnp_resource.cds_type
	"""
	mimeclass = Column(VARCHAR(100), index = True, server_default = "unknown", nullable = False)
	"""
mp_upnp_resource.mimeclass
	"""
	mimetype = Column(VARCHAR(255), index = True, server_default = "application/octet-stream", nullable = False)
	"""
mp_upnp_resource.mimetype
	"""
	resource_type = Column(VARCHAR(100), server_default = "", index = True, nullable = False)
	"""
mp_upnp_resource.resource_type
	"""
	resource_title = Column(VARCHAR(255), server_default = "", index = True, nullable = False)
	"""
mp_upnp_resource.resource_title
	"""
	resource = Column(TEXT, server_default = "", nullable = False, unique = True)
	"""
mp_upnp_resource.resource
	"""
	refreshable = Column(BOOLEAN, server_default = "0", nullable = False)
	"""
mp_upnp_resource.refreshable
	"""
	size = Column(BIGINT)
	"""
mp_upnp_resource.size
	"""

	__mapper_args__ = { "polymorphic_identity": "MpUpnpResource" }
	"""
sqlalchemy.org: Other options are passed to mapper() using the
                __mapper_args__ class variable.
	"""

	rel_mp_upnp_resource_children = relationship("MpUpnpResource", lazy = "dynamic", primaryjoin = (foreign(DataLinker.id) == remote(DataLinker.id_parent)), uselist = True, viewonly = True)
	"""
Relation to MpUpnpResource children
	"""
	rel_resource_metadata = relationship(KeyStore, lazy = "joined", primaryjoin = (foreign(DataLinker.id) == remote(KeyStore.key)), uselist = False)
	"""
Relation to MpUpnpResource metadata
	"""

	def __init__(self, *args, **kwargs):
	#
		"""
Constructor __init__(MpUpnpResource)

:since: v0.1.00
		"""

		DataLinker.__init__(self, *args, **kwargs)

		if (self.cds_type == None): self.cds_type = MpUpnpResource.CDS_TYPE_ITEM
	#
#

##j## EOF