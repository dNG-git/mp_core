# -*- coding: utf-8 -*-
##j## BOF

"""
de.vplace.plugins.pas_core

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    vp
@subpackage core
@license    http://www.direct-netware.de/redirect.php?licenses;gpl
            GNU General Public License 2
"""
"""n// NOTE
----------------------------------------------------------------------------
v'place media center
A device oriented media center solution
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?vp

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
http://www.direct-netware.de/redirect.php?licenses;gpl
----------------------------------------------------------------------------
#echo(pasVpCoreVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from binascii import hexlify
from os import path
from threading import Event
import os

from de.direct_netware.classes.pas_globals import direct_globals
from de.direct_netware.classes.pas_logger import direct_logger
from de.direct_netware.classes.pas_pluginmanager import direct_plugin_hooks
from de.direct_netware.thread.pas_http_tasks import direct_http_tasks

from de.vplace.classes.pas_http_chunked_streamer import direct_http_chunked_streamer
from de.vplace.classes.pas_imaging import direct_imaging

def direct_psd_plugins_image_resize (params = None,last_return = None):
#
	"""
Resize a image to the given size.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (bool) True on success
@since  v0.1.00
	"""

	direct_logger.debug ("vpbgs received call: de.vplace.plugins.mc.imageResize")

	if (last_return == None): f_return = { "error":"","result":"" }
	else: f_return = last_return

	if ((len (params['params']) > 4) and (params['params'][0] != False)):
	#
		try:
		#
			f_source_file = path.basename (params['params'][0])
			f_target_file = path.splitext (f_source_file)[0]
			if (path.splitext(f_target_file)[1] == ""): f_target_file = f_source_file

			f_target_file = path.normpath ("{0}/vp_mc_{1}.{2}x{3}.{4}".format (params['params'][3],params['params'][4],params['params'][1],params['params'][2],f_target_file))

			if (path.isfile (f_target_file)): open(f_target_file,"a").close ()
			else:
			#
				f_image = direct_imaging (params['params'][0])
				f_image.open ()
				f_image.resize (int (params['params'][1]),(int (params['params'][2])))
				f_image.save (f_target_file,quality = 95)
			#

			f_return['result'] = f_target_file
		#
		except Exception as f_handled_exception:
		#
			direct_logger.critical (f_handled_exception)
			f_return['error'] = "{0}".format (f_handled_exception)
		#
	#

	return f_return
#

def direct_psd_plugins_services_get (params = None,last_return = None):
#
	"""
Get a list of service entries provided by the plugins.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (bool) True on success
@since  v0.1.00
	"""

	direct_logger.debug ("vpbgs received call: de.vplace.plugins.mc.services.get")

	if (last_return == None): f_return = [ ]
	else: f_return = last_return

	if (type (direct_globals['settings']['pas_vp_mc_services']) == list): f_mc_services = direct_globals['settings']['pas_vp_mc_services']
	else: f_mc_services = [ direct_globals['settings']['pas_vp_mc_services'] ]

	for f_mc_service in f_mc_services:
	#
		f_services_list = direct_plugin_hooks.call ("de.vplace.plugins.{0}.getServices".format (f_mc_service))
		if (type (f_services_list) == list): f_return += f_services_list
	#

	f_return.append ({ "type": "menurclist","title": "vp_mc_settings","service": "mc.settings","bg_image": "core_settings.jpg" })
	f_return.append ({ "type": "osdrclist","title": "vp_mc_status","service": "mc.status","bg_image": "core_status.jpg" })

	return f_return
#

def direct_psd_plugins_settings_get_list (params = None,last_return = None):
#
	"""
Get a list of setting entries for all plugins.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (bool) True on success
@since  v0.1.00
	"""

	direct_logger.debug ("vpbgs received call: de.vplace.plugins.mc.settings.getList")

	if (last_return == None):
	#
		f_return = [
			{ "type": "osdlocalurl","title": "vp_mc_settings_profile_set","pageurl": "m=vp;s=settings;a=profile_set","include_source": True },
			{ "type": "osdlocalurl","title": "vp_mc_settings_profile_delete","pageurl": "m=vp;s=settings;a=profile_delete","include_source": True }
		]
	#
	else: f_return = last_return

	if (type (direct_globals['settings']['pas_vp_mc_services']) == list): f_mc_services = direct_globals['settings']['pas_vp_mc_services']
	else: f_mc_services = [ direct_globals['settings']['pas_vp_mc_services'] ]

	for f_mc_service in f_mc_services:
	#
		f_status_dict = direct_plugin_hooks.call ("de.vplace.plugins.{0}.getSettings".format (f_mc_service))
		if (type (f_status_dict) == dict): f_return.append (f_status_dict)
	#

	return f_return
#

def direct_psd_plugins_status_get_list (params = None,last_return = None):
#
	"""
Get the status list for all plugins.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (bool) True on success
@since  v0.1.00
	"""

	direct_logger.debug ("vpbgs received call: de.vplace.plugins.mc.status.getList")

	if (last_return == None): f_return = [ ]
	else: f_return = last_return

	if (type (direct_globals['settings']['pas_vp_mc_services']) == list): f_mc_services = direct_globals['settings']['pas_vp_mc_services']
	else: f_mc_services = [ direct_globals['settings']['pas_vp_mc_services'] ]

	for f_mc_service in f_mc_services:
	#
		f_status_dict = direct_plugin_hooks.call ("de.vplace.plugins.{0}.getStatus".format (f_mc_service))
		if (type (f_status_dict) == dict): f_return.append (f_status_dict)
	#

	return f_return
#

def direct_psd_plugins_stream (params = None,last_return = None):
#
	"""
Prepare the stream of an file with HTTP tasks.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (bool) True on success
@since  v0.1.00
	"""

	direct_logger.debug ("vpbgs received call: de.vplace.plugins.mc.getStreamID")

	if (last_return == None): f_return = False
	else: f_return = last_return

	if (len (params['params']) > 3):
	#
		f_params = { "path": params['params'][2] }
		f_params['type'] = params['params'][3]
		if (len (params['params']) > 4): f_params['duration'] = params['params'][4]

		f_ready_event = Event ()
		f_return = hexlify (os.urandom (16))
		f_thread = direct_http_tasks.thread ([ f_return,params['params'][1],direct_psd_plugins_stream_call,f_params ],server_port = params['params'][0],ready_event = f_ready_event)

		if (f_thread != None):
		#
			f_thread.start ()
			f_ready_event.wait ();
		#
	#

	return f_return
#

def direct_psd_plugins_stream_call (server,client,params):
#
	"""
Start a new "direct_downloader_throttled" instance for HTTP tasks.

@param  http_tasks Active HTTP tasks instance
@param  params Parameters used for "direct_downloader_throttled"
@return (direct_downloader_throttled) Pending instance
@since  v0.1.00
	"""

	return direct_http_chunked_streamer (server,client,params)
#

def plugin_deregistration ():
#
	"""
Deregister plugin hooks.

@since v0.1.00
	"""

	direct_plugin_hooks.unregister ("de.vplace.plugins.mc.imageResize",direct_psd_plugins_image_resize)
	direct_plugin_hooks.unregister ("de.vplace.plugins.mc.services.get",direct_psd_plugins_services_get)
	direct_plugin_hooks.unregister ("de.vplace.plugins.mc.settings.getList",direct_psd_plugins_settings_get_list)
	direct_plugin_hooks.unregister ("de.vplace.plugins.mc.status.getList",direct_psd_plugins_status_get_list)
	direct_plugin_hooks.unregister ("de.vplace.plugins.mc.stream",direct_psd_plugins_stream)
#

def plugin_registration ():
#
	"""
Register plugin hooks.

@since v0.1.00
	"""

	direct_plugin_hooks.register ("de.vplace.plugins.mc.imageResize",direct_psd_plugins_image_resize)
	direct_plugin_hooks.register ("de.vplace.plugins.mc.services.get",direct_psd_plugins_services_get)
	direct_plugin_hooks.register ("de.vplace.plugins.mc.settings.getList",direct_psd_plugins_settings_get_list)
	direct_plugin_hooks.register ("de.vplace.plugins.mc.status.getList",direct_psd_plugins_status_get_list)
	direct_plugin_hooks.register ("de.vplace.plugins.mc.stream",direct_psd_plugins_stream)
#

##j## EOF