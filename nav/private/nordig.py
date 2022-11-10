from dvbsi.descriptor import Descriptor


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
    "NorDig logical channel descriptor version 1"
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

class NorDigLogicalChannelV2:
    "lcn in logical channel descriptor version 1"
    def __init__(self, buf, i):
        self.service_id = (buf[i] << 8) | buf[i+1]
        self.visible_service_flag = (buf[i+2] >> 7) & 0x1
        self.reserved = (buf[i+2] >> 2) & 0x1f
        self.logical_channel_number = ((buf[i+2] & 0x03) << 8) | buf[i+3]

    def __str__(self):
        return "      service_id:0x%04x visible:%d lcn:%d" % (
                self.service_id, self.visible_service_flag,
                self.logical_channel_number)

class NorDigChannelListV2:
    "channel_list in logical channel descriptor version 2"
    def __init__(self, buf, i):
        self.channel_list_id = buf[i]
        self.channel_list_name_length = buf[i+1]
        self.channel_list_name = buf[i+2:i+2+self.channel_list_name_length]
        i += 2 + self.channel_list_name_length
        self.country_code = buf[i:i+3]
        self.descriptor_length = buf[i+3]
        i += 4
        i_to = i + self.descriptor_length
        while (i < i_to):
            self.service_lcns.append(NorDigLogicalChannelV2(buf, i))
            i += 4

    def __str__(self):
        return '\n'.join([
            "    channel_list_id:0x%02x, name:%s, country_code:%s" % (
                   self.channel_list_id, self.channel_list_name,
                   self.country_code),
                '\n'.join([lcn.__str__()
                    for lcn in self.service_lcns]) ])

class NorDigLogicalChannelDescriptorV2(Descriptor):
    "logical channel descriptor version 2"
    def __init__(self, buf, i = 0):
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        self.channel_lists = []
        i += 2
        i_to = i + self.length
        while (i < i_to):
            channel_list = NorDigChannelListV2(buf, i)
            self.channel_lists.append(channel_list)
            i += (channel_list.channel_list_name_length + 
                  channel_list.descriptor_length + 6)

    def __str__(self):
        return '\n'.join([
                self.__class__.__name__ + " " + Descriptor.__str__(self),
                '\n'.join([channel_list.__str__()
                    for channel_list in self.channel_lists]) ])


PRIVATE_DATA_SPECIFIER_ID       = 0x00000029

DTAG_LOGICAL_CHANNEL_V1         = 0x83
DTAG_LOGICAL_CHANNEL_V2         = 0x87

DESCRIPTOR_MAP = {
    DTAG_LOGICAL_CHANNEL_V1:    NorDigLogicalChannelDescriptor,
    DTAG_LOGICAL_CHANNEL_V2:    NorDigLogicalChannelDescriptorV2,
}
