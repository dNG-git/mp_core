# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.tasks.mp.ResourceScanner
"""
"""n// NOTE
----------------------------------------------------------------------------
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
----------------------------------------------------------------------------
NOTE_END //n"""

# pylint: disable=import-error,no-name-in-module

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.database.connection import Connection
from dNG.pas.plugins.hooks import Hooks
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	lock = ThreadLock()
	"""
Thread safety lock
	"""
	watcher_instance = None
	"""
Watcher instance
	"""

	def __init__(self, resource):
	#
		"""
Constructor __init__(ResourceScanner)

:since: v0.1.01
		"""

		AbstractLrtHook.__init__(self)

		self.encapsulated_resource = None
		"""
UPnP resource
		"""
		self.encapsulating_id = None
		"""
UPnP resource
		"""
		self.refresh_time = None
		"""
UPnP resource
		"""

		self.context_id = "dNG.pas.tasks.mp.ResourceScanner"
		self.independent_scheduling = True

		entry_data = None

		if (isinstance(resource, MpEntry)): entry_data = resource.data_get("resource")

		if (entry_data != None):
		#
			with Connection.get_instance():
			#
				encapsulated_resource = resource.load_encapsulated_resource(deleted = True)

				if (isinstance(encapsulated_resource, Resource)):
				#
					self.encapsulating_id = resource.get_id()
					self.encapsulated_resource = encapsulated_resource

					if (ResourceScanner.watcher_instance == None):
					#
						# Instance could be created in another thread so check again
						with ResourceScanner.lock:
						#
							if (ResourceScanner.watcher_instance == None):
							#
								ResourceScanner.watcher_instance = Watcher()
								Hooks.register("dNG.pas.upnp.ControlPoint.shutdown", ResourceScanner.stop)
							#
						#
					#

					is_watched = False

					if (self.encapsulated_resource.is_filesystem_resource() and (not ResourceScanner.watcher_instance.is_synchronous())):
					#
						file_url = "file:///{0}".format(quote(self.encapsulated_resource.get_path(), "/"))
						if (ResourceScanner.watcher_instance.is_watched(file_url, ResourceScanner.filesystem_modified) or ResourceScanner.watcher_instance.register(file_url, ResourceScanner.filesystem_modified)): is_watched = True
					#

					if (not is_watched): self.refresh_time = Settings.get("mp_core_entry_scanner_refresh_time", 300)
				#
				elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to initialize the resource for '{0}'".format(entry_data['resource']))
			#
		#
		elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner refused to scan '{0}'".format(resource.get_id()))
	#

	def _run_hook(self):
	#
		"""
Hook execution

:since: v0.1.01
		"""

		if (self.encapsulating_id != None and self.encapsulated_resource.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner scans the content of '{0}'".format(self.encapsulated_resource.get_id()))

			content_list = { }

			self.encapsulated_resource.content_flush_cache()
			for child in self.encapsulated_resource.content_get_list(): content_list[child.get_id()] = child.get_timestamp()

			content_added = [ ]
			content_modified = [ ]
			content_deleted = [ ]
			encapsulating_entry = None
			memory_tasks = MemoryTasks.get_instance()

			with Connection.get_instance() as database:
			#
				encapsulating_entry = Resource.load_cds_id(self.encapsulating_id, deleted = True)

				if (encapsulating_entry != None):
				#
					for child in encapsulating_entry.content_get_list():
					#
						child_updated = False

						if (isinstance(child, MpEntry)):
						#
							if (encapsulating_entry.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): MemoryTasks.get_instance().task_add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child.get_id()), ResourceScanner(child), 0)
							child_id = child.get_encapsulated_id()

							if (child_id in content_list):
							#
								child_data = child.data_get("time_sortable", "refreshable")
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
				else: memory_tasks.task_remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(self.encapsulated_resource.get_id()))
			#

			if (len(content_added) > 0):
			#
				with Connection.get_instance() as database:
				#
					for child_id in content_added:
					#
						is_added = False

						encapsulating_child = MpEntry.load_encapsulating_entry(child_id)

						if (encapsulating_child != None and encapsulating_entry.content_add(encapsulating_child)):
						#
							encapsulating_child.data_set(refreshable = True)
							encapsulating_child.save()
							is_added = True

							if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner added entry '{0}'".format(child_id))
						#
						elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to add entry '{0}'".format(child_id))

						if (is_added):
						#
							memory_tasks.task_add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child_id), ResourceScanner(encapsulating_child), 0)
							memory_tasks.task_add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
						#
					#
				#
			#

			if (len(content_deleted) > 0):
			#
				with Connection.get_instance() as database:
				#
					for child_id in content_deleted:
					#
						encapsulating_child = MpEntry.load_encapsulating_entry(child_id, deleted = True)

						if (encapsulating_child != None and encapsulating_entry.content_remove(encapsulating_child) and encapsulating_child.delete()):
						#
							if (self.log_handler != None): self.log_handler.info("mp.ResourceScanner deleted entry '{0}'".format(child_id))

							database.optimize_random(MpEntry)
							if (encapsulating_child.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): memory_tasks.task_remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
						#
						elif (self.log_handler != None): self.log_handler.warning("mp.ResourceScanner failed to delete entry '{0}'".format(child_id))
					#
				#
			#

			for child_id in content_modified: memory_tasks.task_add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)

			if (self.refresh_time != None): memory_tasks.task_add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_entry.get_id()), ResourceScanner(encapsulating_entry), self.refresh_time)
		#
	#

	@staticmethod
	def filesystem_modified(event_type, url, changed_value = None):
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

				with Connection.get_instance():
				#
					encapsulating_entry = MpEntry.load_encapsulating_entry(url)
					if (encapsulating_entry != None): encapsulating_child = MpEntry.load_encapsulating_entry(child_id)

					if (encapsulating_child != None and encapsulating_entry.content_add(encapsulating_child)):
					#
						encapsulating_child.data_set(time_sortable = encapsulating_child.get_timestamp())
						encapsulating_child.save()
						is_added = True

						ResourceScanner(encapsulating_child)
						LogLine.info("mp.ResourceScanner added entry '{0}'".format(child_id))
					#
					else: LogLine.warning("mp.ResourceScanner failed to add entry '{0}'".format(child_id))
				#

				if (is_added):
				#
					memory_tasks = MemoryTasks.get_instance()
					memory_tasks.task_add("dNG.pas.tasks.mp.ResourceScanner.{0}".format(child_id), ResourceScanner(encapsulating_child), 0)
					memory_tasks.task_add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
			#
				child_id = url + "/" + changed_value

				with Connection.get_instance() as database:
				#
					encapsulating_child = MpEntry.load_encapsulating_entry(child_id, deleted = True)
					encapsulating_entry = (None if (encapsulating_child == None) else encapsulating_child.load_parent())

					if (encapsulating_entry != None and encapsulating_entry.content_remove(encapsulating_child) and encapsulating_child.delete()):
					#
						LogLine.info("mp.ResourceScanner deleted entry '{0}'".format(child_id))

						database.optimize_random(MpEntry)
						MemoryTasks.get_instance().task_remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
					#
					else: LogLine.warning("mp.ResourceScanner failed to delete entry '{0}'".format(child_id))
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED):
			#
				child_id = url + "/" + changed_value
				MemoryTasks.get_instance().task_add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(child_id), ResourceRefreshMetadata(child_id), 0)
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
		#
			with Connection.get_instance() as database:
			#
				encapsulating_child = MpEntry.load_encapsulating_entry(url, deleted = True)
				encapsulating_entry = (None if (encapsulating_child == None) else encapsulating_child.load_parent())

				if (encapsulating_entry != None and encapsulating_entry.content_remove(encapsulating_child) and encapsulating_child.delete()):
				#
					LogLine.info("mp.ResourceScanner deleted entry '{0}'".format(child_id))

					database.optimize_random(MpEntry)
					MemoryTasks.get_instance().task_remove("dNG.pas.tasks.mp.ResourceScanner.{0}".format(encapsulating_child.get_encapsulated_id()))
				#
				else: LogLine.warning("mp.ResourceScanner failed to delete entry '{0}'".format(url))
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED): MemoryTasks.get_instance().task_add("dNG.pas.tasks.mp.ResourceRefreshMetadata.{0}".format(url), ResourceRefreshMetadata(url), 0)
	#

	@staticmethod
	def stop(params = None, last_return = None):
	#
		"""
Called for "dNG.pas.upnp.ControlPoint.shutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.01
		"""

		with ResourceScanner.lock:
		#
			if (ResourceScanner.watcher_instance != None): ResourceScanner.watcher_instance.disable()
		#

		return last_return
	#
#

##j## EOF