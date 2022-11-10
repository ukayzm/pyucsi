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

"""Parse sections defined by ISO"""


from .section import Section, SectionExt
from .descriptor import DescriptorLoop


TRANSPORT_PAT_PID   = 0x00
TRANSPORT_CAT_PID   = 0x01
TRANSPORT_TSDT_PID  = 0x02


STAG_PROGRAM_ASSOCIATION           = 0x00
STAG_CONDITIONAL_ACCESS            = 0x01
STAG_PROGRAM_MAP                   = 0x02
STAG_TRANSPORT_STREAM_DESCRIPTION  = 0x03
STAG_ISO14496_SCENE_DESCRIPTION    = 0x04
STAG_ISO14496_OBJECT_DESCRIPTION   = 0x05
STAG_METADATA                      = 0x06


class PatProgram:
    "Program in PAT"
    def __init__(self, buf, i):
        self.program_number = (buf[i] << 8) | buf[i+1]
        self.pid = ((buf[i+2] & 0x1f) << 8) | buf[i+3]

    def __str__(self):
        return "    program_number:0x%04x pid:0x%04x" % (
                self.program_number, self.pid)

class PatSection(SectionExt):
    "Program Association Table"
    def __init__(self, buf):
        self.programs = []
        self.transport_stream_id = 0
        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            return
        self.transport_stream_id = self.table_id_ext

    def decode(self):
        buf = self.data
        i = 8
        self.programs = []
        while (i < (self.length - 1)):
            self.programs.append(PatProgram(buf, i))
            i += 4
        return 0

    def __str__(self):
        string = '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    transport_stream_id:0x%04x" % self.transport_stream_id])
        for program in self.programs:
            string = '\n'.join([string, program.__str__()])
        return string


# Known stream types.
ISO11172_2_VIDEO    = 0x01
ISO13818_2_VIDEO    = 0x02
ISO11172_3_AUDIO    = 0x03
ISO13818_3_AUDIO    = 0x04
ISO13818_1_PRIVATE_SECTIONS = 0x05
ISO13818_1_PRIVATE_PES = 0x06
ISO13522_MHEG       = 0x07
ISO13818_1_DSMCC    = 0x08
ITUH222_1           = 0x09
ISO13818_6_A        = 0x0a
ISO13818_6_B        = 0x0b
ISO13818_6_C        = 0x0c
ISO13818_6_D        = 0x0d
ISO13818_1_AUX      = 0x0e
ISO13818_7_AUDIO_ADTS = 0x0f
ISO14496_2_VISUAL   = 0x10
ISO14496_3_AUDIO_LATM = 0x11
ISO14496_1_PES      = 0x12
ISO14496_1_SECTIONS = 0x13
ISO14496_6_SYNCDOWNLOAD = 0x14
METADATA_PES        = 0x15
METADATA_SECTIONS   = 0x16
METADATA_DSMCC_DATA = 0x17
METADATA_DSMCC_OBJECT = 0x18
METADATA_SYNCDOWNLOAD = 0x19
ISO13818_11_IPMP    = 0x1a
ISO14496_10_H264    = 0x1b


class PmtStream:
    "Stream in PMT"
    def __init__(self, buf, i):
        self.stream_type = buf[i]
        self.pid = ((buf[i+1] & 0x1f) << 8) | buf[i+2]
        self.es_info_length = ((buf[i+3] & 0xf) << 8) | buf[i+4]
        descriptor_buf = buf[i+5:i+self.es_info_length + 5]
        self.descriptors = DescriptorLoop(descriptor_buf)

    def __str__(self):
        return "stream_type:0x%02x pid:0x%04x" % (
                self.stream_type, self.pid)

class PmtSection(SectionExt):
    "Program Map Table"
    def __init__(self, buf):
        self.program_number = 0
        self.pcr_pid = 0
        self.program_info_length = 0
        self.descriptors = []
        self.streams = []
        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            return
        self.program_number = self.table_id_ext

    def decode(self):
        buf = self.data
        self.pcr_pid = ((buf[8] & 0x1f) << 8) | buf[9]
        self.program_info_length = ((buf[10] & 0xf) << 8) | buf[11]
        i = 12 + self.program_info_length
        descriptor_buf = buf[12:i]
        self.descriptors = DescriptorLoop(descriptor_buf)
        self.streams = []
        while (i < (self.length - 1)):
            stream = PmtStream(buf, i)
            self.streams.append(stream)
            i += stream.es_info_length + 5
        return 0

    def __str__(self):
        return '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    program_number:0x%04x pcr_pid:0x%02x" % (
                self.program_number, self.pcr_pid)])


class PsiState:
    """Class for keeping track of sections of a PSI table."""
    def __init__(self):
        self._next_section_number = 0
        self._complete = False
        self._new_table = 0
        self._version_number = 0xff

    def reset(self):
        """Reset a psi_state state."""
        self._version_number = 0xff

    def useful(self, section):
        """Check if a supplied section_ext is something we want to process."""
        if (self._version_number == section.version_number and
                self._complete is True):
            return False
        if (self._version_number != section.version_number):
            self._complete = False
            if (section.section_number != 0):
                return False
            self._next_section_number = 0
            self._version_number = section.version_number
            self._new_table = 1
        elif (section.section_number == self._next_section_number):
            self._new_table = 0
        else:
            return False

        self._next_section_number += 1
        if (section.last_section_number < self._next_section_number):
            self._complete = True

        return True

    def complete(self):
        return self._complete

