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

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.database.connection import Connection
from dNG.pas.database.transaction_context import TransactionContext
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.thread_lock import ThreadLock
from dNG.pas.tasks.abstract_lrt_hook import AbstractLrtHook
from dNG.pas.vfs.abstract_watcher import AbstractWatcher
from dNG.pas.vfs.file.watcher import Watcher
from .resource_refresh_metadata import ResourceRefreshMetadata

class ResourceScanner(AbstractLrtHook):
#
	"""
"ResourceScanner" runs an recursive scan job to find new files for playback.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	_lock = ThreadLock()
	"""
Thread safety lock
	"""
	_watcher_instance = None
	"""
Watcher instance
	"""

	def __init__(self, resource_id):
	#
		"""
Constructor __init__(ResourceScanner)

:since: v0.1.01
		"""

		AbstractLrtHook.__init__(self)

		self.encapsulated_id = None
		"""
Encapsulated UPnP resource ID
		"""
		self.encapsulating_id = None
		"""
Encapsulating UPnP resource ID
		"""
		self.refresh_time = None
		"""
Refresh time
		"""

		self.context_id = "dNG.pas.tasks.mp.ResourceScanner"
		self.independent_scheduling = True

		entry_data = None

		with Connection.get_instance():
		#
			resource = MpEntry.load_encapsulating_entry(resource_id)
			if (isinstance(resource, MpEntry)): entry_data = resource.get_data_attributes("resource")

			if (entry_data != None):
			#
				encapsulated_resource = resource.load_encapsulated_resource(deleted = True)

				if (isinstance(encapsulated_resource, Resource)):
				#
					self.encapsulating_id = resource.get_id()
					self.encapsulated_id = encapsulated_resource.get_id()

					if (ResourceScanner._watcher_instance == None):
					# Thread safety
						with ResourceScanner._lock:
						#
							if (ResourceScanner._watcher_instance == None):
							#
								ResourceScanner._watcher_instance = Watcher()
								Hook.register("dNG.pas.upnp.ControlPoint.onShutdown", ResourceScanner.stop)
							#
						#
					#

					is_watched = False

					if (encapsulated_resource.is_filesystem_resource() and (not ResourceScanner._watcher_instance.is_synchronous())):
					#
						file_url = "file:///{0}".format(quote(encapsulated_resource.get_path(), "/"))

						if (ResourceScanner._watcher_instance.is_watched(file_url, ResourceScanner.on_filesystem_modified)
					 	    or ResourceScanner._watcher_instance.register(file_url, ResourceScanner.on_filesystem_modified)
					 	   ): is_watched = True
					#

					if (not is_watched): self.refresh_time = Settings.get("mp_core_entry_scanner_refresh_time", 300)
				#
				elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to initialize the resource for '{0}'", entry_data['resource'], context = "mp_server")
			#
			elif (self.log_handler != None):
			#
				if (resource == None): self.log_handler.warning("mp.ResourceScanner refused to scan an invalid resource", context = "mp_server")
				else: self.log_handler.warning("mp.ResourceScanner refused to scan '{0}'", resource.get_id(), context = "mp_server")
			#
		#
	#

	def _run_hook(self):
	#
		"""
Hook execution

:since: v0.1.01
		"""

		with Connection.get_instance() as connection:
		#
			encapsulated_resource = Resource.load_cds_id(self.encapsulated_id)
			encapsulating_entry = None

			if (self.encapsulating_id != None and encapsulated_resource.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
			#
				if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner scans the content of '{0}'", self.encapsulated_id, context = "mp_server")

				content_list = { }

				for child in encapsulated_resource.get_content_list(): content_list[child.get_id()] = child.get_timestamp()

				content_added = [ ]
				content_modified = [ ]
				content_deleted = [ ]
				memory_tasks = MemoryTasks.get_instance()

				encapsulating_entry = Resource.load_cds_id(self.encapsulating_id, deleted = True)

				if (encapsulating_entry != None):
				#
					for child in encapsulating_entry.get_content_list():
					#
						child_updated = False

						if (isinstance(child, MpEntry)):
						#
							child_id = child.get_encapsulated_id()

							if (encapsulating_entry.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
							#
								MemoryTasks.get_instance().add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child_id),
								                               ResourceScanner(child_id),
								                               0
								                              )
							#

							if (child_id in content_list):
							#
								child_data = child.get_data_attributes("time_sortable", "refreshable")
								child_updated = (child_data['time_sortable'] == None or child_data['time_sortable'] < content_list[child_id] or child_data['refreshable'])
							#
						#
						else: child_id = child.get_id()

						if (child_id not in content_list): content_deleted.append(child_id)
						else:
						#
							del(content_list[child_id])
							if (child_updated): content_modified.append(child_id)
						#
					#

					content_added = content_list.keys()
				#
				else: memory_tasks.remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(self.encapsulated_id))

				if (len(content_added) > 0):
				#
					with TransactionContext():
					#
						for child_id in content_added:
						#
							is_added = False

							encapsulating_child = MpEntry.load_encapsulating_entry(child_id)

							if (encapsulating_child != None and encapsulating_entry.add_content(encapsulating_child)):
							#
								encapsulating_child.set_data_attributes(refreshable = True)
								encapsulating_child.save()
								is_added = True

								if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner added entry '{0}'", child_id, context = "mp_server")
							#
							elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to add entry '{0}'", child_id, context = "mp_server")

							if (is_added):
							#
								memory_tasks.add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child_id), ResourceScanner(child_id), 0)
								memory_tasks.add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
							#
						#
					#
				#

				if (len(content_deleted) > 0):
				#
					with TransactionContext():
					#
						for child_id in content_deleted:
						#
							encapsulating_child = MpEntry.load_encapsulating_entry(child_id, deleted = True)

							if (encapsulating_child != None and encapsulating_entry.remove_content(encapsulating_child) and encapsulating_child.delete()):
							#
								if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner deleted entry '{0}'", child_id, context = "mp_server")

								connection.optimize_random(MpEntry)

								if (encapsulating_child.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
								#
									memory_tasks.remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
								#
							#
							elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to delete entry '{0}'", child_id, context = "mp_server")
						#
					#
				#

				for child_id in content_modified: memory_tasks.add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
			#

			if (encapsulating_entry != None and self.refresh_time != None):
			#
				memory_tasks.add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(self.encapsulating_id),
				                 ResourceScanner(self.encapsulating_id),
				                 self.refresh_time
				                )
			#
		#
	#

	@staticmethod
	def on_filesystem_modified(event_type, url, changed_value = None):
	#
		"""
Schedules metadata refreshes for a changed file or directory.

:param event_type: Filesystem watcher event type
:param url: Filesystem URL watched
:param changed_value: Changed filesystem value

:since: v0.1.01
		"""

		if (changed_value != None):
		#
			if (event_type == AbstractWatcher.EVENT_TYPE_CREATED):
			#
				child_id = url + "/" + changed_value
				encapsulating_child = None
				is_added = False

				with TransactionContext():
				#
					encapsulating_entry = MpEntry.load_encapsulating_entry(url)
					if (encapsulating_entry != None): encapsulating_child = MpEntry.load_encapsulating_entry(child_id)

					encapsulated_resource = (None
					                         if (encapsulating_child == None) else
					                         encapsulating_entry.load_encapsulated_resource()
					                        )

					if (encapsulated_resource != None and encapsulating_entry.add_content(encapsulating_child)):
					#
						encapsulating_child.set_data_attributes(time_sortable = encapsulated_resource.get_timestamp())
						encapsulating_child.save()
						is_added = True

						ResourceScanner(child_id)
						LogLine.info("mp.ResourceScanner added entry '{0}'", child_id, context = "mp_server")
					#
					else: LogLine.warning("mp.ResourceScanner failed to add entry '{0}'", child_id, context = "mp_server")
				#

				if (is_added):
				#
					memory_tasks = MemoryTasks.get_instance()
					memory_tasks.add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child_id), ResourceScanner(child_id), 0)
					memory_tasks.add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
			#
				child_id = url + "/" + changed_value

				with Connection.get_instance() as connection:
				#
					encapsulating_child = MpEntry.load_encapsulating_entry(child_id, deleted = True)
					encapsulating_entry = (None if (encapsulating_child == None) else encapsulating_child.load_parent())

					if (encapsulating_entry != None and encapsulating_entry.remove_content(encapsulating_child) and encapsulating_child.delete()):
					#
						LogLine.info("mp.ResourceScanner deleted entry '{0}'", child_id, context = "mp_server")

						connection.optimize_random(MpEntry)
						MemoryTasks.get_instance().remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
					#
					else: LogLine.warning("mp.ResourceScanner failed to delete entry '{0}'", child_id, context = "mp_server")
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED):
			#
				child_id = url + "/" + changed_value
				MemoryTasks.get_instance().add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
		#
			with Connection.get_instance() as connection:
			#
				encapsulating_child = MpEntry.load_encapsulating_entry(url, deleted = True)
				encapsulating_entry = (None if (encapsulating_child == None) else encapsulating_child.load_parent())

				if (encapsulating_entry != None and encapsulating_entry.remove_content(encapsulating_child) and encapsulating_child.delete()):
				#
					LogLine.info("mp.ResourceScanner deleted entry '{0}'", child_id, context = "mp_server")

					connection.optimize_random(MpEntry)
					MemoryTasks.get_instance().remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
				#
				else: LogLine.warning("mp.ResourceScanner failed to delete entry '{0}'", url, context = "mp_server")
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED):
		#
			MemoryTasks.get_instance().add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(url), ResourceRefreshMetadata(url), 0)
		#
	#

	@staticmethod
	def stop(params = None, last_return = None):
	#
		"""
Called for "dNG.pas.upnp.ControlPoint.onShutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.01
		"""

		if (ResourceScanner._watcher_instance != None):
		# Thread safety
			with ResourceScanner._lock:
			#
				if (ResourceScanner._watcher_instance != None): ResourceScanner._watcher_instance.disable()
			#
		#

		return last_return
	#
#

##j## EOF