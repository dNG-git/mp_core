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

from dNG.pas.data.http.translatable_exception import TranslatableError
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from .module import Module

class Index(Module):
#
	"""
Service for "m=mp;s=index"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def execute_index(self):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		self.execute_list_root_containers()
	#

	def execute_list_root_containers(self):
	#
		"""
Action for "list_root_containers"

:since: v0.1.00
		"""

		page = InputFilter.filter_int(self.request.get_dsd("mpage", 1))

		L10n.init("mp_core")

		session = self.request.get_session()
		user_profile = (None if (session == None) else session.get_user_profile())

		if (user_profile == None
		    or (not user_profile.is_type("ad"))
		   ): raise TranslatableError("core_access_denied", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED),
		               L10n.get("mp_core_root_container_new"),
		               { "m": "mp", "s": "root_container", "a": "new" },
		               icon = "mini-default-option",
		               priority = 3
		              )

		content = { "title": L10n.get("mp_core_root_container_list"),
		            "entries": MpEntry.get_root_containers_count(),
		            "page": page
		          }

		self.response.init()
		self.response.set_title(L10n.get("mp_core_root_container_list"))
		self.response.add_oset_content("mp.container", content)
	#
#

##j## EOF