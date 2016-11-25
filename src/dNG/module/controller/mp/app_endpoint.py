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

from dNG.data.http.translatable_error import TranslatableError
from dNG.data.session.implementation import Implementation as Session
from dNG.data.settings import Settings
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.link import Link
from dNG.data.upnp.client_settings_mixin import ClientSettingsMixin
from dNG.module.controller.upnp.access_check_mixin import AccessCheckMixin

from .module import Module

class AppEndpoint(Module, AccessCheckMixin, ClientSettingsMixin):
    """
Service for "m=mp;s=app_endpoint"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(AppEndpoint)

:since: v0.2.00
        """

        Module.__init__(self)
        AccessCheckMixin.__init__(self)
        ClientSettingsMixin.__init__(self)
    #

    def execute_api_get_configuration(self):
        """
Action for "api_get_configuration"

:since: v0.2.00
        """

        user_agent = self.request.get_header("User-Agent")

        template_type = (self.request.get_parameter_chained("attype", "ten_foot_web")
                         if (self.request.is_supported("parameters_chained")) else
                         self.request.get_parameter("attype", "ten_foot_web")
                        )

        template_type = "leanback_{0}".format(InputFilter.filter_control_chars(template_type).strip())

        self.response.init(True)
        self.response.set_header("Access-Control-Allow-Origin", "*")

        if (not self.response.is_supported("dict_result_renderer")): raise TranslatableError("core_access_denied", 403)

        self._ensure_access_granted()

        session = Session.load()

        if (session.get("mp.leanback.user_agent") != user_agent):
            session.set("mp.leanback.access_granted", True)
            session.set("mp.leanback.user_agent", user_agent)
            session.set("mp.leanback.template_type", template_type)
            session.set_cookie(Settings.get("pas_http_site_cookies_supported", True))

            session.save()

            self.request.set_session(session)
        #

        url_parameters = { "m": "mp", "s": "leanback", "a": "dashboard", "uuid": session.get_uuid() }
        self.response.set_result({ "url": Link.get_preferred("upnp").build_url(Link.TYPE_ABSOLUTE_URL, url_parameters) })
    #
#
