# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.tasks.upnp.VpmcEntryScanner
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

from threading import RLock

try: from urllib.parse import unquote, urlsplit
except ImportError:
#
	from urllib import unquote
	from urlparse import urlsplit
#

from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.tasks.memory import Memory
from dNG.pas.data.text.md5 import Md5
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.vpmc_entry import VpmcEntry
from dNG.pas.database.connection import Connection
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks
from dNG.pas.vfs.abstract_watcher import AbstractWatcher
from dNG.pas.vfs.file.watcher import Watcher

class VpmcEntryScanner(object):
#
	"""
"VpmcScanner" runs an recursive scan job to find new files for playback.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    vpmc
:subpackage: core
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	hooked = False
	"""
Hooks registered
	"""
	synchronized = RLock()
	"""
Lock used in multi thread environments.
	"""

	def __init__(self, resource):
	#
		"""
Constructor __init__(Resource)

:since: v0.1.00
		"""

		self.encapsulated_resource = None
		"""
UPnP resource
		"""
		self.encapsulating_id = None
		"""
UPnP resource
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.refresh_time = None
		"""
UPnP resource
		"""
		self.watcher_instance = None
		"""
Watcher instance
		"""

		entry_data = None

		if (isinstance(resource, VpmcEntry)):
		#
			entry_data = resource.data_get("resource")
			url_elements = urlsplit(entry_data['resource'])
		#

		if (entry_data != None and url_elements.scheme == "vpmc-entry" and url_elements.netloc != ""):
		#
			encapsulated_resource = NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}".format("".join([word.capitalize() for word in url_elements.netloc.split("-")])), False)

			if (isinstance(encapsulated_resource, Resource) and encapsulated_resource.init_cds_id("{0}:///{1}".format(url_elements.netloc, url_elements.path[1:]))):
			#
				self.encapsulating_id = entry_data['resource']
				self.encapsulated_resource = encapsulated_resource

				with VpmcEntryScanner.synchronized:
				#
					if (self.watcher_instance == None):
					#
						self.watcher_instance = Watcher()
						Hooks.register("dNG.pas.upnp.control_point.shutdown", self.stop)
					#

					if (not VpmcEntryScanner.hooked):
					#
						Hooks.register("dNG.pas.tasks.upnp.vpmc_entry_scanner.refresh_metadata", VpmcEntryScanner.refresh_metadata)
						Hooks.register("dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", VpmcEntryScanner.scan_entry)
						VpmcEntryScanner.hooked = True
					#
				#

				if ((not self.encapsulated_resource.is_filesystem_resource()) or self.watcher_instance.is_synchronous()): self.refresh_time = Settings.get("vpmc_core_entry_scanner_refresh_time", 300)
				else:
				#
					file_url = "file:///{0}".format(unquote(url_elements.path[1:]))
					if (not self.watcher_instance.is_watched(file_url, VpmcEntryScanner.filesystem_modified)): self.watcher_instance.register(file_url, VpmcEntryScanner.filesystem_modified)
				#

				if (resource.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
				#
					Memory.get_instance().task_add(Md5.hash(self.encapsulated_resource.get_id()), "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", 0, scanner = self)

					for child in resource.content_get():
					#
						if (isinstance(child, VpmcEntry)): VpmcEntryScanner(child)
					#
				#
			#
			elif (self.log_handler != None): self.log_handler.warning("pas.upnp.VpmcEntryScanner failed to initialize the resource for '{0}'".format(entry_data['resource']))
		#
		elif (self.log_handler != None): self.log_handler.warning("pas.upnp.VpmcEntryScanner refused to scan '{0}'".format(resource.get_id()))
	#

	def scan(self):
	#
		"""
Called for "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
		"""

		if (self.encapsulating_id != None):
		#
			if (self.log_handler != None): self.log_handler.info("pas.upnp.VpmcEntryScanner scans the content of '{0}'".format(self.encapsulated_resource.get_id()))

			content_list = { }

			for child in self.encapsulated_resource.content_get(): content_list[child.get_id()] = child.get_timestamp()

			content_added = [ ]
			content_modified = [ ]
			content_deleted = [ ]

			with Connection.get_instance() as database:
			#
				encapsulating_resource = Resource.load_cds_id(self.encapsulating_id)

				if (encapsulating_resource != None):
				#
					for child in encapsulating_resource.content_get():
					#
						child_updated = False

						if (isinstance(child, VpmcEntry)):
						#
							child_id = child.get_encapsulated_id()

							if (child_id in content_list):
							#
								child_data = child.data_get("sorting_date")
								child_updated = (child_data['sorting_date'] == None or child_data['sorting_date'] < content_list[child_id])
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
				else: Memory.get_instance().unregister(Md5.hash("vpmc_core_upnp_entry_scanner_{0}".format(self.encapsulated_resource.get_id())))
			#

			for child_id in content_added:
			#
				with Connection.get_instance() as database:
				#
					encapsulating_child = VpmcEntry.load_encapsulated_entry(child_id)

					if (encapsulating_child != None and encapsulating_resource.content_add(encapsulating_child)):
					#
						encapsulating_child.data_set(sorting_date = content_list[child_id])
						encapsulating_child.save()

						VpmcEntryScanner(encapsulating_child)
						if (self.log_handler != None): self.log_handler.info("pas.upnp.VpmcEntryScanner added entry '{0}'".format(child_id))
					#
					elif (self.log_handler != None): self.log_handler.warning("pas.upnp.VpmcEntryScanner failed to add entry '{0}'".format(child_id))
				#
			#

			for child_id in content_deleted:
			#
				with Connection.get_instance() as database:
				#
					encapsulating_child = Resource.load_cds_id(child_id)

					if (isinstance(encapsulating_child, VpmcEntry)):
					#
						if (encapsulating_resource.content_remove(encapsulating_child) and encapsulating_child.delete()):
						#
							if (self.log_handler != None): self.log_handler.info("pas.upnp.VpmcEntryScanner deleted entry '{0}'".format(child_id))

							database.optimize_random(VpmcEntry)
							if (encapsulating_child.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): Memory.get_instance().unregister(Md5.hash("vpmc_core_upnp_entry_scanner_{0}".format(encapsulating_child.get_encapsulated_id())))
						#
						elif (self.log_handler != None): self.log_handler.warning("pas.upnp.VpmcEntryScanner failed to delete entry '{0}'".format(child_id))
					#
				#
			#

			for child_id in content_modified:
			#
				with Connection.get_instance() as database:
				#
					encapsulating_child = Resource.load_cds_id(child_id)
					#Memory.get_instance().task_add(Md5.hash(self.encapsulated_resource.get_id()), "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", self.refresh_time, scanner = self)
				#
			#

			if (self.refresh_time != None): Memory.get_instance().task_add(Md5.hash(self.encapsulated_resource.get_id()), "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", self.refresh_time, scanner = self)
		#
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Called for "dNG.pas.upnp.control_point.shutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
		"""

		if (self.watcher_instance != None): self.watcher_instance.free()
		return last_return
	#

	@staticmethod
	def filesystem_modified(event_type, url, changed_value = None):
	#
		"""
Refresh metadata for changed files or directories.

:param event_type: Filesystem watcher event type
:param url: Filesystem URL watched
:param changed_value: Changed filesystem value

:since:  v0.1.00
		"""

		if (changed_value != None):
		#
			if (event_type == AbstractWatcher.EVENT_TYPE_CREATED):
			#
				child_id = url + "/" + changed_value

				with Connection.get_instance():
				#
					encapsulating_resource = VpmcEntry.load_encapsulated_entry(url)
					encapsulating_child = (None if (encapsulating_resource == None) else VpmcEntry.load_encapsulated_entry(child_id))

					if (encapsulating_child != None and encapsulating_resource.content_add(encapsulating_child)):
					#
						encapsulating_child.data_set(sorting_date = encapsulating_child.get_timestamp())
						encapsulating_child.save()

						VpmcEntryScanner(encapsulating_child)
						LogLine.info("pas.upnp.VpmcEntryScanner added entry '{0}'".format(child_id))
					#
					else: LogLine.warning("pas.upnp.VpmcEntryScanner failed to add entry '{0}'".format(child_id))
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
			#
				child_id = url + "/" + changed_value
				url_elements = urlsplit(child_id)

				with Connection.get_instance() as database:
				#
					"""
File is already deleted so we need to trick a bit
					"""

					encapsulating_child = VpmcEntry()
					encapsulating_resource = (encapsulating_child.load_parent() if (encapsulating_child.init_cds_id("vpmc-entry://{0}{1}".format(url_elements.scheme, url_elements.path))) else None)

					if (encapsulating_resource != None and encapsulating_resource.content_remove(encapsulating_child) and encapsulating_child.delete()):
					#
						LogLine.info("pas.upnp.VpmcEntryScanner deleted entry '{0}'".format(child_id))

						database.optimize_random(VpmcEntry)
						Memory.get_instance().unregister(Md5.hash("vpmc_core_upnp_entry_scanner_{0}".format(encapsulating_child.get_encapsulated_id())))
					#
					else: LogLine.warning("pas.upnp.VpmcEntryScanner failed to delete entry '{0}'".format(child_id))
				#
			#
			elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED):
			#
				child_id = url + "/" + changed_value

				with Connection.get_instance():
				#
					encapsulating_resource = VpmcEntry.load_encapsulated_entry(child_id)
					#Memory.get_instance().task_add(Md5.hash(self.encapsulated_resource.get_id()), "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", self.refresh_time, scanner = self)
				#
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_DELETED):
		#
			url_elements = urlsplit(url)

			with Connection.get_instance() as database:
			#
				"""
File is already deleted so we need to trick a bit
				"""

				encapsulating_resource = VpmcEntry()
				if (not encapsulating_resource.init_cds_id("vpmc-entry://{0}{1}".format(url_elements.scheme, url_elements.path))): encapsulating_resource = None

				if (encapsulating_resource != None and encapsulating_resource.content_remove(encapsulating_child) and encapsulating_child.delete()):
				#
					LogLine.info("pas.upnp.VpmcEntryScanner deleted entry '{0}'".format(child_id))

					database.optimize_random(VpmcEntry)
					Memory.get_instance().unregister(Md5.hash("vpmc_core_upnp_entry_scanner_{0}".format(encapsulating_child.get_encapsulated_id())))
				#
				else: LogLine.warning("pas.upnp.VpmcEntryScanner failed to delete entry '{0}'".format(child_id))
			#
		#
		elif (event_type == AbstractWatcher.EVENT_TYPE_MODIFIED):
		#
			with Connection.get_instance():
			#
				encapsulating_resource = VpmcEntry.load_encapsulated_entry(url)
				#Memory.get_instance().task_add(Md5.hash(self.encapsulated_resource.get_id()), "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry", self.refresh_time, scanner = self)
			#
		#
	#

	@staticmethod
	def refresh_metadata(params, last_return):
	#
		"""
Called for "dNG.pas.tasks.upnp.vpmc_entry_scanner.refresh_metadata"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
		"""

		_return = last_return

		return _return
	#

	@staticmethod
	def scan_entry(params, last_return):
	#
		"""
Called for "dNG.pas.tasks.upnp.vpmc_entry_scanner.scan_entry"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
		"""

		_return = last_return

		if ("scanner" in params):
		#
			params['scanner'].scan()
			_return = True
		#

		return _return
	#
#

##j## EOF