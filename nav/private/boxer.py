from dvbsi.descriptor import Descriptor


class CBIBasicInfo:
    def __init__(self, buf, i):
        self.series_id = (buf[i] << 24) | (buf[i+1] << 16)
        self.series_id |= (buf[i+2] << 8) | buf[i+3]
        self.episode = (buf[i+4] << 8) | buf[i+5]
        self.episode_total = (buf[i+6] << 8) | buf[i+7]
        self.season = (buf[i+8] << 8) | buf[i+9]
        # TODO: rest of fields

    def __str__(self):
        return "    series_id:%08x season:%d episode:%d/%d" % (
            self.series_id, self.season, self.episode, self.episode_total)


class CBIDescriptor(Descriptor):
    "CBI"
    def __init__(self, buf, i=0):
        self.cbitype = 0
        Descriptor.__init__(self, buf, i)
        if (self.tag == -1):
            return
        if (self.length == 0):
            return
        self.cbitype = buf[i + 2]
        if (self.cbitype == 1):
            self.basic_info = CBIBasicInfo(buf, i + 3)

    def __str__(self):
        string = self.__class__.__name__ + " " + Descriptor.__str__(self)
        if (self.cbitype == 1):
            return '\n'.join([string, self.basic_info.__str__()])
        else:
            return string


PRIVATE_DATA_SPECIFIER_ID = 0x00000014

DTAG_CBI = 0xbc

DESCRIPTOR_MAP = {
    DTAG_CBI:                   CBIDescriptor,
}
