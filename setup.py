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
setup.py
"""

def get_version():
    """
Returns the version currently in development.

:return: (str) Version string
:since:  v0.1.02
    """

    return "v0.2.00"
#

from dNG.distutils.command.build_py import BuildPy
from dNG.distutils.command.install_data import InstallData
from dNG.distutils.command.install_css_data import InstallCssData
from dNG.distutils.temporary_directory import TemporaryDirectory

from distutils.core import setup
from os import path

with TemporaryDirectory(dir = ".") as build_directory:
    css_js_copyright = "mp.core #echo(mpCoreVersion)# - (C) direct Netware Group - All rights reserved"

    parameters = { "install_data_plain_copy_extensions": "crt,jpg,json,png,sql,tsc,xml",
                   "mpCoreVersion": get_version(),
                   "css_header": css_js_copyright, "css_min_filenames": True
                 }

    InstallData.add_install_data_callback(InstallData.plain_copy, [ "data", "lang" ])
    InstallData.add_install_data_callback(InstallCssData.callback, [ "data" ])
    InstallData.set_build_target_path(build_directory)
    InstallData.set_build_target_parameters(parameters)

    _build_path = path.join(build_directory, "src")

    setup(name = "mp_core",
          version = get_version(),
          description = "A device centric multimedia solution",
          long_description = """"mp_core" is the basic platform for the MediaProvider software.""",
          author = "direct Netware Group et al.",
          author_email = "web@direct-netware.de",
          license = "GPLv2+",
          url = "https://www.direct-netware.de/redirect?mp;core",

          platforms = [ "any" ],

          package_dir = { "": _build_path },
          packages = [ "dNG", "mp" ],

          data_files = [ ( "docs", [ "LICENSE", "README" ]) ],

          # Override build_py to first run builder.py over all PAS modules
          cmdclass = { "build_py": BuildPy,
                       "install_data": InstallData
                     }
         )
#
