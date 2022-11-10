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

"""Generic Descriptor"""

class Descriptor:
    """Generic descriptor header."""
    def __init__(self, buf, i = 0):
        self.tag = -1
        buf_len = len(buf)
        if (buf_len < i + 2):
            return
        self.length = buf[i+1]
        if (buf_len < i + self.length + 2):
            return
        self.tag = buf[i]
        self.data = buf[i:i+self.length+2]

    def __str__(self):
        if (self.tag == -1):
            return "invalid descriptor"
        return "tag:0x%02x length:%d" % (self.tag, self.length)

class DescriptorLoop:
    """Iterator of descriptor loop."""

    def __init__(self, buf, offset = 0, length = 0):
        self.descriptors = []
        if (length == 0):
            length = len(buf)
        elif (len(buf) < offset + length):
            return
        i = 0
        while (i < length):
            dsc = Descriptor(buf, i + offset)
            if (dsc.tag == -1):
                return
            if (i + dsc.length + 2 > length + offset):
                return
            self.descriptors.append(dsc)
            i += dsc.length + 2
        self.iter_offset = 0

    def __iter__(self):
        self.iter_offset = 0
        return self

    def __next__(self):
        self.iter_offset += 1
        if (len(self.descriptors) < self.iter_offset):
            raise StopIteration
        return self.descriptors[self.iter_offset - 1]

