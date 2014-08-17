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

from math import floor

from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.database.condition_definition import ConditionDefinition
from dNG.pas.database.transaction_context import TransactionContext
from dNG.pas.tasks.abstract import Abstract as AbstractTask

class RootContainerDeleter(AbstractTask):
#
	"""
"RootContainerDeleter" runs deletes all database entries for the given
DataLinker main entry ID.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, root_container_id):
	#
		"""
Constructor __init__(RootContainerDeleter)

:since: v0.1.00
		"""

		AbstractTask.__init__(self)

		self.root_container_id = None
		"""
UPnP root container resource ID
		"""
	#

	def run(self):
	#
		"""
Task execution

:since: v0.1.00
		"""

		condition_definition = ConditionDefinition()
		condition_definition.add_exact_match_condition("id_main", self.root_container_id)

		entries_count = DataLinker.get_entries_count_with_condition(condition_definition)

		limit = Settings.get("pas_database_delete_iterator_limit", 50)
		entry_iterator_count = floor(entries_count / limit)

		for _ in range(0, entry_iterator_count):
		#
			with TransactionContext():
			#
				entries = DataLinker.load_entries_list_with_condition(condition_definition, limit = limit)
				for entry in entries: entry.delete()
			#
		#
	#
#

##j## EOF