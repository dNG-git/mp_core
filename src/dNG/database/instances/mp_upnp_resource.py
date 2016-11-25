# -*- coding: utf-8 -*-

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

from sqlalchemy.orm import foreign, relationship, remote
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BOOLEAN, VARCHAR

from .file_center_entry import FileCenterEntry
from .key_store import KeyStore

class MpUpnpResource(FileCenterEntry):
    """
"MpUPnPResource" represents an database UPnP resource.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    __tablename__ = "{0}_mp_upnp_resource".format(FileCenterEntry.get_table_prefix())
    """
SQLAlchemy table name
    """
    db_instance_class = "dNG.data.upnp.resources.MpEntry"
    """
Encapsulating SQLAlchemy database instance class name
    """
    db_schema_version = 3
    """
Database schema version
    """

    id = Column(VARCHAR(32), ForeignKey(FileCenterEntry.id), primary_key = True)
    """
mp_upnp_resource.id
    """
    resource_title = Column(VARCHAR(255), index = True, server_default = "", nullable = False)
    """
mp_upnp_resource.resource_title
    """
    refreshable = Column(BOOLEAN, server_default = "0", nullable = False)
    """
mp_upnp_resource.refreshable
    """

    __mapper_args__ = { "polymorphic_identity": "MpUpnpResource" }
    """
sqlalchemy.org: Other options are passed to mapper() using the
__mapper_args__ class variable.
    """

    rel_mp_upnp_resource_children = relationship("MpUpnpResource", lazy = "dynamic", primaryjoin = (foreign(FileCenterEntry.id) == remote(FileCenterEntry.id_parent)), uselist = True, viewonly = True)
    """
Relation to MpUpnpResource children
    """
    rel_resource_metadata = relationship(KeyStore, lazy = "joined", primaryjoin = (foreign(FileCenterEntry.id) == remote(KeyStore.key)), uselist = False)
    """
Relation to MpUpnpResource metadata
    """
#
