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

from os import path

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
#
	from urllib import quote, unquote
	from urlparse import urlsplit
#

from dNG.pas.data.cache.file import File as CacheFile
from dNG.pas.data.text.link import Link
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.runtime.io_exception import IOException
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from .abstract_dlna_http_stream import AbstractDlnaHttpStream

class AbstractTransformedImageStream(AbstractDlnaHttpStream):
#
	"""
"AbstractTransformedImageStream" represents an UPnP thumbnail object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	SCHEME = "upnp-transformed-image"
	"""
URL scheme for transformed images
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractTransformedImageStream)

:since: v0.1.02
		"""

		AbstractDlnaHttpStream.__init__(self)

		self.transformed_image_height = None
		"""
Height of the transformed image
		"""
		self.transformed_image_width = None
		"""
Width of the transformed image
		"""
		self.transformed_source_path = None
		"""
Source image file path and name for the transformed image
		"""
		self.transformed_source_resource_id = None
		"""
UPnP resource ID of the item of the transformed image
		"""
	#

	def get_dlna_org_pn(self):
	#
		"""
Returns the DLNA "ORG_PN" value of the transformed image.

:return: (str) DLNA "ORG_PN" value
:since:  v0.1.02
		"""

		raise NotImplementedException()
	#

	def get_transformed_image_settings(self):
	#
		"""
Returns the transformation settings.

:return: (dict) Transformation settings
:since:  v0.1.02
		"""

		return { "mimetype": self.get_mimetype(),
		         "width": self.transformed_image_width,
		         "height": self.transformed_image_height
		       }
	#

	def get_transformed_image_url(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.02
		"""

		if (self.transformed_source_resource_id is None): raise IOException("Source resource ID of transformed image URL is invalid")

		transformation_settings = self.get_transformed_image_settings()

		link_parameters = { "__virtual__": "/upnp/image",
		                    "a": "transformed_resource",
		                    "dsd": { "urid": self.transformed_source_resource_id,
		                             "umimetype": transformation_settings['mimetype'],
		                             "uwidth": transformation_settings['width'],
		                             "uheight": transformation_settings['height'],
		                             "utype_id": self.__class__.__name__
		                           }
		                  }

		return Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, link_parameters)
	#

	def _init_cds_resource(self, deleted = False):
	#
		"""
Initialize a UPnP CDS resource instance.

:param _id: UPnP CDS ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		_return = (self.resource_id is not None)

		if (_return):
		#
			url_elements = urlsplit(self.resource_id)

			_return = (self._init_transformed_image_resource(deleted)
			           if (url_elements.scheme == self.__class__.SCHEME) else
			           AbstractDlnaHttpStream._init_cds_resource(self, deleted)
			          )
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.02
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		if (self.transformed_source_resource_id is None): _return = AbstractDlnaHttpStream._init_content(self)
		else:
		#
			self.content = [ self.get_transformed_image_url() ]
			_return = True
		#

		return _return
	#

	def _init_dlna_content_features(self):
	#
		"""
Initializes the UPnP DLNA content features variable.

:since: v0.1.02
		"""

		dlna_content_features = "DLNA.ORG_OP={0:0>2x};DLNA.ORG_CI={1:d};DLNA.ORG_FLAGS={2:0>8x}000000000000000000000000"

		dlna_converted_flag = (0 if (self.transformed_source_resource_id is None) else 1)

		dlna_content_features = dlna_content_features.format(AbstractDlnaHttpStream.DLNA_SEEK_BYTES,
		                                                     dlna_converted_flag,
		                                                     (AbstractDlnaHttpStream.DLNA_0150
		                                                      | AbstractDlnaHttpStream.DLNA_HTTP_STALLING
		                                                      | AbstractDlnaHttpStream.DLNA_BACKGROUND_TRANSFER
		                                                      | AbstractDlnaHttpStream.DLNA_INTERACTIVE_TRANSFER
		                                                     )
		                                                    )

		if (self.transformed_source_resource_id is not None):
		#
			dlna_content_features = "DLNA.ORG_PN={0};{1}".format(self.get_dlna_org_pn(),
			                                                     dlna_content_features
			                                                    )
		#

		self.dlna_content_features = dlna_content_features
	#

	def _init_transformed_image_resource(self, deleted = False):
	#
		"""
Initialize a UPnP CDS resource instance.

:param _id: UPnP CDS ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		_return = False

		if (self.transformed_source_path is not None):
		#
			source_resource = None
			source_resource_id = None
			url_elements = urlsplit(self.resource_id)

			if (self.transformed_source_resource_id is None):
			#
				if (url_elements.scheme == "upnp-transformed-image"):
				#
					source_resource_id = self.get_parent_resource_id()
					if (source_resource_id is None): source_resource_id = unquote(url_elements.path[1:])
				#

				source_resource = (None
				                   if (source_resource_id is None) else
				                   Resource.load_cds_id(source_resource_id, self.client_user_agent, deleted = deleted)
				                  )

				if (source_resource is None): self.name = path.split(self.transformed_source_path)[1]
				else:
				#
					source_resource = Resource.load_cds_id(source_resource_id, self.client_user_agent, deleted = deleted)

					self.name = source_resource.get_name()
					self.transformed_source_resource_id = source_resource_id
				#
			#

			self.type = AbstractTransformedImageStream.TYPE_CDS_RESOURCE
			transformation_settings = self.get_transformed_image_settings()

			transformation_metadata = { "resolution": "{0:d}x{1:d}".format(transformation_settings['width'],
			                                                               transformation_settings['height']
			                                                              )
			                          }

			try:
			#
				transformed_url = "upnp-transformed-image:///{0}?mimetype={1};width={2:d};height={3:d};depth=24;type_id={4}"

				transformed_url = transformed_url.format(quote(self.transformed_source_path),
				                                         transformation_settings['mimetype'],
				                                         transformation_settings['width'],
				                                         transformation_settings['height'],
				                                         self.__class__.__name__
				                                        )

				transformed_file = CacheFile.load_resource(transformed_url)
				transformation_metadata['size'] = transformed_file.get_size()
			#
			except NothingMatchedException: pass

			self.set_metadata(**transformation_metadata)

			self.set_mimeclass(transformation_settings['mimetype'].split("/", 1)[0])
			self.set_mimetype(transformation_settings['mimetype'])

			_return = True
		#

		return _return
	#

	def set_transformed_source_path(self, _path):
	#
		"""
Sets the source image file path and name for the transformed image.

:param _path: Source image file path and name

:since: v0.1.02
		"""

		self.transformed_source_path = _path
	#

	def set_transformed_image_height(self, height):
	#
		"""
Sets the height of the transformed image.

:param height: Height of the transformed image

:since: v0.1.02
		"""

		self.transformed_image_height = height
	#

	def set_transformed_image_width(self, width):
	#
		"""
Sets the width of the transformed image.

:param width: Width of the transformed image

:since: v0.1.02
		"""

		self.transformed_image_width = width
	#
#

##j## EOF