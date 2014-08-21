# -*- coding: utf-8 -*-
##j## BOF

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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
"""

from dNG.pas.data.upnp.client import Client
#from dNG.pas.data.upnp.services.av_transport import AvTransport
from dNG.pas.data.upnp.services.connection_manager import ConnectionManager
from dNG.pas.data.upnp.services.content_directory import ContentDirectory
#from dNG.pas.data.upnp.services.scheduled_recording import ScheduledRecording
from dNG.pas.data.upnp.services.xms_media_receiver_registrar import XMSMediaReceiverRegistrar
from .abstract_device import AbstractDevice

class MediaServer(AbstractDevice):
#
	"""
The UPnP MediaServer:1 device implementation.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
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
		self.device_model_url = "https://www.direct-netware.de/redirect?pas;upnp"
		self.device_model_version = "#echo(mpCoreVersion)#"
		self.manufacturer = "direct Netware Group"
		self.manufacturer_url = "http://www.direct-netware.de"
		self.spec_major = 1
		self.spec_minor = 1

		#service = AvTransport()
		#if (service.init_host(self, configid = self.configid)): self.add_service(service)

		service = ConnectionManager()
		if (service.init_host(self, configid = self.configid)): self.add_service(service)

		service = ContentDirectory()
		if (service.init_host(self, configid = self.configid)): self.add_service(service)

		#service = ScheduledRecording()
		#if (service.init_host(self, configid = self.configid)): self.add_service(service)

		service = XMSMediaReceiverRegistrar()
		if (service.init_host(self, configid = self.configid)): self.add_service(service)

		return True
	#

	def _get_xml(self, xml_resource):
	#
		"""
Returns the UPnP device description for encoding.

:param xml_resource: XML resource

:return: (object) Device description XML resource
:since:  v0.1.01
		"""

		# pylint: disable=maybe-no-member,no-member
		# pylint 1.2.1 gets crazy here and thinks that xml_resource is the same as self

		client = Client.load_user_agent(self.client_user_agent)

		xml_resource = AbstractDevice._get_xml(self, xml_resource)

		xml_resource.add_node("root device dlna:X_DLNADOC", "DMS-1.50", { "xmlns:dlna": "urn:schemas-dlna-org:device-1-0" })
		# TODO: if (client.get("upnp_xml_dlnacap_supported", True)): xml_resource.add_node("root device dlna:X_DLNACAP", "audio-upload,av-upload,image-upload", { "xmlns:dlna": "urn:schemas-dlna-org:device-1-0" }) # TODO: upload

		value = client.get("mp_media_server_device_model")
		if (value != None):  xml_resource.change_node_value("root device modelName", value)

		value = client.get("mp_media_server_device_model_desc")
		if (value != None): xml_resource.change_node_value("root device modelDescription", value)

		value = client.get("mp_media_server_device_model_version")
		if (value != None): xml_resource.change_node_value("root device modelNumber", value)

		value = client.get("mp_media_server_manufacturer")
		if (value != None): xml_resource.change_node_value("root device manufacturer", value)

		return xml_resource
	#
#

##j## EOF