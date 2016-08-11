-- MediaProvider
-- A device centric multimedia solution
--
-- (C) direct Netware Group - All rights reserved
-- https://www.direct-netware.de/redirect?mp;core
--
-- The following license agreement remains valid unless any additions or
-- changes are being made by direct Netware Group in a written form.
--
-- This program is free software; you can redistribute it and/or modify it
-- under the terms of the GNU General Public License as published by the
-- Free Software Foundation; either version 2 of the License, or (at your
-- option) any later version.
--
-- This program is distributed in the hope that it will be useful, but WITHOUT
-- ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
-- FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
-- more details.
--
-- You should have received a copy of the GNU General Public License along with
-- this program; if not, write to the Free Software Foundation, Inc.,
-- 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
--
-- https://www.direct-netware.de/redirect?licenses;gpl

-- Create index for resource attribute

CREATE INDEX ix___db_prefix___mp_upnp_resource_cds_type ON __db_prefix___mp_upnp_resource USING btree (cds_type);
CREATE INDEX ix___db_prefix___mp_upnp_resource_resource ON __db_prefix___mp_upnp_resource USING btree (resource);