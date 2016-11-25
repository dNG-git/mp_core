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

class DlnaItemResourceMixin(object):
    """
This mixin provides all constants required for DLNA 1.50 compliant item
resources.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    DLNA_0150 = 1 << 20
    """
Flag for DLNA 1.50 compatibility.
    """
    DLNA_BACKGROUND_TRANSFER = 1 << 22
    """
Flag for background transfer mode.
    """
    DLNA_INTERACTIVE_TRANSFER = 1 << 23
    """
Flag for interactive transfer mode.
    """
    DLNA_HTTP_STALLING = 1 << 21
    """
Flag for the method of stalling the HTTP data flow on pause.
    """
    DLNA_IS_CONTAINER = 1 << 28
    """
Flag for container or playlist elements.
    """
    DLNA_LOP_BYTES = 1 << 29
    """
Flag for limited seek ability by byte range.
    """
    DLNA_LOP_TIME = 1 << 30
    """
Flag for limited seek ability by time.
    """
    DLNA_RSTP_PAUSE_SUPPORT = 1 << 25
    """
Flag for streams.
    """
    DLNA_S0_INCREASING = 1 << 27
    """
Flag for stream with changing start time.
    """
    DLNA_SEEK_BYTES = 1
    """
Flag for seek ability by byte range.
    """
    DLNA_SEEK_TIME = 1 << 1
    """
Flag for seek ability by time.
    """
    DLNA_SERVERSIDE_FLOW_CONTROL = 1 << 31
    """
Flag for server-side data flow control corresponding to the current
playback speed.
    """
    DLNA_SN_INCREASING = 1 << 26
    """
Flag for stream with changing end time.
    """
    DLNA_STREAMING_TRANSFER = 1 << 24
    """
Flag for streams.
    """

    def __init__(self):
        """
Constructor __init__(DlnaItemResourceMixin)

:since: v0.2.00
        """

        self.dlna_content_features = "*"
        """
UPnP DLNA content features
        """

        self.supported_features['dlna_content_features'] = True
    #

    def get_dlna_content_features(self):
        """
Returns the UPnP DLNA content features known used for the 4th-field.

:return: (str) UPnP DLNA compliant content features
:since:  v0.2.00
        """

        return self.dlna_content_features
    #

    def _refresh_dlna_content_features(self):
        """
Initializes the UPnP DLNA content features variable.

:since: v0.2.00
        """

        dlna_content_features = "DLNA.ORG_OP={0:0>2x};DLNA.ORG_CI=0;DLNA.ORG_FLAGS={1:0>8x}000000000000000000000000"

        self.dlna_content_features = dlna_content_features.format(DlnaItemResourceMixin.DLNA_SEEK_BYTES,
                                                                  (DlnaItemResourceMixin.DLNA_0150
                                                                   | DlnaItemResourceMixin.DLNA_HTTP_STALLING
                                                                  )
                                                                 )
    #

    def _refresh_dlna_res_protocol(self):
        """
Initializes the UPnP DLNA res protocol variable.

:since: v0.2.00
        """

        self.didl_res_protocol = "http-get:*:{0}:{1}".format(self.get_mimetype(),
                                                             self.dlna_content_features
                                                            )
    #
#
