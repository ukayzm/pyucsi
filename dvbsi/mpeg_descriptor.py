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

"""Descriptors defined by ISO"""

from .descriptor import Descriptor

#
# Enumeration of MPEG descriptor tags.
#
DTAG_VIDEO_STREAM                  = 0x02
DTAG_AUDIO_STREAM                  = 0x03
DTAG_HIERARCHY                     = 0x04
DTAG_REGISTRATION                  = 0x05
DTAG_DATA_STREAM_ALIGNMENT         = 0x06
DTAG_TARGET_BACKGROUND_GRID        = 0x07
DTAG_VIDEO_WINDOW                  = 0x08
DTAG_CA                            = 0x09
DTAG_ISO_639_LANGUAGE              = 0x0a
DTAG_SYSTEM_CLOCK                  = 0x0b
DTAG_MULTIPLEX_BUFFER_UTILIZATION  = 0x0c
DTAG_COPYRIGHT                     = 0x0d
DTAG_MAXIMUM_BITRATE               = 0x0e
DTAG_PRIVATE_DATA_INDICATOR        = 0x0f
DTAG_SMOOTHING_BUFFER              = 0x10
DTAG_STD                           = 0x11
DTAG_IBP                           = 0x12
DTAG_4_VIDEO                       = 0x1b
DTAG_4_AUDIO                       = 0x1c
DTAG_IOD                           = 0x1d
DTAG_SL                            = 0x1e
DTAG_FMC                           = 0x1f
DTAG_EXTERNAL_ES_ID                = 0x20
DTAG_MUXCODE                       = 0x21
DTAG_FMXBUFFER_SIZE                = 0x22
DTAG_MULTIPLEX_BUFFER              = 0x23
DTAG_CONTENT_LABELLING             = 0x24
DTAG_METADATA_POINTER              = 0x25
DTAG_METADATA                      = 0x26
DTAG_METADATA_STD                  = 0x27


class Iso639LanguageCode:
    "language code in iso 639 language descriptor"
    def __init__(self, buf, i):
        language_code = buf[i:i+3].decode()
        if (language_code.isalpha()):
            self.language_code = language_code
        else:
            self.language_code = "???"
        self.audio_type = buf[i+3]

    def __str__(self):
        return "    language_code:%.3s audio_type:0x%02x" % (
                self.language_code, self.audio_type)

class Iso639LanguageDescriptor(Descriptor):
    "iso 639 language descriptor"
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(Iso639LanguageCode(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class CaDescriptor(Descriptor):
    "CA descriptor"
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.ca_system_id = (buf[i+2] << 8) | buf[i+3]
        self.ca_pid = ((buf[i+4] & 0x1f) << 8) | buf[i+5]
        self.private_data_byte = buf[i+6:i+self.length+2]

    def __str__(self):
        hexa = ' '.join(["%02x"%(x) for x in self.private_data_byte])
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
            "    ca_system_id: 0x%04x, ca_pid: 0x%04x, private_data_byte: %s" % (
                self.ca_system_id, self.ca_pid, hexa) ])

