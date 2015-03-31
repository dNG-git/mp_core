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

# pylint: disable=import-error,no-name-in-module

try: from urllib.parse import parse_qsl, unquote, urlsplit
except ImportError: from urlparse import parse_qsl, unquote, urlsplit

from dNG.pas.data.upnp.resource import Resource
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.not_implemented_exception import NotImplementedException

class HookResource(Resource):
#
	"""
"HookResource" is a hook based UPnP resource.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(HookResource)

:since: v0.1.02
		"""

		Resource.__init__(self)

		self.hook_id = None
		"""
UPnP resource's hook ID
		"""
		self.hook_params = { }
		"""
UPnP resource hook's parameters
		"""

		self.virtual_resource = True
	#

	def add_content(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.02
		"""

		raise NotImplementedException()
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:since: v0.1.02
		"""

		raise NotImplementedException()
	#

	def init(self, data):
	#
		"""
Initializes a new resource with the data given.

:param data: UPnP resource data

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		if ("name" not in data): data['name'] = self.hook_id
		if ("type" not in data): data['type'] = HookResource.TYPE_CDS_CONTAINER
		if ("type_class" not in data): data['type_class'] = "object.container"

		return Resource.init(self, data)
	#

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		Resource.init_cds_id(self, _id, client_user_agent, deleted)
		_return = (self.resource_id is not None)

		if (_return):
		#
			url_elements = urlsplit(self.resource_id)
			url_path_elements = url_elements.path[1:].split("/", 1)

			hook_id = url_path_elements[0]

			hook_params = (dict(parse_qsl(unquote(url_path_elements[1]), keep_blank_values = True))
			               if (len(url_path_elements) == 2) else
			               { }
			              )

			resource_data = Hook.call("dNG.mp.upnp.HookResource.getResourceData", id = hook_id, **hook_params)

			if (self.init(resource_data)):
			#
				self.hook_id = hook_id
				self.hook_params = hook_params
			#
			else: _return = False
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.02
		"""

		_return = False

		params = self.hook_params.copy()
		params['id'] = self.hook_id
		params['offset'] = self.content_offset
		params['limit'] = self.content_limit

		children = Hook.call("dNG.mp.upnp.HookResource.getChildren", **params)

		if (children is not None):
		#
			self.content = children
			_return = True
		#

		return _return
	#

	def remove_content(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.02
		"""

		raise NotImplementedException()
	#
#

##j## EOF