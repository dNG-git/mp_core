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

# pylint: disable=import-error,no-name-in-module

import socket

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.http.streaming import Streaming
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.module.named_loader import NamedLoader
from .module import Module

class Stream(Module):
#
	"""
Service for "m=upnp;s=stream"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    mp
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

		if (not isinstance(self.request, HttpUpnpRequest)): raise TranslatableException("pas_http_core_400", 400)

		client_host = self.request.get_client_host()
		upnp_control_point = self.request.get_upnp_control_point()
		url = self.request.get_dsd("src")

		client = Client.load_user_agent(self.client_user_agent)

		self.response.init(True, compress = client.get("upnp_http_compression_supported", True))

		if (client_host == None): is_allowed = False
		else:
		#
			ip_address_paths = socket.getaddrinfo(client_host, self.request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
			is_allowed = (False if (len(ip_address_paths) < 1) else upnp_control_point.is_ip_allowed(ip_address_paths[0][4][0]))
		#

		resource = (Resource.load_cds_id(url, self.client_user_agent) if (is_allowed) else None)
		stream_resource = None

		if (resource != None):
		#
			stream_resource = (resource
			                   if (isinstance(resource, AbstractStream)) else
			                   resource.get_content(0)
			                  )
		#

		if (stream_resource != None):
		#
			if (self.response.is_supported("headers")):
			#
				if (self.request.get_header("getcontentFeatures.dlna.org") == "1"
				    and stream_resource.is_supported("dlna_content_features")
				   ):
				#
					self.response.set_header("contentFeatures.dlna.org",
					                         stream_resource.get_dlna_content_features()
					                        )
				#

				upnp_transfer_mode = self.request.get_header("transferMode.dlna.org")

				if (upnp_transfer_mode == "Background"
				    or upnp_transfer_mode == "Interactive"
				    or upnp_transfer_mode == "Streaming"
				   ): self.response.set_header("transferMode.dlna.org", upnp_transfer_mode)

				self.response.set_header("Content-Type", resource.get_mimetype())
			#

			stream_url = InputFilter.filter_control_chars(stream_resource.get_id())
			stream_url_elements = urlsplit(stream_url)

			streamer = (None if (stream_url_elements.scheme == "") else NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format("".join([word.capitalize() for word in stream_url_elements.scheme.split("-")])), False))
			Streaming.run(self.request, streamer, stream_url, self.response)
		#
		else: self.response.handle_critical_error("core_access_denied")
	#
#

##j## EOF