#
# section and descriptor parser
#
# Copyright (c) 2008 by K. Uhm <kayzm0@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#

class Section:
    """Generic section header."""
    def __init__(self, buf):
        self.table_id = -1
        self.syntax_indicator = 0
        self.private_indicator = 0
        self.length = 0
        self.data = ""
        if (len(buf) < 3):
            return
        self.syntax_indicator = (buf[1] >> 7) & 1
        self.private_indicator = (buf[1] >> 6) & 1
        self.length = ((buf[1] & 0xf) << 8) | buf[2]
        if (self.length + 3 != len(buf)):
            return
        if (self.length < 5):
            return
        self.table_id = buf[0]
        self.data = buf

    def __str__(self):
        if (self.table_id == -1):
            return "invalid section"
        return "table:0x%02x length:%d" % (
                self.table_id, self.length)

    def decode(self):
        pass

class SectionExt(Section):
    """Generic extended section header class."""
    def __init__(self, buf):
        self.table_id_ext = 0
        self.version_number = 0
        self.current_next_indicator = 0
        self.section_number = 0
        self.last_section_number = 0
        self.crc_32 = 0
        Section.__init__(self, buf)
        if (self.table_id == -1):
            return
        if (self.syntax_indicator != 1):
            self.table_id = -1
            return
        self.table_id_ext = (buf[3] << 8) | buf[4]
        self.version_number = (buf[5] >> 1) & 0x1f
        self.current_next_indicator = buf[5] & 1
        self.section_number = buf[6]
        self.last_section_number = buf[7]
        if (self.section_number > self.last_section_number):
            self.table_id = -1
            return
        crc_i = self.length - 1
        self.crc_32 = (buf[crc_i] << 24) | (buf[crc_i + 1] << 16)
        self.crc_32 |= (buf[crc_i + 2] << 8) | buf[crc_i + 3]

    def __str__(self):
        if (self.table_id == -1):
            return "invalid section"
        return '\n'.join((Section.__str__(self),
                "    version:%i(%d), section number (%d/%d)" % (
                        self.version_number, self.current_next_indicator,
                        self.section_number, self.last_section_number)))

