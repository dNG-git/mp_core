# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.AbstractStream
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

from base64 import b64encode
from os import path
from threading import RLock

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
#
	from urllib import quote, unquote
	from urlparse import urlsplit
#

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.binary import Binary
from dNG.pas.data.mime_type import MimeType
from dNG.pas.data.text.url import Url
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader

class AbstractStream(Resource):
#
	"""
"Resource" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	DLNA_0150 = 1048576
	"""
Flag for DLNA 1.50 compatibility.
	"""
	DLNA_BACKGROUND_TRANSFER = 4194304
	"""
Flag for background transfer mode.
	"""
	DLNA_INTERACTIVE_TRANSFER = 8388608
	"""
Flag for interactive transfer mode.
	"""
	DLNA_HTTP_STALLING = 2097152
	"""
Flag for the method of stalling the HTTP data flow on pause.
	"""
	DLNA_IS_CONTAINER = 268435456
	"""
Flag for container or playlist elements.
	"""
	DLNA_LOP_BYTES = 536870912
	"""
Flag for limited seek ability by byte range.
	"""
	DLNA_LOP_TIME = 1073741824
	"""
Flag for limited seek ability by time.
	"""
	DLNA_RSTP_PAUSE_SUPPORT = 33554432
	"""
Flag for streams.
	"""
	DLNA_S0_INCREASING = 134217728
	"""
Flag for stream with changing start time.
	"""
	DLNA_SEEK_BYTES = 1
	"""
Flag for seek ability by byte range.
	"""
	DLNA_SEEK_TIME = 2
	"""
Flag for seek ability by time.
	"""
	DLNA_SERVERSIDE_FLOW_CONTROL = 2147483648
	"""
Flag for server-side data flow control corresponding to the current
playback speed.
	"""
	DLNA_SN_INCREASING = 67108864
	"""
Flag for stream with changing end time.
	"""
	DLNA_STREAM = 16777216
	"""
Flag for streams.
	"""

	synchronized = RLock()
	"""
Lock used in multi thread environments.
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractStream)

:since: v0.1.00
		"""

		Resource.__init__(self)

		self.mimetype = None
		"""
UPnP resource mimetype
		"""
	#

	def _content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		_return = False

		self.content = [ ]

		if (self.type != None):
		#
			self.content.append(Url(path = "/upnp/stream/{0}".format(quote(Binary.str(b64encode(Binary.utf8_bytes(self.id)))))).build_url(Url.TYPE_FULL, { }))
			_return = True
		#

		return _return
	#

	def init_cds_id(self, _id, client_user_agent = None, update_id = None):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		_return = Resource.init_cds_id(self, _id, client_user_agent, update_id)

		url_elements = urlsplit(self.id)

		streamer = (None if (url_elements.scheme == "") else NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(url_elements.scheme.capitalize()), False))

		if (streamer.url_supported(self.id)):
		#
			self.name = path.basename(unquote(url_elements.path))
			self.type = AbstractStream.TYPE_CDS_RESOURCE

			if (self.mimetype == None):
			#
				path_ext = path.splitext(url_elements.path)[1]
				mimetype_definition = MimeType.get_instance().get(path_ext[1:])
				if (mimetype_definition != None): self.mimetype = mimetype_definition['mimetype']
			#

			if (self.mimetype != None): self.didl_res_protocol = "http-get:*:{0}:*".format(self.mimetype)

			_return = True
		#

		return _return
	#

	@staticmethod
	def handle_http_request(params = None, last_return = None):
	#
		"""
Handles a valid HTTP task request.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		_return = last_return

		if (_return == None):
		#
			_return = PredefinedHttpRequest()
			_return.set_module("output")
			_return.set_service("throttled")
			_return.set_action("stream")
			_return.set_dsd("url", params['url'])
		#

		return _return
	#
#

##j## EOF