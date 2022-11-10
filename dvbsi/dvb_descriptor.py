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

"""Descriptors defined by DVB"""

from .descriptor import Descriptor
from .dvb_types import bcd_to_integer


#
# Enumeration of DVB descriptor tags.
#
DTAG_NETWORK_NAME           = 0x40
DTAG_SERVICE_LIST           = 0x41
DTAG_STUFFING               = 0x42
DTAG_SATELLITE_DELIVERY_SYSTEM  = 0x43
DTAG_CABLE_DELIVERY_SYSTEM      = 0x44
DTAG_VBI_DATA               = 0x45
DTAG_VBI_TELETEXT           = 0x46
DTAG_BOUQUET_NAME           = 0x47
DTAG_SERVICE                = 0x48
DTAG_COUNTRY_AVAILABILITY       = 0x49
DTAG_LINKAGE                = 0x4A
DTAG_NVOD_REFERENCE         = 0x4B
DTAG_TIME_SHIFTED_SERVICE       = 0x4C
DTAG_SHORT_EVENT            = 0x4D
DTAG_EXTENDED_EVENT         = 0x4E
DTAG_TIME_SHIFTED_EVENT     = 0x4F
DTAG_COMPONENT              = 0x50
DTAG_MOSAIC                 = 0x51
DTAG_STREAM_IDENTIFIER      = 0x52
DTAG_CA_IDENTIFIER          = 0x53
DTAG_CONTENT                = 0x54
DTAG_PARENTAL_RATING        = 0x55
DTAG_TELETEXT               = 0x56
DTAG_TELEPHONE              = 0x57
DTAG_LOCAL_TIME_OFFSET      = 0x58
DTAG_SUBTITLING             = 0x59
DTAG_TERRESTRIAL_DELIVERY_SYSTEM = 0x5A
DTAG_MULTILINGUAL_NETWORK_NAME   = 0x5B
DTAG_MULTILINGUAL_BOUQUET_NAME   = 0x5C
DTAG_MULTILINGUAL_SERVICE_NAME   = 0x5D
DTAG_MULTILINGUAL_COMPONENT      = 0x5E
DTAG_PRIVATE_DATA_SPECIFIER = 0x5F
DTAG_SERVICE_MOVE           = 0x60
DTAG_SHORT_SMOOTHING_BUFFER = 0x61
DTAG_FREQUENCY_LIST         = 0x62
DTAG_PARTIAL_TRANSPORT_STREAM = 0x63
DTAG_DATA_BROADCAST         = 0x64
DTAG_SCRAMBLING             = 0x65
DTAG_DATA_BROADCAST_ID      = 0x66
DTAG_TRANSPORT_STREAM       = 0x67
DTAG_DSNG                   = 0x68
DTAG_PDC                    = 0x69
DTAG_AC3                    = 0x6A
DTAG_ANCILLARY_DATA         = 0x6B
DTAG_CELL_LIST              = 0x6C
DTAG_CELL_FREQUENCY_LINK    = 0x6D
DTAG_ANNOUNCEMENT_SUPPORT   = 0x6E
DTAG_APPLICATION_SIGNALLING = 0x6F
DTAG_ADAPTATION_FIELD_DATA  = 0x70
DTAG_SERVICE_IDENTIFIER     = 0x71
DTAG_SERVICE_AVAILABILITY   = 0x72
DTAG_DEFAULT_AUTHORITY      = 0x73
DTAG_RELATED_CONTENT        = 0x74
DTAG_TVA_ID                 = 0x75
DTAG_CONTENT_IDENTIFIER     = 0x76
DTAG_TIME_SLICE_FEC_IDENTIFIER  = 0x77
DTAG_ECM_REPETITION_RATE        = 0x78
DTAG_S2_SATELLITE_DELIVERY_DESCRIPTOR = 0x79
DTAG_ENHANCED_AC3           = 0x7A
DTAG_DTS                    = 0x7B
DTAG_AAC                    = 0x7C
DTAG_EXTENSION              = 0x7F

# descriptors which may only appear in an RNT
DTAG_RNT_RAR_OVER_DVB_STREAM = 0x40
DTAG_RNT_RAR_OVER_IP         = 0x41
DTAG_RNT_RNT_SCAN            = 0x42

# descriptors which may only appear in an AIT
DTAG_AIT_APPLICATION         = 0x00
DTAG_AIT_APPLICATION_NAME    = 0x01
DTAG_AIT_TRANSPORT_PROTOCOL  = 0x02
DTAG_AIT_DVB_J_APPLICATION   = 0x03
DTAG_AIT_DVB_J_APPLICATION_LOCATION = 0x04
DTAG_AIT_EXTERNAL_APPLICATION_AUTHORISATION = 0x05
DTAG_AIT_DVB_HTML_APPLICATION = 0x08
DTAG_AIT_DVB_HTML_APPLICATION_LOCATION = 0x09
DTAG_AIT_DVB_HTML_APPLICATION_BOUNDARY = 0x0A
DTAG_AIT_APPLICATION_ICONS      = 0x0B
DTAG_AIT_PREFETCH           = 0x0C
DTAG_AIT_DII_LOCATION       = 0x0D
DTAG_AIT_IP_SIGNALLING      = 0x11

# descriptors which may only appear in INT
DTAG_TARGET_IP_ADDRESS      = 0x09
DTAG_TARGET_IPV6_ADDRESS        = 0x0A
DTAG_IP_MAC_PLATFORM_NAME       = 0x0C
DTAG_IP_MAC_PLATFORM_PROVIDER_NAME  = 0x0D
DTAG_TARGET_IP_SLASH        = 0x0F
DTAG_TARGET_IP_SOURCE_SLASH     = 0x10
DTAG_TARGET_IPV6_SLASH      = 0x11
DTAG_TARGET_IPV6_SOURCE_SLASH   = 0x12
DTAG_IP_MAC_STREAM_LOCATION     = 0x13


# service type
DIGITAL_TV     = 0x01
DIGITAL_RADIO  = 0x02
TELETEXT       = 0x03
NVOD_REF       = 0x04
NVOD_TIMESHIFT = 0x05
MOSAIC         = 0x06
AVC_RADIO      = 0x0a
AVC_MOSAIC     = 0x0b
DATA_BCAST     = 0x0c
RCS_MAP        = 0x0e
RCS_FLS        = 0x0f
DVB_MHP        = 0x10
MPEG2_HD_DIGITAL_TV   = 0x11
AVC_SD_DIGITAL_TV     = 0x16
AVC_SD_NVOD_TIMESHIFT = 0x17
AVC_SD_NVOD_REF       = 0x18
AVC_HD_DIGITAL_TV     = 0x19
AVC_HD_NVOD_TIMESHIFT = 0x1a
AVC_HD_NVOD_REF       = 0x1b
AVC_PS_3D_HD_DIGITAL_TV     = 0x1c
AVC_PS_3D_HD_NVOD_TIMESHIFT = 0x1d
AVC_PS_3D_HD_NVOD_REF       = 0x1e


class Service:
    "service in service list descriptor"

    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.service_type = buf[i+2]

    def __str__(self):
        return "    service_id:0x%04x service_type:0x%02x" % (
                self.service_id, self.service_type)


class ServiceListDescriptor(Descriptor):
    "service list descriptor"
    def __init__(self, buf, i=0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.services = []
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.services.append(Service(buf, i))
            i += 3

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([service.__str__()
                    for service in self.services]) ])


class ServiceDescriptor(Descriptor):
    "service descriptor"
    def __init__(self, buf, i = 0):
        self.service_type = 0
        self.service_name = ""
        self.service_provider_name = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.service_type = buf[i+2]
        name_len = buf[i+3]
        self.service_provider_name = buf[i+4:i+4+name_len]
        i += name_len + 4
        name_len = buf[i]
        self.service_name = buf[i+1:i+1+name_len]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    service_type:%02x" % self.service_type,
                "    provider_name:%s" % self.service_provider_name,
                "    name:%s" % self.service_name])


class ShortEventDescriptor(Descriptor):
    """short event descriptor"""
    def __init__(self, buf, i = 0):
        self.language_code = ""
        self.event_name = ""
        self.text = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.language_code = buf[i+2:i+5].decode()
        name_len = buf[i+5]
        self.event_name = buf[i+6:i+6+name_len]
        i += name_len + 6
        text_len = buf[i]
        self.text = buf[i+1:i+1+text_len]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    language_code:%s" % self.language_code,
                "    event_name:%s" % self.event_name,
                "    text:%s" % self.text])


class Item():
    """item in extended event descriptor"""
    def __init__(self, buf, i):
        self.item_description_length = buf[i]
        i += 1
        self.item_description = buf[i:i+self.item_description_length]
        i += self.item_description_length
        self.item_length = buf[i]
        i += 1
        self.item = buf[i:i+self.item_length]

    def __str__(self):
        return "    item_desc:%s, item:%s" % (
                self.item_description, self.item)

class ExtendedEventDescriptor(Descriptor):
    """extended event descriptor"""
    def __init__(self, buf, i = 0):
        self.language_code = ""
        self.text = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.language_code = buf[i+3:i+6].decode()
        item_len = buf[i+6]
        i += 7
        i_to = i + item_len
        self.items = []
        while (i < i_to):
            item = Item(buf, i)
            self.items.append(item)
            i += item.item_description_length + item.item_length + 2

        text_len = buf[i]
        self.text = buf[i+1:i+1+text_len]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    language_code:%s" % self.language_code,
                '\n'.join([item.__str__() for item in self.items]),
                "    text:%s" % self.text])

class StreamIdentifierDescriptor(Descriptor):
    """stream identifier descriptor"""
    def __init__(self, buf, i = 0):
        self.component_tag = 0
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.component_tag = buf[i+2]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    component_tag:%i" % self.component_tag])

class SubtitlingEntry:
    """entry in subtitling descriptor"""
    def __init__(self, buf, i):
        self.language_code = buf[i:i+3].decode()
        self.subtitling_type = buf[i+3]
        self.composition_page_id = (buf[i+4] << 8) | buf[i+5]
        self.ancillary_page_id = (buf[i+6] << 8) | buf[i+7]

    def __str__(self):
        return "    language_code:%s subtitling_type:0x%02x " \
            "composition_page_id:0x%04x ancillary_page_id:0x%04x" % (
                self.language_code, self.subtitling_type,
                self.composition_page_id, self.ancillary_page_id)

class SubtitlingDescriptor(Descriptor):
    """subtitling descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(SubtitlingEntry(buf, i))
            i += 8

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class MultilingualServiceName:
    "service name in muntilingual service name descriptor"
    def __init__(self, buf, i):
        self.language_code = buf[i:i+3].decode()
        self.service_provider_name_length = buf[i+3]
        self.service_provider_name = buf[i+4:i+4+self.service_provider_name_length]
        i += self.service_provider_name_length+4
        self.service_name_length = buf[i]
        self.service_name = buf[i+1:i+self.service_name_length+1]
        #self.service_name_length = 0
        #self.service_name = ""

    def __str__(self):
        return '\n'.join([
                "    language_code:%s" % self.language_code,
                "        service_provider_name:%s" % self.service_provider_name,
                "        service_name:%s" % self.service_name])

class MultilingualServiceNameDescriptor(Descriptor):
    """multilingual service name descriptor"""
    def __init__(self, buf, i = 0):
        self.names = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            name = MultilingualServiceName(buf, i)
            self.names.append(name)
            i += 5 + name.service_provider_name_length
            i += name.service_name_length

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([name.__str__() for name in self.names]) ])

class DataBroadcastIdDescriptor(Descriptor):
    """data broadcast id descriptor"""
    def __init__(self, buf, i = 0):
        self.data_broadcast_id = 0
        self.id_selector_byte = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.data_broadcast_id = (buf[i+2] << 8) | buf[i+3]
        self.id_selector_byte = buf[i+4:i+self.length+2]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    data_broadcast_id:0x%04x" % self.data_broadcast_id,
                "    id_selector_byte:%s" % ' '.join(["%02x" % x for x in
                                                      self.id_selector_byte])])

class DefaultAuthorityDescriptor(Descriptor):
    """default authority descriptor"""
    def __init__(self, buf, i = 0):
        self.name = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.name = buf[i+2:i+self.length+2].decode()

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    name:%s" % self.name])

class ComponentDescriptor(Descriptor):
    """component descriptor"""
    def __init__(self, buf, i = 0):
        self.stream_content = 0
        self.component_type = 0
        self.component_tag = 0
        self.language_code = ""
        self.text = ""
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.stream_content = buf[i+2] & 0xf
        self.component_type = buf[i+3]
        self.component_tag = buf[i+4]
        self.language_code = buf[i+5:i+8].decode()
        self.text = buf[i+8:i+self.length+2]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    stream_content:%i" % self.stream_content,
                "    component_type:%i" % self.component_type,
                "    component_tag:%i" % self.component_tag,
                "    language_code:%.3s" % self.language_code,
                "    text:%s" % self.text])

class PrivateDataSpecifierDescriptor(Descriptor):
    "private data specifier descriptor"
    def __init__(self, buf, i = 0):
        private_data_specifier = 0
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.private_data_specifier = (buf[i+2] << 24)
        self.private_data_specifier |= (buf[i+3] << 16)
        self.private_data_specifier |= (buf[i+4] << 8)
        self.private_data_specifier |= buf[i+5]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    private_data_specifier:0x%08x" % \
                            self.private_data_specifier])

class Content:
    "content in content descriptor"
    def __init__(self, buf, i):
        self.content_nibble_level_1 = (buf[i] >> 4) & 0xf
        self.content_nibble_level_2 = buf[i] & 0xf
        self.user_byte = buf[i+1]

    def __str__(self):
        return "    content_nibble_level_1:0x%x content_nibble_level_2:0x%x" \
               " user_byte:0x%x" % (
                self.content_nibble_level_1,
                self.content_nibble_level_2,
                self.user_byte)

class ContentDescriptor(Descriptor):
    """content descriptor"""
    def __init__(self, buf, i = 0):
        self.contents = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.contents.append(Content(buf, i))
            i += 2

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([content.__str__() for content in self.contents]) ])


class NetworkNameDescriptor(Descriptor):
    """network name descriptor"""
    def __init__(self, buf, i = 0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            self.network_name = ""
            return
        self.network_name = buf[i+2:i+self.length+2]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    name:%s" % self.network_name])

class BouquetNameDescriptor(Descriptor):
    """bouquet name descriptor"""
    def __init__(self, buf, i = 0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            self.bouquet_name = ""
            return
        self.bouquet_name = buf[i+2:i+self.length+2]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    name:%s" % self.bouquet_name])

class ParentalRating:
    "parental rating in parental rating descriptor"
    def __init__(self, buf, i):
        self.country_code = buf[i:i+3]
        self.rating = buf[i+3]

    def __str__(self):
        return "  country_code:%s rating %i" % (
                self.country_code, self.rating)

class ParentalRatingDescriptor(Descriptor):
    """parental rating descriptor"""
    def __init__(self, buf, i = 0):
        self.parental_ratings = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.parental_ratings.append(ParentalRating(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([rate.__str__() for rate in self.parental_ratings]) ])

class DataBroadcastDescriptor(Descriptor):
    """data broadcast descriptor"""
    def __init__(self, buf, i = 0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            self.data_broadcast_id = 0
            self.component_tag = 0
            self.selector = ""
            self.language_code = ""
            self.text = ""
            return
        self.data_broadcast_id = (buf[i+2] << 8) | buf[i+3]
        self.component_tag = buf[i+4]
        length = buf[i+5]
        self.selector = buf[i+6:i+6+length]
        i += length + 6
        self.language_code = buf[i:i+3].decode()
        i += 3
        length = buf[i]
        self.text = buf[i+1:i+1+length]

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                "    data_broadcast_id:0x%04x" % self.data_broadcast_id,
                "    component_tag:0x%02x" % self.component_tag,
                "    selector:%s" % self.selector,
                "    language_code:%s" % self.language_code,
                "    text:%s" % self.text])


class SatelliteDeliverySystemDescriptor(Descriptor):

    POLARIZATION_STR = ["linear_horizontal",
                        "linear_vertical",
                        "circular_left",
                        "circular_right",
                        "?"]

    MODULATION_SYSTEM_STR = ["DVB-S", "DVB-S2"]

    def __init__(self, buf, i=0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        bcd = (buf[i+2] << 24) | (buf[i+3] << 16)
        bcd |= (buf[i+4] << 8) | buf[i+5]
        # self.frequency is in MHz
        self.frequency = int(bcd_to_integer(bcd) / 100)
        bcd = (buf[i+6] << 8) | buf[i+7]
        self.orbital_position = bcd_to_integer(bcd)
        west_east_flag = (buf[i+8] >> 7) & 1
        if (west_east_flag == 0):
            self.orbital_position = -self.orbital_position
        self.polarization = (buf[i+8] >> 5) & 3
        self.roll_off = (buf[i+8] >> 3) & 3
        self.modulation_system = (buf[i+8] >> 2) & 1
        self.modulation_type = buf[i+8] & 3
        bcd = (buf[i+9] << 24) | (buf[i+10] << 16)
        bcd |= (buf[i+11] << 8) | buf[i+12]
        self.symbol_rate = int(bcd_to_integer(bcd >> 4) / 10)
        self.fec_inner = buf[i+12] & 0xf

    def __str__(self):
        if (self.orbital_position < 0):
            we_str = "west"
        else:
            we_str = "east"
        orbital_position = abs(self.orbital_position)
        pol_str = self.POLARIZATION_STR[self.polarization]
        sys_str = self.MODULATION_SYSTEM_STR[self.modulation_system]
        name_str = self.__class__.__name__ + " " + Descriptor.__str__(self)
        str1 = "    frequency: %d MHz" % self.frequency
        str1 += ", Orb %d" % int(orbital_position / 10)
        str1 += "%d deg" % (orbital_position % 10)
        str1 += ", " + we_str
        str1 += ", " + pol_str
        str2 = "    roll_off:%d" % self.roll_off
        str2 += ", modulation_system: " + sys_str
        str2 += ", type:%d" % self.modulation_type
        str2 += ", symbol_rate: %d ksymbol/s" % self.symbol_rate
        str2 += ", fec_inner:%d" % self.fec_inner
        return '\n'.join([name_str, str1, str2])


class TerrestrialDeliverySystemDescriptor(Descriptor):

    BANDWIDTH_STR = ["8 MHz", "7 MHz", "6 MHz", "5 MHz",
                     "4?", "5?", "6?", "7?"]
    PRIORITY_STR = ["LP", "HP"]
    CONSTELLATION_STR = ["QPSK", "16-QAM", "64-QAM", "4?"]
    CODE_RATE_STR = ["1/2", "2/3", "3/4", "5/6", "7/8", "5?", "6?", "7?"]
    GUARD_INTERVAL_STR = ["1/32", "1/16", "1/8", "1/4", "AUTO?"]
    TRANSMISSION_MODE_STR = ["2k", "8k", "4k", "3?"]

    def __init__(self, buf, i=0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        centre_frequency = ((buf[i+2] << 24) | (buf[i+3] << 16) |
                            (buf[i+4] << 8) | buf[i+5])
        # self.frequency is in kHz
        self.frequency = int(centre_frequency / 100)
        self.bandwidth = buf[i+6] >> 5
        self.priority = (buf[i+6] >> 4) & 1
        self.time_slicing_indicator = (buf[i+6] >> 3) & 1
        self.mpe_fec_indicator = (buf[i+6] >> 2) & 1
        self.reserved1 = buf[i+6] & 0x3
        self.constellation = (buf[i+7] >> 6) & 0x3
        self.hierarchy_information = (buf[i+7] >> 3) & 0x7
        self.code_rate_hp_stream = buf[i+7] & 0x7
        self.code_rate_lp_stream = (buf[i+8] >> 5) & 0x7
        self.guard_interval = (buf[i+8] >> 3) & 0x3
        self.transmission_mode = (buf[i+8] >> 1) & 0x3
        self.other_frequency_flag = buf[i+8] & 0x1
        self.reserved2 = (buf[i+9] << 24) | (buf[i+10] << 16)
        self.reserved2 |= (buf[i+11] << 8) | buf[i+12]

    def __str__(self):
        name_str = self.__class__.__name__ + " " + Descriptor.__str__(self)
        str1 = "    centre_frequency: %d kHz" % self.frequency
        str1 += ", bandwidth: " + self.BANDWIDTH_STR[self.bandwidth]
        str2 = "    priority: " + self.PRIORITY_STR[self.priority]
        str2 += ", time_slicing_indicator: %d" % self.time_slicing_indicator
        str2 += ", mpe_fec_indicator: %d" % self.mpe_fec_indicator
        str3 = "    constellation: "
        str3 += self.CONSTELLATION_STR[self.constellation]
        str3 += ", hierarchy_information: %d" % self.hierarchy_information
        str3 += ", code_rate_hp: "
        str3 += self.CODE_RATE_STR[self.code_rate_hp_stream]
        str3 += ", code_rate_lp: "
        str3 += self.CODE_RATE_STR[self.code_rate_lp_stream]
        str4 = "    guard_interval: "
        str4 += self.GUARD_INTERVAL_STR[self.guard_interval]
        str4 += ", transmission_mode: "
        str4 += self.TRANSMISSION_MODE_STR[self.transmission_mode]
        str4 += ", other_frequency_flag: %d" % self.other_frequency_flag
        return '\n'.join([name_str, str1, str2, str3, str4])


class CableDeliverySystemDescriptor(Descriptor):

    MODULATION_SCHEME_STR = ["",
                             "16-QAM",
                             "32-QAM",
                             "64-QAM",
                             "128-QAM",
                             "256-QAM"]

    INNER_FEC_STR = ["",
                     "1/2",
                     "2/3",
                     "3/4",
                     "5/6",
                     "7/8",
                     "8/9",
                     "3/5",
                     "4/5",
                     "9/10"]

    def __init__(self, buf, i=0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        bcd = (buf[i + 2] << 24) | (buf[i + 3] << 16)
        bcd |= (buf[i + 4] << 8) | buf[i + 5]
        # self.frequency is in kHz
        self.frequency = int(bcd_to_integer(bcd) / 10)
        self.fec_outer = buf[i + 7] & 0xf
        self.modulation = buf[i + 8]
        bcd = (buf[i + 9] << 20) | (buf[i + 10] << 12)
        bcd |= (buf[i + 11] << 4) | ((buf[i + 12] >> 4) & 0xf)
        self.symbol_rate = int(bcd_to_integer(bcd) / 10)
        self.fec_inner = buf[i + 12] & 0xf

    def __str__(self):
        if (0 < self.modulation < len(self.MODULATION_SCHEME_STR)):
            mod_str = self.MODULATION_SCHEME_STR[self.modulation]
        else:
            mod_str = hex(self.modulation)
        if (0 < self.fec_inner < len(self.INNER_FEC_STR)):
            fec_inner_str = self.INNER_FEC_STR[self.fec_inner]
        else:
            fec_inner_str = hex(self.fec_inner)
        name_str = self.__class__.__name__ + " " + Descriptor.__str__(self)
        str1 = "    frequency: %d kHz" % self.frequency
        str1 += ", fec_outer: " + hex(self.fec_outer)
        str1 += ", modulation: " + mod_str
        str1 += ", symbol_rate: %d ksymbol/s" % self.symbol_rate
        str1 += ", fec_inner: " + fec_inner_str
        return '\n'.join([name_str, str1])


CRID_TYPE_PROGRAM_CRID = 0x01
CRID_TYPE_SERIES_CRID = 0x02
CRID_TYPE_RECOMMENDATION = 0x03

class Crid:
    "CRID in content identifier descriptor"

    def __init__(self, buf, i):
        self.crid_type = (buf[i] >> 2) & 0x3f
        self.location = buf[i] & 0x03
        if (self.location == 0):
            self.crid_length = buf[i+1]
            self.crid_byte = buf[i+2:i+2+self.crid_length].decode()
        elif (self.location == 1):
            self.crid_length = 1
            self.crid_ref = (buf[i+1] << 8) | buf[i+2]

    def __str__(self):
        if (self.location == 0):
            return "  crid_type:%d, crid_location:%d, crid_byte:%s" % (
                self.crid_type, self.location, self.crid_byte)
        elif (self.location == 1):
            return "  crid_type:%d, crid_location:%d, crid_ref:0x%x" % (
                self.crid_type, self.location, self.crid_ref)
        else:
            return "  crid_type:%d, crid_location:%d" % (
                self.crid_type, self.location)

class ContentIdentifierDescriptor(Descriptor):
    """content identifier descriptor"""
    def __init__(self, buf, i = 0):
        self.crids = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            crid = Crid(buf, i)
            self.crids.append(crid)
            i += crid.crid_length + 2

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([crid.__str__() for crid in self.crids]) ])

class TeletextEntry:
    """entry in teletext descriptor"""
    def __init__(self, buf, i):
        self.language_code = buf[i:i+3].decode()
        self.teletext_type = (buf[i+3] >> 3) & 0x1f
        self.teletext_magazine_number = buf[i+3] & 0x07
        self.teletext_page_number = buf[i+4]

    def __str__(self):
        return "    language_code:%s teletext_type:0x%02x " \
            "teletext_magazine_number:0x%x " \
            "teletext_page_number:0x%02x" % (
                self.language_code, self.teletext_type,
                self.teletext_magazine_number, self.teletext_page_number)

class TeletextDescriptor(Descriptor):
    """teletext descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(TeletextEntry(buf, i))
            i += 5

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class LocalTimeOffset:
    """entry in local time descriptor"""
    def __init__(self, buf, i):
        self.country_code = buf[i:i+3]
        self.country_region_id = (buf[i+3] >> 2) & 0x3f
        self.local_time_offset_polarity = buf[i+3] & 0x1
        self.local_time_offset = buf[i+4:i+6]
        self.time_of_change = buf[i+6:i+11]
        self.next_time_offset = buf[i+11:i+13]

    def __str__(self):
        return "    country_code:%s region_id:%d polarity:%d offset:%02x%02x" \
                " time_of_change: %02x%02x%02x%02x%02x" \
                " next_time_offset:%02x%02x" % (
                    self.country_code, self.country_region_id,
                    self.local_time_offset_polarity,
                    self.local_time_offset[0],
                    self.local_time_offset[1],
                    self.time_of_change[0],
                    self.time_of_change[1],
                    self.time_of_change[2],
                    self.time_of_change[3],
                    self.time_of_change[4],
                    self.next_time_offset[0],
                    self.next_time_offset[1])

class LocalTimeOffsetDescriptor(Descriptor):
    """local time offset descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i_to = i + self.length - 6
        i += 2
        while (i < i_to):
            self.entries.append(LocalTimeOffset(buf, i))
            i += 13

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class UkDttLogicalChannel:
    '''entry in logical channel descriptor'''
    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.logical_channel_number = ((buf[i+2] & 0x03) << 8) | buf[i+3]

    def __str__(self):
        return "    service_id:%04x lcn:%d" % (
            self.service_id, self.logical_channel_number)

class UkDttLogicalChannelDescriptor(Descriptor):
    """local time offset descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(UkDttLogicalChannel(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class NorDigLogicalChannel:
    '''entry in logical channel descriptor'''
    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.visible_service_flag = (buf[i+2] >> 7) & 0x1
        self.logical_channel_number = ((buf[i+2] & 0x3f) << 8) | buf[i+3]

    def __str__(self):
        return "    service_id:%04x visible:%d lcn:%d" % (
            self.service_id, self.visible_service_flag,
            self.logical_channel_number)

class NorDigLogicalChannelDescriptor(Descriptor):
    """local time offset descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(NorDigLogicalChannel(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

class EacemLogicalChannel:
    '''entry in logical channel descriptor'''
    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.visible_service_flag = (buf[i+2] >> 7) & 0x1
        self.logical_channel_number = ((buf[i+2] & 0x03) << 8) | buf[i+3]

    def __str__(self):
        return "    service_id:%04x visible:%d lcn:%d" % (
            self.service_id, self.visible_service_flag,
            self.logical_channel_number)

class EacemLogicalChannelDescriptor(Descriptor):
    """local time offset descriptor"""
    def __init__(self, buf, i = 0):
        self.entries = []
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        i += 2
        i_to = i + self.length
        while (i < i_to):
            self.entries.append(EacemLogicalChannel(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([entry.__str__() for entry in self.entries]) ])

