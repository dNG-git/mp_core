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

from os import path
import re
import os

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.controller.predefined_http_request import PredefinedHttpRequest
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.settings import Settings
from dNG.data.tasks.database_proxy import DatabaseProxy as DatabaseTasks
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.upnp.resources.mp_entry import MpEntry
from dNG.data.xhtml.link import Link
from dNG.data.xhtml.notification_store import NotificationStore
from dNG.data.xhtml.form.info_field import InfoField
from dNG.data.xhtml.form.processor import Processor as FormProcessor
from dNG.data.xhtml.form.select_field import SelectField
from dNG.data.xhtml.form.text_field import TextField
from dNG.database.nothing_matched_exception import NothingMatchedException

from .module import Module

class RootContainer(Module):
    """
Service for "m=mp;s=root_container"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def _check_container_local_pathname_exists(self, field, validator_context):
        """
Form validator that checks if the path name exists if defined.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.2.00
        """

        _return = None

        filepath = path.abspath(field.get_value())

        if ((not path.isdir(filepath))
            or (not os.access(filepath, os.R_OK))
           ): _return = L10n.get("mp_core_form_container_resource_local_pathname_does_not_exist")

        return _return
    #

    def _check_container_local_pathname_unique(self, field, validator_context):
        """
Form validator that checks if the tag is unique if defined.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.2.00
        """

        _return = None

        filepath = path.abspath(field.get_value())
        resource_url = "file:///{0}".format(quote(filepath))

        if (validator_context['form'] == "new"):
            mp_entry = MpEntry.load_encapsulating_entry(resource_url)
            if (mp_entry.is_known()): _return = L10n.get("mp_core_form_container_resource_local_pathname_not_unique")
        #

        return _return
    #

    def execute_delete(self):
        """
Action for "delete"

:since: v0.2.00
        """

        cid = InputFilter.filter_file_path(self.request.get_dsd("mcid", ""))

        source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
        target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

        if (source_iline == ""): source_iline = "m=mp;a=list_root_containers"
        if (target_iline == ""): target_iline = source_iline

        L10n.init("mp_core")

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        user_profile = (None if (session is None) else session.get_user_profile())

        if (user_profile is None
            or (not user_profile.is_type("ad"))
           ): raise TranslatableError("core_access_denied", 403)

        try: mp_entry = MpEntry.load_id(cid)
        except NothingMatchedException as handled_exception: raise TranslatableError("mp_core_cid_invalid", 404, _exception = handled_exception)

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        Link.set_store("servicemenu",
                       Link.TYPE_RELATIVE_URL,
                       L10n.get("core_back"),
                       { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
                       icon = "mini-default-back",
                       priority = 7
                      )

        if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

        mp_entry.delete()

        database_tasks = DatabaseTasks.get_instance()
        database_tasks.add("dNG.pas.upnp.Resource.onDeleted.{0}".format(cid), "dNG.pas.upnp.Resource.onDeleted", 1, container_id = cid)
        database_tasks.add("dNG.pas.upnp.Resource.onRootContainerDeleted.{0}".format(cid), "dNG.pas.upnp.Resource.onRootContainerDeleted", 1, container_id = cid)

        target_iline = re.sub("\\_\\w+\\_\\_", "", target_iline)

        NotificationStore.get_instance().add_completed_info(L10n.get("mp_core_done_root_container_delete"))

        Link.clear_store("servicemenu")

        redirect_request = PredefinedHttpRequest()
        redirect_request.set_iline(target_iline)
        self.request.redirect(redirect_request)
    #

    def execute_edit(self, is_save_mode = False):
        """
Action for "edit"

:since: v0.2.00
        """

        cid = InputFilter.filter_file_path(self.request.get_dsd("mcid", ""))

        source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
        target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

        source = source_iline
        if (source_iline == ""): source_iline = "m=mp;a=list_root_containers"

        target = target_iline
        if (target_iline == ""): target_iline = "m=mp;a=list_root_containers;dsd=mcid+__id_d__"

        L10n.init("mp_core")

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        user_profile = (None if (session is None) else session.get_user_profile())

        if (user_profile is None
            or (not user_profile.is_type("ad"))
           ): raise TranslatableError("core_access_denied", 403)

        try: mp_entry = MpEntry.load_id(cid)
        except NothingMatchedException as handled_exception: raise TranslatableError("mp_core_cid_invalid", 404, _exception = handled_exception)

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        Link.set_store("servicemenu",
                       Link.TYPE_RELATIVE_URL,
                       L10n.get("core_back"),
                       { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
                       icon = "mini-default-back",
                       priority = 7
                      )

        if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

        form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

        form = FormProcessor(form_id)
        form.set_context({ "form": "edit" })

        mp_entry_data = mp_entry.get_data_attributes("title", "resource")

        if (is_save_mode): form.set_input_available()

        field = TextField("mtitle")
        field.set_title(L10n.get("mp_core_container_title"))
        field.set_value(mp_entry_data['title'])
        field.set_required()
        field.set_limits(int(Settings.get("mp_core_container_title_min", 3)))
        form.add(field)

        field = InfoField("mresource_filepath")
        field.set_title(L10n.get("mp_core_container_resource_local_pathname"))
        field.set_value(mp_entry_data['resource'])
        form.add(field)

        if (is_save_mode and form.check()):
            mp_entry_title = InputFilter.filter_control_chars(form.get_value("mtitle"))

            mp_entry.set_data_attributes(title = mp_entry_title,
                                         resource_title = mp_entry_title
                                        )

            mp_entry.save()

            resource_id = mp_entry.get_resource_id()

            database_tasks = DatabaseTasks.get_instance()
            database_tasks.add("dNG.pas.upnp.Resource.onUpdated.{0}".format(cid), "dNG.pas.upnp.Resource.onUpdated", 1, resource_id = resource_id)
            database_tasks.add("dNG.pas.upnp.Resource.onRootContainerUpdated.{0}".format(cid), "dNG.pas.upnp.Resource.onRootContainerUpdated", 1, container_id = resource_id)

            target_iline = target_iline.replace("__id_d__", "{0}".format(cid))
            target_iline = re.sub("\\_\\w+\\_\\_", "", target_iline)

            NotificationStore.get_instance().add_completed_info(L10n.get("mp_core_done_root_container_edit"))

            Link.clear_store("servicemenu")

            redirect_request = PredefinedHttpRequest()
            redirect_request.set_iline(target_iline)
            self.request.redirect(redirect_request)
        else:
            content = { "title": L10n.get("mp_core_root_container_edit") }

            content['form'] = { "object": form,
                                "url_parameters": { "__request__": True,
                                                    "a": "edit-save",
                                                    "dsd": { "source": source, "target": target }
                                                  },
                                "button_title": "pas_http_core_edit"
                              }

            self.response.init()
            self.response.set_title(content['title'])
            self.response.add_oset_content("core.form", content)
        #
    #

    def execute_edit_save(self):
        """
Action for "edit-save"

:since: v0.2.00
        """

        self.execute_edit(self.request.get_type() == "POST")
    #

    def execute_new(self, is_save_mode = False):
        """
Action for "new"

:since: v0.2.00
        """

        # pylint: disable=star-args

        source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
        target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

        source = source_iline
        if (source_iline == ""): source_iline = "m=mp;a=list_root_containers"

        target = target_iline
        if (target_iline == ""): target_iline = "m=mp;a=list_root_containers;dsd=mcid+__id_d__"

        L10n.init("pas_http_core_form")
        L10n.init("mp_core")

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        user_profile = (None if (session is None) else session.get_user_profile())

        if (user_profile is None
            or (not user_profile.is_type("ad"))
           ): raise TranslatableError("core_access_denied", 403)

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        Link.set_store("servicemenu",
                       Link.TYPE_RELATIVE_URL,
                       L10n.get("core_back"),
                       { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
                       icon = "mini-default-back",
                       priority = 7
                      )

        if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

        form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

        form = FormProcessor(form_id)
        form.set_context({ "form": "new" })

        if (is_save_mode): form.set_input_available()

        field = TextField("mtitle")
        field.set_title(L10n.get("mp_core_container_title"))
        field.set_required()
        field.set_limits(int(Settings.get("mp_core_container_title_min", 3)))
        form.add(field)

        field = TextField("mresource_filepath")
        field.set_title(L10n.get("mp_core_container_resource_local_pathname"))
        field.set_placeholder(L10n.get("pas_http_core_form_case_sensitive_placeholder"))
        field.set_required()
        field.set_size(TextField.SIZE_LARGE)

        field.set_validators([ self._check_container_local_pathname_exists,
                               self._check_container_local_pathname_unique
                             ])


        form.add(field)

        resource_type_choices = [ { "title": L10n.get("mp_core_container_resource_type_audio"), "value": "audio" },
                                  { "title": L10n.get("mp_core_container_resource_type_image"), "value": "image" },
                                  { "title": L10n.get("mp_core_container_resource_type_video"), "value": "video" }
                                ]

        field = SelectField("mresource_type")
        field.set_title(L10n.get("mp_core_container_resource_type"))
        field.set_choices(resource_type_choices)
        field.set_required()
        form.add(field)

        if (is_save_mode and form.check()):
            protocol = "file:///"

            mp_entry_title = InputFilter.filter_control_chars(form.get_value("mtitle"))

            resource_filepath = path.abspath(InputFilter.filter_control_chars(form.get_value("mresource_filepath")))
            resource_url = "{0}{1}".format(protocol, quote(resource_filepath))

            mp_entry = MpEntry.load_encapsulating_entry(resource_url)
            if (mp_entry is None): raise TranslatableException("core_unknown_error")

            mp_entry_resource_type = InputFilter.filter_control_chars(form.get_value("mresource_type"))
            mp_entry_mimetype = "text/directory"

            if (mp_entry_resource_type == "audio"): mp_entry_mimetype = "text/x-directory-upnp-audio"
            elif (mp_entry_resource_type == "image"): mp_entry_mimetype = "text/x-directory-upnp-image"
            elif (mp_entry_resource_type == "video"): mp_entry_mimetype = "text/x-directory-upnp-video"

            mp_entry_data = { "title": mp_entry_title,
                              "cds_type": MpEntry.DB_CDS_TYPE_ROOT,
                              "mimeclass": "directory",
                              "mimetype": mp_entry_mimetype,
                              "resource_title": mp_entry_title
                            }

            mp_entry.set_data_attributes(**mp_entry_data)
            mp_entry.set_as_main_entry()
            mp_entry.save()

            cid_d = mp_entry.get_id()
            resource_id = mp_entry.get_resource_id()

            database_tasks = DatabaseTasks.get_instance()
            database_tasks.add("dNG.pas.upnp.Resource.onAdded.{0}".format(cid_d), "dNG.pas.upnp.Resource.onAdded", 1, resource_id = resource_id)
            database_tasks.add("dNG.pas.upnp.Resource.onRootContainerAdded.{0}".format(cid_d), "dNG.pas.upnp.Resource.onRootContainerAdded", 1, container_id = resource_id)

            target_iline = target_iline.replace("__id_d__", "{0}".format(cid_d))
            target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

            NotificationStore.get_instance().add_completed_info(L10n.get("mp_core_done_root_container_new"))

            Link.clear_store("servicemenu")

            redirect_request = PredefinedHttpRequest()
            redirect_request.set_iline(target_iline)
            self.request.redirect(redirect_request)
        else:
            content = { "title": L10n.get("mp_core_root_container_new") }

            content['form'] = { "object": form,
                                "url_parameters": { "__request__": True,
                                                    "a": "new-save",
                                                    "dsd": { "source": source, "target": target }
                                                  },
                                "button_title": "pas_core_save"
                              }

            self.response.init()
            self.response.set_title(content['title'])
            self.response.add_oset_content("core.form", content)
        #
    #

    def execute_new_save(self):
        """
Action for "new-save"

:since: v0.2.00
        """

        self.execute_new(self.request.get_type() == "POST")
    #
#
