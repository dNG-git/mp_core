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

from sqlalchemy.event import listen
from sqlalchemy.schema import Column, DDL, ForeignKey
from sqlalchemy.types import FLOAT, INT, TEXT, VARCHAR

from .mp_upnp_resource import MpUpnpResource

class MpUpnpVideoResource(MpUpnpResource):
    """
"MpResource" represents an database video resource.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    __tablename__ = "{0}_mp_upnp_video_resource".format(MpUpnpResource.get_table_prefix())
    """
SQLAlchemy table name
    """
    db_instance_class = "dNG.data.upnp.resources.MpEntryVideo"
    """
Encapsulating SQLAlchemy database instance class name
    """
    db_schema_version = 1
    """
Database schema version
    """

    id = Column(VARCHAR(32), ForeignKey(MpUpnpResource.id), primary_key = True)
    """
mp_upnp_video_resource.id
    """
    duration = Column(FLOAT, index = True)
    """
mp_upnp_video_resource.duration
    """
    description = Column(TEXT, index = True)
    """
mp_upnp_video_resource.description
    """
    genre = Column(VARCHAR(255), index = True)
    """
mp_upnp_video_resource.genre
    """
    series = Column(VARCHAR(255), index = True)
    """
mp_upnp_video_resource.series
    """
    episode = Column(VARCHAR(255), index = True)
    """
mp_upnp_video_resource.episode
    """
    actor = Column(TEXT, index = True)
    """
mp_upnp_video_resource.actor
    """
    author = Column(TEXT, index = True)
    """
mp_upnp_video_resource.author
    """
    director = Column(TEXT, index = True)
    """
mp_upnp_video_resource.director
    """
    producer = Column(TEXT, index = True)
    """
mp_upnp_video_resource.producer
    """
    publisher = Column(TEXT, index = True)
    """
mp_upnp_video_resource.publisher
    """
    width = Column(INT, index = True)
    """
mp_upnp_video_resource.width
    """
    height = Column(INT, index = True)
    """
mp_upnp_video_resource.height
    """
    codec = Column(VARCHAR(255), index = True)
    """
mp_upnp_video_resource.codec
    """
    bitrate = Column(INT)
    """
mp_upnp_video_resource.bitrate
    """
    bpp = Column(INT)
    """
mp_upnp_video_resource.bpp
    """
    encoder = Column(VARCHAR(255), index = True)
    """
mp_upnp_video_resource.encoder
    """

    __mapper_args__ = { "polymorphic_identity": "MpUpnpVideoResource" }
    """
sqlalchemy.org: Other options are passed to mapper() using the
__mapper_args__ class variable.
    """

    @classmethod
    def before_apply_schema(cls):
        """
Called before applying the SQLAlchemy generated schema to register the
custom DDL for PostgreSQL.

:since: v0.2.00
    """

        create_postgresql_tsvector_index = "CREATE INDEX idx_{0}_mp_upnp_video_resource_description ON {0}_mp_upnp_video_resource USING gin(to_tsvector('simple', description));"
        create_postgresql_tsvector_index = create_postgresql_tsvector_index.format(cls.get_table_prefix())

        listen(cls.__table__,
               "after_create",
               DDL(create_postgresql_tsvector_index).execute_if(dialect = "postgresql")
              )
    #
#
