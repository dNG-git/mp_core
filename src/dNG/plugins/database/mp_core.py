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

# pylint: disable=unused-argument

from dNG.database.schema import Schema
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook

def after_apply_schema(params, last_return = None):
#
	"""
Called for "dNG.pas.Database.applySchema.after"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
	"""

	resource_class = NamedLoader.get_class("dNG.database.instances.MpUpnpResource")
	Schema.apply_version(resource_class)

	audio_class = NamedLoader.get_class("dNG.database.instances.MpUpnpAudioResource")
	Schema.apply_version(audio_class)

	image_class = NamedLoader.get_class("dNG.database.instances.MpUpnpImageResource")
	Schema.apply_version(image_class)

	video_class = NamedLoader.get_class("dNG.database.instances.MpUpnpVideoResource")
	Schema.apply_version(video_class)

	return last_return
#

def before_apply_schema(params, last_return = None):
#
	"""
Called for "dNG.pas.Database.applySchema.before"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
	"""

	audio_class = NamedLoader.get_class("dNG.database.instances.MpUpnpAudioResource")
	if (audio_class is not None): audio_class.before_apply_schema()

	image_class = NamedLoader.get_class("dNG.database.instances.MpUpnpImageResource")
	if (image_class is not None): image_class.before_apply_schema()

	video_class = NamedLoader.get_class("dNG.database.instances.MpUpnpVideoResource")
	if (video_class is not None): video_class.before_apply_schema()

	return last_return
#

def load_all(params, last_return = None):
#
	"""
Load and register all SQLAlchemy objects to generate database tables.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
	"""

	NamedLoader.get_class("dNG.database.instances.MpUpnpAudioResource")
	NamedLoader.get_class("dNG.database.instances.MpUpnpImageResource")
	NamedLoader.get_class("dNG.database.instances.MpUpnpResource")
	NamedLoader.get_class("dNG.database.instances.MpUpnpVideoResource")

	return last_return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.2.00
	"""

	Hook.register("dNG.pas.Database.applySchema.after", after_apply_schema)
	Hook.register("dNG.pas.Database.applySchema.before", before_apply_schema)
	Hook.register("dNG.pas.Database.loadAll", load_all)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.2.00
	"""

	Hook.unregister("dNG.pas.Database.applySchema.after", after_apply_schema)
	Hook.unregister("dNG.pas.Database.applySchema.before", before_apply_schema)
	Hook.unregister("dNG.pas.Database.loadAll", load_all)
#

##j## EOF