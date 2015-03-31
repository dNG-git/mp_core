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

from dNG.pas.data.upnp.resources.mp_entry import MpEntry
from dNG.pas.database.condition_definition import ConditionDefinition
from dNG.pas.database.connection import Connection
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.value_exception import ValueException
from .abstract_segment import AbstractSegment
from .criteria_definition import CriteriaDefinition

class CommonMpEntrySegment(AbstractSegment):
#
	"""
"CommonMpEntrySegment" provides UPnP searches for "MpEntry" instances.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    mp
:subpackage: core
:since:      v0.1.02
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(SearchResources)

:since: v0.1.02
		"""

		AbstractSegment.__init__(self)

		self.condition_definition = None
		"""
Database query condition definition
		"""
		self.pre_condition_failed = False
		"""
True if a pre-condition fails
		"""
	#

	def _ensure_condition_definition(self):
	#
		"""
Checks and sets the database query condition definition based on the defined
UPnP criteria definition specified.

:since: v0.1.02
		"""

		if ((not self.pre_condition_failed) and self.condition_definition is None):
		#
			self.condition_definition = self._rewrite_criteria_definition_walker(self.criteria_definition)
		#
	#

	def get_count(self):
	#
		"""
Returns the total number of matches in this UPnP search segment.

:return: (int) Number of matches
:since:  v0.1.02
		"""

		self._ensure_condition_definition()

		return (0
		        if (self.pre_condition_failed) else
		        MpEntry.get_entries_count_with_condition(self.condition_definition)
		       )
	#

	def get_list(self):
	#
		"""
Returns the list of UPnP resource search segment results as defined by
"offset" and "limit".

:return: (list) List of search segment results
:since:  v0.1.02
		"""

		self._ensure_condition_definition()

		kwargs = { }
		#if (sort_definition)

		return ([ ]
		        if (self.pre_condition_failed) else
		        list(MpEntry.load_entries_list_with_condition(self.condition_definition, self.offset, self.limit, **kwargs))
		       )
	#

	def _get_property_attribute_name(self, _property):
	#
		"""
Returns the database attribute name for the given lower-case property.

:param property: Lower-case property

:return: (str) Database attribute name
:since:  v0.1.02
		"""

		_return = None

		if (_property == "@id"): _return = "id"
		elif (_property == "@refid"): _return = "resource"
		elif (_property in ( "dc:date", "upnp:recordedStartDateTime" )): _return = "time_sortable"
		elif (_property == "dc:description"): _return = "description"
		elif (_property == "dc:title"): _return = "title"
		elif (_property == "res@size"): _return = "size"
		elif (_property == "upnp:class"): _return = "identity"

		if (_return is None): raise ValueException("UPnP property '{0}' not defined".format(_property))

		return _return
	#

	def _rewrite_criteria_definition_walker(self, criteria_definition):
	#
		"""
Adds the specified criteria to the given database query condition
definition.

:param criteria_definition: Criteria definition instance

:return: (object) Database condition definition instance
:since:  v0.1.02
		"""

		condition_concatenation = (ConditionDefinition.AND
		                           if (criteria_definition.get_concatenation() == CriteriaDefinition.AND) else
		                           ConditionDefinition.OR
		                          )

		_return = ConditionDefinition(condition_concatenation)

		for criteria in criteria_definition.get_criteria():
		#
			condition_method = None

			criteria_property = criteria.get("property")
			criteria_type = criteria['type']
			criteria_value = None

			if (criteria_property == "@id"
			    and "value" in criteria
			    and "://" in criteria['value']
			   ): criteria_value = criteria['value'].split("://", 1)[1]

			if (criteria_property == "@refid" and
			    criteria_type in ( CriteriaDefinition.TYPE_DEFINED_MATCH, CriteriaDefinition.TYPE_NOT_DEFINED_MATCH)
			   ):
			#
				value_list = Hook.call("dNG.mp.upnp.MpResource.getReferenceDbIdentities")

				if (type(value_list) is list
				    and len(value_list) > 0
				   ):
				#
					if (criteria_type == CriteriaDefinition.TYPE_DEFINED_MATCH): _return.add_in_list_match_condition("identity", value_list)
					else: _return.add_not_in_list_match_condition("identity", value_list)
				#
				elif (criteria_type == CriteriaDefinition.TYPE_DEFINED_MATCH):
				#
					self.pre_condition_failed = True
					break
				#
			#
			elif (criteria_type == CriteriaDefinition.TYPE_SUB_CRITERIA):
			#
				condition_definition = self._rewrite_criteria_definition_walker(criteria['criteria_definition'])

				if (self.pre_condition_failed): break
				else: _return.add_sub_condition(condition_definition)
			#
			elif (criteria_type == CriteriaDefinition.TYPE_CASE_INSENSITIVE_MATCH):
			#
				condition_method = _return.add_case_insensitive_match_condition
				criteria_value = "*{0}*".format(criteria['value'])
			#
			elif (criteria_type == CriteriaDefinition.TYPE_CASE_INSENSITIVE_NO_MATCH):
			#
				condition_method = _return.add_case_insensitive_no_match_condition
				criteria_value = "*{0}*".format(criteria['value'])
			#
			elif (criteria_type == CriteriaDefinition.TYPE_DEFINED_MATCH):
			#
				attribute = self._get_property_attribute_name(criteria['property'])
				_return.add_exact_no_match_condition(attribute, None)
			#
			elif (criteria_type == CriteriaDefinition.TYPE_DERIVED_CRITERIA):
			#
				if (criteria_property != "upnp:class"): raise ValueException("UPnP 'derivedFrom' criteria is only supported for the 'upnp:class' property")

				criteria_value = criteria['value'].lower().strip()

				old_conditions_count = _return.get_conditions_count()

				Hook.call("dNG.mp.upnp.MpResource.applyValueDerivedDbCondition",
				          condition_definition = _return,
				          value = criteria_value
				         )

				if (old_conditions_count == _return.get_conditions_count()):
				#
					self.pre_condition_failed = True
					break
				#
			#
			elif (criteria_type == CriteriaDefinition.TYPE_EXACT_MATCH):
			#
				condition_method = _return.add_exact_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_EXACT_NO_MATCH):
			#
				condition_method = _return.add_exact_no_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_GREATER_THAN_MATCH):
			#
				condition_method = _return.add_greater_than_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_GREATER_THAN_OR_EQUAL_MATCH):
			#
				condition_method = _return.add_greater_than_or_equal_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_LESS_THAN_MATCH):
			#
				condition_method = _return.add_less_than_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_LESS_THAN_OR_EQUAL_MATCH):
			#
				condition_method = _return.add_less_than_or_equal_match_condition
			#
			elif (criteria_type == CriteriaDefinition.TYPE_NOT_DEFINED_MATCH):
			#
				attribute = self._get_property_attribute_name(criteria_property)
				_return.add_exact_match_condition(attribute, None)
			#

			if (condition_method is not None):
			#
				if (criteria_value is None): criteria_value = criteria['value']

				attribute = self._get_property_attribute_name(criteria_property)

				value = (Hook.call("dNG.mp.upnp.MpResource.getDbIdentity", value = criteria_value)
				         if (criteria_property == "upnp:class") else
				         self._rewrite_value(criteria_value)
				        )

				condition_method(attribute, value)
			#
		#

		if (self.pre_condition_failed): _return = None

		return _return
	#

	def _rewrite_value(self, value):
	#
		"""
Rewrites the value to be used in a database query.

:param value: Value to be rewritten

:return: (str) Rewritten value
:since:  v0.1.02
		"""

		_return = value.strip()
		_return = Connection.get_instance().escape_like_condition(_return)
		_return = _return.replace("*", "%")

		return _return
	#

	def set_criteria_definition(self, criteria_definition):
	#
		"""
Sets the UPnP search criteria definition used.

:param criteria_definition: Criteria definition instance

:since: v0.1.02
		"""

		AbstractSegment.set_criteria_definition(self, criteria_definition)
		self.condition_definition = None
	#

	@staticmethod
	def apply_value_derived_db_condition(params, last_return = None):
	#
		"""
Called for "dNG.mp.upnp.MpResource.applyValueDerivedDbCondition"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.02
		"""

		if ("condition_definition" not in params
		    or "value" not in params
		   ): raise ValueException("Missing required arguments")

		condition_definition = params['condition_definition']
		value = "{0}.".format(params['value'])

		is_generic_container = "object.container.".startswith(value)
		is_audio_container = "object.container.genre.musicGenre.".startswith(value)
		is_image_container = "object.container.album.photoAlbum.".startswith(value)
		is_video_container = "object.container.genre.movieGenre.".startswith(value)

		if (is_generic_container or is_audio_container or is_image_container or is_video_container):
		#
			and_condition_definition = (condition_definition
			                            if (condition_definition.get_concatenation() == ConditionDefinition.AND) else
			                            ConditionDefinition(ConditionDefinition.AND)
			                           )

			and_condition_definition.add_exact_match_condition("cds_type", MpEntry.DB_CDS_TYPE_CONTAINER)
			and_condition_definition.add_exact_match_condition("identity", "MpUpnpResource")

			if (is_audio_container):
			#
				and_condition_definition.add_exact_match_condition("mimetype", "text/x-directory-upnp-audio")
			#
			elif (is_image_container):
			#
				and_condition_definition.add_exact_match_condition("mimetype", "text/x-directory-upnp-image")
			#
			elif (is_video_container):
			#
				and_condition_definition.add_exact_match_condition("mimetype", "text/x-directory-upnp-video")
			#

			if (condition_definition.get_concatenation() == ConditionDefinition.OR):
			#
				condition_definition.add_sub_condition(and_condition_definition)
			#
		#

		if ("object.item.audioitem.".startswith(value)): condition_definition.add_exact_match_condition("identity", "MpUpnpAudioResource")
		if ("object.item.imageitem.".startswith(value)): condition_definition.add_exact_match_condition("identity", "MpUpnpImageResource")
		if ("object.item.videoitem.".startswith(value)): condition_definition.add_exact_match_condition("identity", "MpUpnpVideoResource")

		return last_return
	#

	@classmethod
	def is_search_criteria_definition_supported(cls, criteria_definition):
	#
		"""
Checks if only supported MpEntry instance attributes are queried.

:param cls: Python class
:param criteria_definition: Criteria definition instance

:return: (bool) True if only supported MpEntry instance attributes are
         queried
:since:  v0.1.02
		"""

		return cls._is_search_criteria_definition_supported_walker(criteria_definition)
	#

	@classmethod
	def _is_search_criteria_definition_supported_walker(cls, criteria_definition):
	#
		"""
Checks recursively if only supported MpEntry instance attributes are
queried.

:param cls: Python class
:param criteria_definition: Criteria definition instance

:return: (bool) True if only supported MpEntry instance attributes are
         queried
:since:  v0.1.02
		"""

		_return = True

		for criteria in criteria_definition.get_criteria():
		#
			_return = (cls._is_search_criteria_definition_supported_walker(criteria['criteria_definition'])
			           if (criteria['type'] == CriteriaDefinition.TYPE_SUB_CRITERIA) else
			           (criteria['property'] in ( "@id",
			                                      "@refid",
			                                      "dc:date",
			                                      "dc:title",
			                                      "res@size",
			                                      "upnp:class",
			                                      "upnp:recordedStartDateTime"
			                                    )
			           )
			          )

			if (not _return): break
		#

		return _return
	#
#

##j## EOF