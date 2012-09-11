# -*- coding: utf-8 -*-
##j## BOF

"""
de.vplace.classes.pas_imaging

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

try:
#
	from PIL import Image as PILImage
	_direct_image_mode = "PIL"
#
except ImportError:
#
	from ImageMagick import Image as IMImage
	_direct_image_mode = "ImageMagick"
#

class direct_imaging (object):
#
	file_pathname = None
	image = None

	def __init__ (self,file_pathname):
	#
		self.file_pathname = file_pathname
		self.image = None
	#

	def open (self):
	#
		global _direct_image_mode

		if (_direct_image_mode == "PIL"): self.image = PILImage.open (self.file_pathname,"r")
		else: self.image = IMImage (self.file_pathname)
	#

	def pil_resize (self,width,height):
	#
		f_scaled_resize = self.scaled_size (width,height)

		if (f_scaled_resize != False):
		#
			if (f_scaled_resize[0] == True):
			#
				if (self.image.mode != "RGBA"): self.image = self.image.convert ("RGBA")
				self.image = self.image.transform (( f_scaled_resize[1],f_scaled_resize[2] ),PILImage.EXTENT,( f_scaled_resize[4],f_scaled_resize[3],f_scaled_resize[6],f_scaled_resize[5] ),PILImage.BICUBIC)
			#
			else:
			#
				if (self.image.mode != "RGBA"): self.image = self.image.convert ("RGBA")
				self.image = self.image.resize (( f_scaled_resize[1],f_scaled_resize[2] ),PILImage.ANTIALIAS)
			#
		#
	#

	def resize (self,width,height):
	#
		global _direct_image_mode

		if (_direct_image_mode == "PIL"): self.pil_resize (width,height)
		else: self.im_resize (width,height)
	#

	def save (self,f_file_pathname,**kwargs):
	#
		global _direct_image_mode

		if (_direct_image_mode == "PIL"): self.image.save (f_file_pathname,**kwargs)
		else: pass
	#

	def scaled_size (self,width,height):
	#
		( f_image_width,f_image_height ) = self.size ()

		f_scale = 0
		f_scaled_height = 0
		f_scaled_width = 0
		f_resize_check = True

		if (width > 0):
		#
			f_scale = (float (width) / f_image_width)

			if (height > 0):
			#
				f_scaled_height = int (round (f_image_height * f_scale))
				if (f_scaled_height != height): f_resize_check = False
			#
			else: height = int (round (f_image_height * f_scale))
		#
		elif (height > 0):
		#
			f_scale = (float (height) / f_image_height)

			if (width > 0):
			#
				f_scaled_width = int (round (f_image_width * f_scale))
				if (f_scaled_width != width): f_resize_check = False
			#
			else: width = int (round (f_image_width * f_scale))
		#
		else:
		#
			f_resize_check = False

			width = f_image_width
			height = f_image_height
		#

		if (f_resize_check): f_return = ( False,width,height )
		elif (f_scale != 0):
		#
			f_scaled_bottom = f_image_width
			f_scaled_left = 0
			f_scaled_right = f_image_height
			f_scaled_top = 0

			if (f_scaled_width < 1):
			#
				f_scale_height = (float (height) / f_image_height)

				if (f_scale_height > f_scale):
				#
					f_scale = f_scale_height
					f_scaled_height = int (round (f_image_height * f_scale))
				#

				f_scaled_width = int (round (f_image_width * f_scale))
			#
			elif (f_scaled_height < 1):
			#
				f_scale_width = (float (width) / f_image_width)

				if (f_scale_width > f_scale):
				#
					f_scale = f_scale_width
					f_scaled_width = int (round (f_image_width * f_scale))
				#

				f_scaled_height = int (round (f_image_height * f_scale))
			#

			if (f_scaled_width > width):
			#
				f_border = ((f_scaled_width - width) / f_scale)
				f_scaled_top = (f_border / 2)
				f_scaled_bottom -= (f_border - f_scaled_top)
			#

			if (f_scaled_height > height):
			#
				f_border = ((f_scaled_height - height) / f_scale)
				f_scaled_left = (f_border / 2)
				f_scaled_right -= (f_border - f_scaled_left)
			#

			f_return = ( True,width,height,f_scaled_left,f_scaled_top,f_scaled_right,f_scaled_bottom )
		#
		else: f_return = False

		return f_return
	#

	def size (self):
	#
		global _direct_image_mode

		if (_direct_image_mode == "PIL"): f_return = self.image.size
		else:
		#
			f_image_size = self.image.size ()
			f_return = ( f_image_size.width (),(f_image_size.height ()) )
		#

		return f_return
	#
#

##j## EOF