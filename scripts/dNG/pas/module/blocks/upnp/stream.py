# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.upnp.Stream
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

import socket

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.translatable_exception import TranslatableException
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.http.streaming import Streaming
#from dNG.pas.data.http.throttled_streamer import direct_throttled_streamer
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader
from .module import Module

class Stream(Module):
#
	"""
Service for "m=upnp;s=stream"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def execute_source(self):
	#
		"""
Action for "source"

:since: v0.1.00
		"""

		if (not isinstance(self.request, HttpUpnpRequest)): raise TranslatableException("pas_http_error_400")

		client_host = self.request.get_client_host()
		upnp_control_point = self.request.get_upnp_control_point()
		url = self.request.get_dsd("src")

		if (client_host == None): is_allowed = False
		else:
		#
			ip_address_paths = socket.getaddrinfo(client_host, self.request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
			is_allowed = (False if (len(ip_address_paths) < 1) else upnp_control_point.is_ip_allowed(ip_address_paths[0][4][0]))
		#

		if (is_allowed and Resource.load_cds_id(url, self.request.get_header("User-Agent")) != None):
		#
			url = InputFilter.filter_control_chars(url)
			url_elements = urlsplit(url)

			streamer = (None if (url_elements.scheme == "") else NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format("".join([word.capitalize() for word in url_elements.scheme.split("-")])), False))
			Streaming.run(self.request, streamer, url, self.response)
		#
		else: self.response.handle_critical_error("core_access_denied")
	#
#

##j## EOF