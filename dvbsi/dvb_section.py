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
# Foundation, Inc., 51 Franklin Street, 5th Floor, Boston, MA  02110-1301, USA
#

"""Parse sections defined by DVB"""


from .section import Section, SectionExt
from .descriptor import DescriptorLoop
from .dvb_types import dvbdate_to_datetime, dvbduration_to_seconds


TRANSPORT_NIT_PID = 0x10
TRANSPORT_SDT_PID = 0x11
TRANSPORT_BAT_PID = 0x11
TRANSPORT_EIT_PID = 0x12
TRANSPORT_CIT_PID = 0x12
TRANSPORT_RST_PID = 0x13
TRANSPORT_TDT_PID = 0x14
TRANSPORT_TOT_PID = 0x14
TRANSPORT_RNT_PID = 0x16
TRANSPORT_DIT_PID = 0x1e
TRANSPORT_SIT_PID = 0x1f


STAG_NETWORK_INFORMATION_ACTUAL           = 0x40
STAG_NETWORK_INFORMATION_OTHER            = 0x41

STAG_SERVICE_DESCRIPTION_ACTUAL           = 0x42
STAG_SERVICE_DESCRIPTION_OTHER            = 0x46

STAG_BOUQUET_ASSOCIATION                  = 0x4a
STAG_UPDATE_NOTIFICATION                  = 0x4b  # same syntax as IP_MAC
STAG_IP_MAC_NOTIFICATION                  = 0x4c

STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL     = 0x4e
STAG_EVENT_INFORMATION_NOWNEXT_OTHER      = 0x4f
STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL    = 0x50  # 0x50->0x5f
STAG_EVENT_INFORMATION_SCHEDULE_OTHER     = 0x60  # 0x60->0x6f

STAG_TIME_DATE                            = 0x70
STAG_RUNNING_STATUS                       = 0x71
STAG_STUFFING                             = 0x72
STAG_TIME_OFFSET                          = 0x73
STAG_APPLICATION_INFORMATION              = 0x74
STAG_TVA_CONTAINER                        = 0x75
STAG_TVA_RELATED_CONTENT                  = 0x76
STAG_TVA_CONTENT_IDENTIFIER               = 0x77
STAG_MPE_FEC                              = 0x78
STAG_TVA_RESOLUTION_PROVIDER_NOTIFICATION = 0x79

STAG_DISCONTINUITY_INFORMATION            = 0x7e
STAG_SELECTION_INFORMATION                = 0x7f


class SdtService:
    "Service in SDT"
    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.eit_schedule_flag = (buf[i+2] >> 1) & 1
        self.eit_present_following_flag = buf[i+2] & 1
        self.running_status = (buf[i+3] >> 5) & 7
        self.free_ca_mode = (buf[i+3] >> 4) & 1
        self.descriptors_loop_length = (((buf[i+3] & 0xf) << 8) | buf[i+4])
        descriptor_buf = buf[i+5:i+self.descriptors_loop_length + 5]
        self.descriptors = DescriptorLoop(descriptor_buf)

    def __str__(self):
        return "service_id:0x%04x eit_schedule_flag:%i" \
               " eit_present_following_flag:%i running_status:%i" \
               " free_ca_mode:%i" % (
                    self.service_id, self.eit_schedule_flag,
                    self.eit_present_following_flag,
                    self.running_status, self.free_ca_mode)

class SdtSection(SectionExt):
    "Service Description Table"
    def __init__(self, buf):
        self.transport_stream_id = -1
        self.original_network_id = -1
        self.services = []
        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            return
        self.transport_stream_id = self.table_id_ext
        self.original_network_id = (buf[8] << 8) | buf[9]

    def decode(self):
        buf = self.data
        self.services = []
        i = 11
        while (i < (self.length - 1)):
            service = SdtService(buf, i)
            self.services.append(service)
            i += service.descriptors_loop_length + 5
        return 0

    def __str__(self):
        return '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    transport_stream_id:0x%04x" % self.transport_stream_id,
            "    original_network_id:0x%04x" % self.original_network_id])

class Transport:
    "Transport in NIT or BAT"
    def __init__(self, buf, i):
        self.transport_stream_id = (buf[i] << 8) | buf[i+1]
        self.original_network_id = (buf[i+2] << 8) | buf[i+3]
        self.transport_descriptors_length = (((buf[i+4] & 0xf) << 8) |
                                               buf[i+5])
        descriptor_buf = buf[i+6:i+self.transport_descriptors_length + 6]
        self.descriptors = DescriptorLoop(descriptor_buf)

    def __str__(self):
        return "transport_stream_id:0x%04x original_network_id:0x%04x" % (
                    self.transport_stream_id,
                    self.original_network_id)

class NitSection(SectionExt):
    "Network Information Table"
    def __init__(self, buf):
        self.network_id = -1
        self.descriptors = []
        self.transports = []
        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            return
        self.network_id = self.table_id_ext

    def decode(self):
        buf = self.data
        network_descriptors_length = (((buf[8] & 0xf) << 8) | buf[9])
        i = 10 + network_descriptors_length
        descriptor_buf = buf[10:i]
        self.descriptors = DescriptorLoop(descriptor_buf)
        i += 2
        self.transports = []
        while (i < (self.length - 1)):
            transport = Transport(buf, i)
            self.transports.append(transport)
            i += transport.transport_descriptors_length + 6
        return 0

    def __str__(self):
        return '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    network_id:0x%04x" % self.network_id])


class BatSection(SectionExt):
    "Bouquet Association Table"
    def __init__(self, buf):
        self.transports = []
        self.descriptors = []
        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            bouquet_id = -1
            return
        self.bouquet_id = self.table_id_ext

    def decode(self):
        buf = self.data
        bouquet_descriptors_length = (((buf[8] & 0xf) << 8) | buf[9])
        i = 10 + bouquet_descriptors_length
        descriptor_buf = buf[10:i]
        self.descriptors = DescriptorLoop(descriptor_buf)
        i += 2
        self.transports = []
        while (i < (self.length - 1)):
            transport = Transport(buf, i)
            self.transports.append(transport)
            i += transport.transport_descriptors_length + 6
        return 0

    def __str__(self):
        return '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    bouquet_id:0x%04x" % self.bouquet_id])


class EitEvent:
    "Event in EIT"
    def __init__(self, buf, i):
        self.event_id = (buf[i] << 8) | buf[i+1]
        self.start_time = buf[i+2:i+7]
        self.duration = buf[i+7:i+10]
        self.running_status = (buf[i+10] >> 5) & 0x7
        self.free_ca_mode = (buf[i+10] >> 4) & 0x1
        self.descriptors_loop_length = (((buf[i+10] & 0xf) << 8) | buf[i+11])
        descriptor_buf = buf[i+12:i+self.descriptors_loop_length + 12]
        self.descriptors = DescriptorLoop(descriptor_buf)

    def __str__(self):
        dvb_time = dvbdate_to_datetime(self.start_time)
        return "event_id:0x%04x duration:%i running_status:%i" \
            " free_ca_mode:%i start_time:%02x%02x%02x%02x%02x -- %s" % (
                self.event_id,
                dvbduration_to_seconds(self.duration),
                self.running_status,
                self.free_ca_mode,
                self.start_time[0],
                self.start_time[1],
                self.start_time[2],
                self.start_time[3],
                self.start_time[4],
                dvb_time)

class EitSection(SectionExt):
    "Event Information Table"
    def __init__(self, buf):
        self.service_id = 0
        self.transport_stream_id = 0
        self.original_network_id = 0
        self.segment_last_section_number = 0
        self.last_table_id = 0
        self.events = []

        SectionExt.__init__(self, buf)
        if (self.table_id == -1):
            return
        self.service_id = self.table_id_ext
        self.transport_stream_id = (buf[8] << 8) | buf[9]
        self.original_network_id = (buf[10] << 8) | buf[11]
        self.segment_last_section_number = buf[12]
        if (self.section_number // 8 != self.segment_last_section_number // 8):
            self.table_id = -1
            return
        if (self.section_number % 8 > self.segment_last_section_number % 8):
            self.table_id = -1
            return
        self.last_table_id = buf[13]

    def decode(self):
        buf = self.data
        i = 14
        self.events = []
        while (i < (self.length - 1)):
            event = EitEvent(buf, i)
            self.events.append(event)
            i += event.descriptors_loop_length + 12
        return 0

    def __str__(self):
        return '\n'.join([
            self.__class__.__name__ + " " + SectionExt.__str__(self),
            "    service_id:0x%04x" % self.service_id,
            "    transport_stream_id:0x%04x" % self.transport_stream_id,
            "    original_network_id:0x%04x" % self.original_network_id,
            "    segment_last_section_number:0x%02x" % \
                                        self.segment_last_section_number,
            "    last_table_id:0x%02x" % self.last_table_id])


class TdtSection(Section):
    "Time and Data Table"
    def __init__(self, buf):
        self.utc_time = -1
        Section.__init__(self, buf)
        if (self.table_id == -1):
            return
        crc_i = self.length - 1
        self.crc_32 = (buf[crc_i] << 24) | (buf[crc_i + 1] << 16)
        self.crc_32 |= (buf[crc_i + 2] << 8) | buf[crc_i + 3]

    def decode(self):
        buf = self.data
        if (self.length != 5):
            return -1
        self.utc_time = buf[3:8]
        return 0

    def __str__(self):
        dvbtime = dvbdate_to_datetime(self.utc_time)
        return '\n'.join([
            self.__class__.__name__ + " " + Section.__str__(self),
            "    utc_time: %02x%02x%02x%02x%02x -- %s" % (
                self.utc_time[0],
                self.utc_time[1],
                self.utc_time[2],
                self.utc_time[3],
                self.utc_time[4],
                dvbtime)])

class TotSection(Section):
    "Time Offset Table"
    def __init__(self, buf):
        Section.__init__(self, buf)
        self.utc_time = -1
        self.descriptors = []

    def decode(self):
        buf = self.data
        self.utc_time = buf[3:8]
        descriptors_loop_length = ((buf[8] & 0xf) << 8) | buf[9]
        descriptor_buf = buf[10:descriptors_loop_length + 10]
        self.descriptors = DescriptorLoop(descriptor_buf)
        return 0

    def __str__(self):
        dvbtime = dvbdate_to_datetime(self.utc_time)
        return '\n'.join([
            self.__class__.__name__ + " " + Section.__str__(self),
            "    utc_time: %02x%02x%02x%02x%02x -- %s" % (
                self.utc_time[0],
                self.utc_time[1],
                self.utc_time[2],
                self.utc_time[3],
                self.utc_time[4],
                dvbtime)])

