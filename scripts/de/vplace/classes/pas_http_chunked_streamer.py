# -*- coding: utf-8 -*-
##j## BOF

"""
de.vplace.classes.sWG.pas_http_chunked_streamer

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    vp
@subpackage core
@since      v0.1.00
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

from os import path
from threading import RLock
import os,re

from de.direct_netware.classes.pas_file_functions import direct_file_functions
from de.direct_netware.classes.pas_pythonback import direct_bytes,direct_str
from de.direct_netware.classes.sWG.pas_http_throttled import direct_http_throttled

try: from urllib.parse import unquote,unquote_plus
except ImportError: from urllib import unquote,unquote_plus

_direct_http_chunked_streamer_ids = { }
_direct_http_chunked_streamer_synchronized = RLock ()

class direct_http_chunked_streamer (direct_http_throttled):
#
	streamer_id = None

	def __init__ (self,server,client,task):
	#
		global _direct_http_chunked_streamer_ids,_direct_http_chunked_streamer_synchronized

		f_exception = None

		try: direct_http_throttled.__init__ (self,server,client,task)
		except Exception as f_handled_exception: f_exception = f_handled_exception

		_direct_http_chunked_streamer_synchronized.acquire ()
		if (_direct_http_chunked_streamer_ids[task['id']] == self.streamer_id): del (_direct_http_chunked_streamer_ids[task['id']])
		_direct_http_chunked_streamer_synchronized.release ()

		if (f_exception != None): raise f_exception
	#

	def set_task_data (self,server,client,task):
	#
		global _direct_http_chunked_streamer_ids,_direct_http_chunked_streamer_synchronized

		self.buffer_timeout = -1
		self.streamer_id = os.urandom (16)

		_direct_http_chunked_streamer_synchronized.acquire ()
		_direct_http_chunked_streamer_ids[task['id']] = self.streamer_id
		_direct_http_chunked_streamer_synchronized.release ()

		direct_http_throttled.set_task_data (self,server,client,task)
	#

	def output (self):
	#
		f_continue_check = True

		if ("path" in self.task):
		#
			f_path = self.task['path']
			f_path_os = path.normpath (f_path)
		#
		else: f_path = None

		if ((f_path != None) and ("type" in self.task) and (os.access (f_path_os,os.R_OK))):
		#
			f_file_object = direct_file_functions ()
			f_continue_check = f_file_object.open (f_path,True,"rb")
		#
		else: f_continue_check = False

		if (f_continue_check):
		#
			f_bytes_offset = 0
			f_bytes_offset_end = None

			if ("RANGE" in self.client.headers):
			#
				f_result_object = re.compile("^bytes(.*?)=(.*?)-(.*?)$",re.I).match (self.client.headers['RANGE'])

				if (f_result_object != None):
				#
					f_re_no_digit = re.compile ("(\\D+)")

					f_bytes_offset = f_re_no_digit.sub ("",f_result_object.group (2))
					f_bytes_offset_end = f_re_no_digit.sub ("",f_result_object.group (3))

					if (f_bytes_offset == ""): f_bytes_offset = -1
					else: f_bytes_offset = int (f_bytes_offset)

					if (f_bytes_offset_end == ""): f_bytes_offset_end = -1
					else:
					#
						f_bytes_offset_end = int (f_bytes_offset_end)
					#
				#
			#

			f_bytes_unread = path.getsize (f_path_os)
			f_partitial_check = False

			if (f_bytes_offset_end != None):
			#
				if (f_bytes_offset >= 0):
				#
					if (f_bytes_offset_end >= 0):
					#
						if ((f_bytes_offset >= 0) and (f_bytes_offset <= f_bytes_offset_end) and (f_bytes_offset_end < f_bytes_unread)): f_partitial_check = True
					#
					elif ((f_bytes_offset >= 0) and (f_bytes_offset < f_bytes_unread)):
					#
						f_partitial_check = True
						f_bytes_offset_end = (f_bytes_unread - 1)
					#
				#
			#

			if (f_partitial_check):
			#
				f_bytes_original = f_bytes_unread
				f_bytes_unread = (1 + f_bytes_offset_end - f_bytes_offset)

				self.client.send_response (206)
				self.client.send_header ("Content-Length",f_bytes_unread)
				self.client.send_header ("Content-Range","{0}-{1}/{2}".format (f_bytes_offset,f_bytes_offset_end,f_bytes_original))

				if (f_bytes_offset >= 0): f_file_object.seek (f_bytes_offset)
			#
			else:
			#
				self.client.send_response (200)
				if ("duration" in self.task): self.client.send_header ("Content-Duration",self.task['duration'])
				self.client.send_header ("Content-Length",f_bytes_unread)
			#

			self.client.server.get_socket().settimeout (None)
			( f_path,f_file_name ) = path.split (unquote (self.client.get_path ()))

			if (f_partitial_check): self.output_object (f_file_object,self.task['type'],bytes_max = f_bytes_unread,chunked = True)
			else: self.output_object (f_file_object,self.task['type'],chunked = True)
		#
		else: direct_http_throttled.output (self)
	#

	def output_object (self,output_object,content_type = None,header = True,bytes_max = None,chunked = False):
	#
		global _direct_http_chunked_streamer_ids,_direct_http_chunked_streamer_synchronized

		_direct_http_chunked_streamer_synchronized.acquire ()

		if (_direct_http_chunked_streamer_ids[self.task['id']] == self.streamer_id):
		#
			_direct_http_chunked_streamer_synchronized.release ()
			direct_http_throttled.output_object (self,output_object,content_type,header,bytes_max,chunked)
		#
		else:
		#
			_direct_http_chunked_streamer_synchronized.release ()

			try: self.output_bytes (direct_bytes ("0\r\n\r\n"))
			except: pass

			self.result = True
			self.result_event.set ()
		#
	#
#

##j## EOF