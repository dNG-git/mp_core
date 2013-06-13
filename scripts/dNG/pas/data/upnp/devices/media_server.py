# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.devices.MediaServer
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

#from dNG.pas.data.upnp.services.av_transport import AvTransport
from dNG.pas.data.upnp.services.connection_manager import ConnectionManager
from dNG.pas.data.upnp.services.content_directory import ContentDirectory
#from dNG.pas.data.upnp.services.scheduled_recording import ScheduledRecording
from .abstract_device import AbstractDevice

class MediaServer(AbstractDevice):
#
	"""
The UPnP MediaServer:1 device implementation.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(MediaServer)

:since: v0.1.00
		"""

		AbstractDevice.__init__(self)

		self.type = "MediaServer"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"
	#

	def init_device(self, control_point, udn = None, configid = None):
	#
		"""
Initialize a host device.

:return: (bool) Returns true if initialization was successful.
:since: v0.1.00
		"""

		AbstractDevice.init_device(self, control_point, udn, configid)

		self.device_model = "UPnP media server"
		self.device_model_desc = "Python based UPnP media server"
		self.device_model_url = "http://www.direct-netware.de/redirect.py?pas;upnp"
		self.device_model_version = "#echo(pasUPnPVersion)#"
		self.manufacturer = "direct Netware Group"
		self.manufacturer_url = "http://www.direct-netware.de"
		self.spec_major = 1
		self.spec_minor = 1

		#service = AvTransport()
		#if (service.init_service(self, configid = self.configid)): self.service_add(service)

		service = ConnectionManager()
		if (service.init_service(self, configid = self.configid)): self.service_add(service)

		service = ContentDirectory()
		if (service.init_service(self, configid = self.configid)): self.service_add(service)

		#service = ScheduledRecording()
		#if (service.init_service(self, configid = self.configid)): self.service_add(service)

		return True
	#

	def get_xml(self, flush = True):
	#
		"""
Returns the UPnP device description.

:param flush: True to flush the XML parser instance and return the string
              representation.

:return: (mixed) Device description XML as string or XML parser instance
:since:  v0.1.00
		"""

		_return = AbstractDevice.get_xml(self, False)
		_return.node_add("root device dlna:X_DLNADOC", "DMS-1.50", { "xmlns:dlna": "urn:schemas-dlna-org:device-1-0" })
		# upload _return.node_add("root device dlna:X_DLNACAP", "", { "xmlns:dlna": "urn:schemas-dlna-org:device-1-0" })

		return (_return.cache_export(True) if (flush) else _return)
	#
#

##j## EOF