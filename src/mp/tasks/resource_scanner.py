# -*- coding: utf-8 -*-

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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(mpCoreVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,no-name-in-module

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.data.logging.log_line import LogLine
from dNG.data.settings import Settings
from dNG.data.tasks.memory import Memory as MemoryTasks
from dNG.data.upnp.resource import Resource
from dNG.data.upnp.resources.mp_entry import MpEntry
from dNG.database.connection import Connection
from dNG.database.transaction_context import TransactionContext
from dNG.plugins.hook import Hook
from dNG.runtime.thread_lock import ThreadLock
from dNG.tasks.abstract_lrt_hook import AbstractLrtHook
from dNG.vfs.implementation import Implementation
from dNG.vfs.watcher_implementation import WatcherImplementation

from .resource_id_deleter import ResourceIdDeleter
from .resource_metadata_refresh import ResourceMetadataRefresh

class ResourceScanner(AbstractLrtHook):
    """
"ResourceScanner" runs an recursive scan job to find new files for playback.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    # pylint: disable=unused-argument

    _lock = ThreadLock()
    """
Thread safety lock
    """
    _watcher_instances = { }
    """
Watcher instances
    """

    def __init__(self, _id):
        """
Constructor __init__(ResourceScanner)

:since: v0.2.00
        """

        AbstractLrtHook.__init__(self)

        self.id = None
        """
Encapsulating UPnP resource ID
        """
        self.refresh_time = None
        """
Refresh time
        """
        self.vfs_url = None
        """
UPnP encapsulated VFS URL
        """

        self.context_id = "mp.tasks.ResourceScanner"
        self.independent_scheduling = True

        entry_data = None

        with Connection.get_instance():
            is_auto_maintained = False
            resource = MpEntry.load_encapsulating_entry(_id)

            if (isinstance(resource, MpEntry)):
                entry_data = resource.get_data_attributes("resource")
                is_auto_maintained = resource.is_supported("auto_maintenance")
            #

            if (is_auto_maintained):
                if (self.log_handler is not None): self.log_handler.debug("mp.ResourceScanner ignores auto maintained resource ID '{0}'", _id, context = "mp_server")
            elif (entry_data is not None):
                self.id = resource.get_resource_id()
                self.vfs_url = resource.get_vfs_url()

                vfs_scheme = WatcherImplementation.get_scheme_from_vfs_url_if_supported(self.vfs_url)
                vfs_watcher = None

                if (vfs_scheme is not None):
                    with ResourceScanner._lock:
                        if (len(ResourceScanner._watcher_instances) < 1):
                            Hook.register("dNG.pas.upnp.ControlPoint.onShutdown", ResourceScanner.stop)
                        #

                        if (vfs_scheme not in ResourceScanner._watcher_instances):
                            ResourceScanner._watcher_instances[vfs_scheme] = WatcherImplementation.get_instance(vfs_scheme)
                        #

                        vfs_watcher = ResourceScanner._watcher_instances[vfs_scheme]
                    #
                #

                is_watched = False

                if (vfs_watcher is not None and (not vfs_watcher.is_synchronous())):
                    is_watched = (vfs_watcher.is_watched(self.vfs_url, ResourceScanner.on_watcher_event)
                                  or vfs_watcher.register(self.vfs_url, ResourceScanner.on_watcher_event)
                                 )
                #

                if (not is_watched): self.refresh_time = Settings.get("mp_core_entry_scanner_refresh_time", 300)
            elif (self.log_handler is not None): self.log_handler.warning("mp.ResourceScanner refused to scan '{0}'", _id, context = "mp_server")
        #
    #

    def _run_hook(self):
        """
Hook execution

:since: v0.2.00
        """

        resource = None
        vfs_object = (None if (self.vfs_url is None) else Implementation.load_vfs_url(self.vfs_url, True))

        if (self.id is not None
            and vfs_object is not None
            and vfs_object.is_valid()
            and vfs_object.is_directory()
           ):
            if (self.log_handler is not None): self.log_handler.info("mp.ResourceScanner scans the content of '{0}'", self.vfs_url, context = "mp_server")

            content_list = { }

            for child in vfs_object.scan():
                if (child.is_valid()): content_list[child.get_url()] = child.get_time_updated()
                child.close()
            #

            content_added = [ ]
            content_modified = [ ]
            content_deleted = [ ]
            memory_tasks = MemoryTasks.get_instance()

            with Connection.get_instance():
                resource = Resource.load_cds_id(self.id, deleted = True)

                if (resource is not None):
                    for child in resource.get_content_list():
                        child_updated = False

                        child_resource_id = child.get_resource_id()
                        child_vfs_url = child.get_vfs_url()

                        if (child_vfs_url in content_list):
                            if (child.get_type() & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
                                memory_tasks.add("mp.tasks.ResourceScanner.{0}".format(child_resource_id),
                                                 ResourceScanner(child_resource_id),
                                                 0
                                                )
                            #

                            child_data = child.get_data_attributes("time_sortable", "refreshable")

                            child_updated = (child_data['time_sortable'] is None
                                             or int(child_data['time_sortable']) < int(content_list[child_vfs_url])
                                             or child_data['refreshable']
                                            )

                            del(content_list[child_vfs_url])

                            if (child_updated): content_modified.append(child_resource_id)
                        else: content_deleted.append(child_resource_id)
                    #

                    content_added = content_list.keys()
                else: memory_tasks.remove("mp.tasks.ResourceScanner.{0}".format(self.vfs_url))
            #

            if (len(content_added) > 0):
                for child_vfs_url in content_added:
                    with TransactionContext():
                        child_resource_id = None

                        child = MpEntry.load_encapsulating_entry(child_vfs_url)

                        if (child is not None and resource.add_content(child)):
                            child.set_data_attributes(refreshable = True)
                            child.save()

                            child_resource_id = child.get_resource_id()
                            child.close()

                            if (self.log_handler is not None): self.log_handler.info("mp.ResourceScanner added entry '{0}'", child_vfs_url, context = "mp_server")
                        elif (self.log_handler is not None): self.log_handler.warning("mp.ResourceScanner failed to add entry '{0}'", child_vfs_url, context = "mp_server")

                        if (child_resource_id is not None):
                            memory_tasks.add("mp.tasks.ResourceScanner.{0}".format(child_resource_id), ResourceScanner(child_resource_id), 0)
                            memory_tasks.add("mp.tasks.ResourceMetadataRefresh.{0}".format(child_resource_id), ResourceMetadataRefresh(child_resource_id), 0)
                        #
                    #
                #
            #

            if (len(content_deleted) > 0):
                for child_resource_id in content_deleted:
                    with Connection.get_instance():
                        child = MpEntry.load_cds_id(child_resource_id, deleted = True)

                        if (child is not None):
                            child_db_id = child.get_id()
                            child.close()

                            memory_tasks.add("mp.tasks.ResourceIdDeleter.{0}".format(child_db_id),
                                             ResourceIdDeleter(child_db_id),
                                             0
                                            )

                            memory_tasks.remove("mp.tasks.ResourceScanner.{0}".format(child_resource_id))
                            memory_tasks.remove("mp.tasks.ResourceMetadataRefresh.{0}".format(child_resource_id))
                        #
                    #
                #
            #

            for child_resource_id in content_modified: memory_tasks.add("mp.tasks.ResourceMetadataRefresh.{0}".format(child_resource_id), ResourceMetadataRefresh(child_resource_id), 0)

            resource.close()
        #

        if (resource is not None and self.refresh_time is not None):
            memory_tasks.add("mp.tasks.ResourceScanner.{0}".format(self.id),
                             ResourceScanner(self.id),
                             self.refresh_time
                            )
        #
    #

    @staticmethod
    def on_watcher_event(event_type, url, changed_value = None):
        """
Schedules metadata refreshes for a changed file or directory.

:param event_type: Filesystem watcher event type
:param url: Filesystem URL watched
:param changed_value: Changed filesystem value

:since: v0.2.00
        """

        if (changed_value is not None):
            changed_value = quote(changed_value)
            child_id = url + "/" + changed_value

            if (event_type == WatcherImplementation.EVENT_TYPE_CREATED):
                child = None
                is_added = False

                with TransactionContext():
                    parent = MpEntry.load_encapsulating_entry(url)
                    if (parent is not None): child = MpEntry.load_encapsulating_entry(child_id)

                    if (child is not None and parent.add_content(child)):
                        child.set_data_attributes(refreshable = True)
                        child.save()

                        is_added = True
                    else: LogLine.warning("mp.ResourceScanner failed to add entry '{0}'", child_id, context = "mp_server")
                #

                if (is_added):
                    LogLine.info("mp.ResourceScanner added entry '{0}'", child_id, context = "mp_server")

                    memory_tasks = MemoryTasks.get_instance()
                    memory_tasks.add("mp.tasks.ResourceScanner.{0}".format(child_id), ResourceScanner(child_id), 0)
                    memory_tasks.add("mp.tasks.ResourceMetadataRefresh.{0}".format(child_id), ResourceMetadataRefresh(child_id), 0)
                #
            elif (event_type == WatcherImplementation.EVENT_TYPE_DELETED):
                with Connection.get_instance():
                    child = MpEntry.load_encapsulating_entry(child_id, deleted = True)

                    if (child is not None):
                        child_db_id = child.get_id()
                        memory_tasks = MemoryTasks.get_instance()

                        memory_tasks.add("mp.tasks.ResourceIdDeleter.{0}".format(child_db_id),
                                         ResourceIdDeleter(child_db_id),
                                         0
                                        )

                        memory_tasks.remove("mp.tasks.ResourceScanner.{0}".format(child_id))
                        memory_tasks.remove("mp.tasks.ResourceMetadataRefresh.{0}".format(child_id))
                    #
                #
            elif (event_type == WatcherImplementation.EVENT_TYPE_MODIFIED):
                MemoryTasks.get_instance().add("mp.tasks.ResourceMetadataRefresh.{0}".format(child_id), ResourceMetadataRefresh(child_id), 0)
            #
        elif (event_type == WatcherImplementation.EVENT_TYPE_DELETED):
            with Connection.get_instance():
                child = MpEntry.load_encapsulating_entry(url, deleted = True)

                if (child is not None):
                    child_db_id = child.get_id()
                    memory_tasks = MemoryTasks.get_instance()

                    memory_tasks.add("mp.tasks.ResourceIdDeleter.{0}".format(child_db_id),
                                     ResourceIdDeleter(child_db_id),
                                     0
                                    )

                    memory_tasks.remove("mp.tasks.ResourceScanner.{0}".format(child_id))
                    memory_tasks.remove("mp.tasks.ResourceMetadataRefresh.{0}".format(child_id))
                #
            #
        elif (event_type == WatcherImplementation.EVENT_TYPE_MODIFIED):
            MemoryTasks.get_instance().add("mp.tasks.ResourceMetadataRefresh.{0}".format(url), ResourceMetadataRefresh(url), 0)
        #
    #

    @staticmethod
    def stop(params = None, last_return = None):
        """
Called for "dNG.pas.upnp.ControlPoint.onShutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
        """

        if (len(ResourceScanner._watcher_instances) > 1):
            with ResourceScanner._lock:
                # Thread safety
                for vfs_scheme in ResourceScanner._watcher_instances:
                    ResourceScanner._watcher_instances[vfs_scheme].disable()
                #

                ResourceScanner._watcher_instances = { }
            #
        #

        return last_return
    #
#
