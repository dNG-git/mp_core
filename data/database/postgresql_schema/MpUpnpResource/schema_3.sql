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

-- Reuse FileCenterEntry for MpUpnpResource

UPDATE __db_prefix___mp_upnp_resource SET size = 0 WHERE size is null;

INSERT INTO __db_prefix___file_center_entry (id, mimeclass, mimetype, vfs_url, size, vfs_type, role_id, guest_permission, user_permission) (
 SELECT id, mimeclass, mimetype, resource, size, 1, 'upnp_root_container', 'r', 'r' FROM __db_prefix___mp_upnp_resource WHERE cds_type = 1
);

INSERT INTO __db_prefix___file_center_entry (id, mimeclass, mimetype, vfs_url, size, vfs_type, guest_permission, user_permission) (
 SELECT id, mimeclass, mimetype, resource, size, 1, 'r', 'r' FROM __db_prefix___mp_upnp_resource WHERE cds_type = 2
);

INSERT INTO __db_prefix___file_center_entry (id, mimeclass, mimetype, vfs_url, size, vfs_type, guest_permission, user_permission) (
 SELECT id, mimeclass, mimetype, resource, size, 2, 'r', 'r' FROM __db_prefix___mp_upnp_resource WHERE cds_type = 3
);

ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN cds_type;
ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN mimeclass;
ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN mimetype;
ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN resource_type;
ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN resource;
ALTER TABLE __db_prefix___mp_upnp_resource DROP COLUMN size;