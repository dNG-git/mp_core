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

from math import ceil

from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.page_links_renderer import PageLinksRenderer
from dNG.pas.data.xhtml.oset.file_parser import FileParser
from .module import Module

class RootContainerList(Module):
#
	"""
"RootContainerList" creates a list of UPnP root containers.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def execute_render(self):
	#
		"""
Action for "render"

:since: v0.1.00
		"""

		if (self._is_primary_action()): raise TranslatableError("core_access_denied", 403)

		root_containers_count = MpEntry.get_root_containers_count()

		limit = 20

		page = self.context.get("page", 1)
		pages = (1 if (root_containers_count == 0) else ceil(float(root_containers_count) / limit))

		offset = (0 if (page < 1 or page > pages) else (page - 1) * limit)

		page_link_renderer = PageLinksRenderer({ "__request__": True }, page, pages)
		page_link_renderer.set_dsd_page_key("mpage")
		rendered_links = page_link_renderer.render()

		rendered_content = rendered_links
		for root_container in MpEntry.load_root_containers(offset = offset, limit = limit): rendered_content += self._render_root_container(root_container)
		rendered_content += "\n" + rendered_links

		self.set_action_result(rendered_content)
	#

	def _render_root_container(self, root_container):
	#
		"""
Renders the UPnP root container.

:return: (str) Post XHTML
:since:  v0.1.01
		"""

		root_container_data = root_container.get_data_attributes("id",
		                                                         "title",
		                                                         "resource"
		                                                        )

		content = { "id": root_container_data['id'],
		            "title": root_container_data['title'],
		            "resource": root_container_data['resource']
		          }

		options = [ { "title": L10n.get("mp_core_root_container_edit"),
		              "type": (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
		              "parameters": { "m": "mp",
		                              "s": "root_container",
		                              "a": "edit",
		                              "dsd": { "mcid": root_container_data['id'] }
		                            }
		            },
		            { "title": L10n.get("mp_core_root_container_delete"),
		              "type": Link.TYPE_RELATIVE_URL,
		              "parameters": { "m": "mp",
		                              "s": "root_container",
		                              "a": "delete",
		                              "dsd": { "mcid": root_container_data['id'] }
		                            }
		            }
		          ]

		content['options'] = { "entries": options }

		parser = FileParser()
		parser.set_oset(self.response.get_oset())
		_return = parser.render("mp.list_container", content)

		return _return
	#
#

##j## EOF