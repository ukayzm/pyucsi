import window
import frontend
import db_center
from datetime import datetime
import dvb
import logging

service_type_string = [
    "",
    "DIGITAL_TV",       # 0x01
    "DIGITAL_RADIO",    # 0x02
    "TELETEXT",         # 0x03
    "NVOD_REF",         # 0x04
    "NVOD_SHIFT",       # 0x05
    "MOSAIC",           # 0x06
    "",
    "",
    "",
    "AVC_RADIO",        # 0x0a
    "AVC_MOSAIC",       # 0x0b
    "DATA_BROADCAST",   # 0x0c
    "",
    "RCS_MAP",          # 0x0e
    "RCS_FLS",          # 0x0f
    "DVB_MHP",          # 0x10
    "MPEG2_HDTV",       # 0x11
    "",
    "",
    "",
    "",
    "AVC_SDTV",          # 0x16
    "AVC_SD_NVOD_SFT",   # 0x17
    "AVC_SD_NVOD_REF",   # 0x18
    "AVC_HDTV",          # 0x19
    "AVC_HD_NVOD_SFT",   # 0x1a
    "AVC_HD_NVOD_REF",   # 0x1b
]

stream_type_string = [
    "",
    "11172_2_VIDEO",         # 0x01
    "13818_2_VIDEO",         # 0x02
    "11172_3_AUDIO",         # 0x03
    "13818_3_AUDIO",         # 0x04
    "13818_1_PRIVATE_SEC",   # 0x05
    "13818_1_PRIVATE_PES",   # 0x06
    "13522_MHEG",            # 0x07
    "13818_1_DSMCC",         # 0x08
    "ITUH222_1",             # 0x09
    "13818_6_A",             # 0x0a
    "13818_6_B",             # 0x0b
    "13818_6_C",             # 0x0c
    "13818_6_D",             # 0x0d
    "13818_1_AUX",           # 0x0e
    "13818_7_AUDIO_ADTS",    # 0x0f
    "14496_2_VISUAL",        # 0x10
    "14496_3_AUDIO_LATM",    # 0x11
    "14496_1_PES",           # 0x12
    "14496_1_SECTIONS",      # 0x13
    "14496_6_SYNC_DNLOAD",   # 0x14
    "METADATA_PES",          # 0x15
    "METADATA_SECTIONS",     # 0x16
    "METADATA_DSMCC_DATA",   # 0x17
    "METADATA_DSMCC_OBJ",    # 0x18
    "METADATA_SYNC_DNLOAD",  # 0x19
    "13818_11_IPMP",         # 0x1a
    "H.264_VIDEO",           # 0x1b
]

dvb_subtitle_type_string = {
    0x01: "EBU subtitle",
    0x02: "associated EBU",
    0x03: "VBI data",
    0x10: "DVB, no AR",
    0x11: "DVB, 4:3",
    0x12: "DVB, 16:9",
    0x13: "DVB, 2.21:1",
    0x14: "DVB, HD",
    0x20: "DVB (HoH), no AR",
    0x21: "DVB (HoH), 4:3",
    0x22: "DVB (HoH), 16:9",
    0x23: "DVB (HoH), 2.21:1",
    0x24: "DVB (HoH), HD",
    0x30: "Open sign",
    0x31: "Closed sign",
    0x40: "Video up-sampled",
}

teletext_type_string = [
    "",
    "initial_page",
    "subtitle",
    "info",
    "schedule",
    "subtitle (HoH)",
]


class InfoWin(window.Window):
    def __init__(self):
        window.Window.__init__(self)
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.logger = logging.getLogger('MainLog')

    def refresh(self):
        pass

    def print_ts(self, service):
        if (self.win is None):
            return
        ts_key = service.ts_key
        string = "Tuning param [ "
        ts = self.db.read_transport(ts_key)
        string += str(ts)
        string += " ]"

        self.win.addstr(0, 1, string)

    def print_service(self, service):
        if (self.win is None):
            return

        self.win.addstr(1, 1, "svc_key: %d" % service.svc_key)
        self.win.addstr(2, 1, "lcn: ")
        if (service.lcn):
            self.win.addstr(2, 6, "%d" % service.lcn)

        if (service._type):
            self.win.addstr(1, 35, "service_type: 0x%02x" % service._type)
            if (service._type < len(service_type_string)):
                string = "(%s)" % (service_type_string[service._type])
            else:
                string = "(???)"
            self.win.addstr(2, 35, string)

        self.win.addstr(1, 16, "onid.tsid.svid")
        self.win.addstr(1, 60, "network_id: ")
        c = self.connection.cursor()
        c.execute(''' select nid, tsid, onid, svid
                  from services inner join transports
                  on services.ts_key = transports.ts_key
                  where svc_key = ?''',
                  [service.svc_key])
        row = c.fetchone()
        if (row):
            string = "%04x.%04x.%04x" % (row['onid'], row['tsid'], row['svid'])
            self.win.addstr(2, 16, string)
            self.win.addstr(1, 72, "0x%04x" % row['nid'])

        string = "name: ["
        nid = row['nid']
        c.execute('''select * from networks where nid = ?''', [nid])
        row = c.fetchone()
        if (row):
            string += "%s" % row['net_name']
        string += "]"
        self.win.addstr(2, 60, string)

    def get_stream_type_string(self, stream_type):
        string = "0x%02x (" % stream_type
        if (len(stream_type_string) <= stream_type):
            string += "???"
        else:
            string += stream_type_string[stream_type]
        return string

    def add_audio_stream_string(self, strm_key, strings):
        c = self.connection.cursor()
        c.execute('''select * from streams_audio where strm_key = ?;''',
                  [strm_key])
        rows = c.fetchall()
        if (not rows):
            return
        for row in rows:
            codec = row['codec']
            if (codec == dvb.AUDIO_CODEC_MPEG_MONO_LEFT):
                codec_string = "MPEG-L"
            elif (codec == dvb.AUDIO_CODEC_MPEG_MONO_RIGHT):
                codec_string = "MPEG-R"
            elif (codec == dvb.AUDIO_CODEC_MPEG_STEREO):
                codec_string = "MPEG"
            elif (codec == dvb.AUDIO_CODEC_AC3):
                codec_string = "AC3"
            elif (codec == dvb.AUDIO_CODEC_E_AC3):
                codec_string = "E-AC3"
            elif (codec == dvb.AUDIO_CODEC_DTS):
                codec_string = "DTS"
            elif (codec == dvb.AUDIO_CODEC_AAC):
                codec_string = "AAC"
            else:
                codec_string = "???"

            string = "     AUD [" + row['lang'] + "]"
            string += " %s, audio_type %d" % (codec_string, row['audio_type'])
            strings.append(string)

    def add_dvb_subtitle_stream_string(self, strm_key, strings):
        c = self.connection.cursor()
        c.execute('''select * from streams_dvb_subtitle where strm_key = ?;''',
                  [strm_key])
        rows = c.fetchall()
        if (not rows):
            return
        for row in rows:
            string = "     SUB [" + row['lang'] + "] "
            subtitle_type = row['subtitling_type']
            type_string = dvb_subtitle_type_string.get(subtitle_type)
            if (type_string is None):
                type_string = "type 0x%02x" % subtitle_type
            string += type_string
            strings.append(string)

    def add_teletext_stream_string(self, strm_key, strings):
        c = self.connection.cursor()
        c.execute('''select * from streams_teletext where strm_key = ?;''',
                  [strm_key])
        rows = c.fetchall()
        if (not rows):
            return
        for row in rows:
            string = "     TTX [" + row['lang'] + "] "
            string += teletext_type_string[row['teletext_type']]
            strings.append(string)

    def print_stream(self, service):
        if (self.win is None):
            return
        strings = []

        c = self.connection.cursor()

        c.execute('''select * from streams where svc_key = ?''',
                  [service.svc_key])
        rows = c.fetchall()
        if (not rows):
            return
        for row in rows:
            string = "0x%04x - " % row['pid']
            stream_type = row['stream_type']
            string += self.get_stream_type_string(stream_type)
            string += ")"
            strings.append(string)
            stream_class = row['stream_class']
            strm_key = row['strm_key']
            if (stream_class == dvb.STREAM_CLASS_AUDIO):
                self.add_audio_stream_string(strm_key, strings)
            elif (stream_class == dvb.STREAM_CLASS_DVB_SUBTITLE):
                self.add_dvb_subtitle_stream_string(strm_key, strings)
            elif (stream_class == dvb.STREAM_CLASS_TELETEXT):
                self.add_teletext_stream_string(strm_key, strings)

        x = 1
        min_y = 3
        x_width = 40
        y = min_y
        for string in strings:
            if (y == min_y):
                self.win.addstr(y, x, "PID      stream_type")
                y += 1
            self.win.addstr(y, x, string[0:x_width - 1])
            y += 1
            if (y >= self.height):
                y = min_y
                x += x_width
                if (x > self.width - x_width):
                    break

    def print_event(self, event):
        if (self.win is None):
            return

        # print time and name
        self.win.addstr(3, 16, "evid: %04x" % event.evid)
        self.win.addstr(3, 1, "evt_key: %d" % event.evt_key)

        ts_key = event.ts_key
        time_offset = self.db.read_time_offset(ts_key)
        dt = datetime.utcfromtimestamp(event.start_time + time_offset)
        string = dt.strftime("%Y-%m-%d %a %H:%M:%S")

        string += " (%+d:%02d)" % ((time_offset // 3600),
                                    ((time_offset % 3600) // 60))
        min = int(event.duration() / 60)
        hour = int(min / 60)
        min = min % 60
        string += " (for %02d:%02d)" % (hour, min)
        self.win.addstr(3, 35, string)

        c = self.connection.cursor()
        y = 4

        # print event text
        self.win.addstr(y, 1, "[ %s ]" % event.evt_name)
        y += 1

        if (y >= self.height):
            return

        # print program crid
        prog_crid = ""
        c.execute('''select * from programs where evt_key = ?''',
                  [event.evt_key])
        row = c.fetchone()
        if (row):
            prog_crid = row['prog_crid']
            prog_crid_imi = row['prog_crid']
            if (row['imi']):
                prog_crid_imi += row['imi']
            c.execute('''select count(*) from programs where prog_crid = ?''',
                      [prog_crid])
            row = c.fetchone()
            string = "%s alternative" % row[0]
            if (row[0] > 1):
                string += "s"
            string += " for program crid " + prog_crid_imi
            self.win.addstr(y, 5, string)
            y += 1
            if (y >= self.height):
                return

        # print series crid
        c.execute('''select * from series_crids where evt_key = ?''',
                  [event.evt_key])
        rows = c.fetchall()
        if (not rows):
            rows = []
        crid_strings = []
        for row in rows:
            crid_strings.append(row['series_crid'])

        for series_crid in crid_strings:
            c.execute('''select count(*) from series_crids
                      where series_crids.series_crid = ?''',
                      [series_crid])
            row = c.fetchone()
            string = str(row[0]) + " event"
            if (row[0] > 1):
                string += "s"
            string += " for series crid " + series_crid
            if (len(prog_crid)):
                c.execute('''select count(distinct(prog_crid))
                          from series_crids
                          join programs
                          on series_crids.evt_key = programs.evt_key
                          where series_crids.series_crid = ?''',
                          [series_crid])
                row = c.fetchone()
                string += " (" + str(row[0]) + " program"
                if (row[0] > 1):
                    string += "s"
                string += ")"
            self.win.addstr(y, 5, string)
            y += 1
            if (y >= self.height):
                return

    def print_event_texts(self, event):
        y = 4
        c = self.connection.cursor()
        c.execute('''select lang, evt_name, short_text, extended_text
                  from event_texts where evt_key = ?;''', [event.evt_key])
        rows = c.fetchall()
        if (not rows):
            rows = []
        for row in rows:
            lang = row['lang']
            if (row['evt_name']):
                string = "name    [%s] %s" % (lang, row['evt_name'])
                self.win.addstr(y, 1, string)
                y += 1
                if (y >= self.height):
                    break
            if (row['short_text']):
                self.win.addstr(y, 1, "short   [%s] %s" %
                                (lang, row['short_text']))
                y += 1
                if (y >= self.height):
                    break
            if (row['extended_text']):
                self.win.addstr(y, 1, "extended[%s] %s" %
                                (lang, row['extended_text']))
                y += 1
                if (y >= self.height):
                    break

    def print_svc_table(self, svc_table):
        if (self.win is None):
            return
        pass

    def print_fe(self, fe):
        if (self.win is None):
            return
        self.win.addstr(0, 0, fe.info_str)

        feinfo = fe.get_info()
        is_real_tuner = (feinfo.type == frontend.FE_OFDM
                         or feinfo.type == frontend.FE_QAM
                         or feinfo.type == frontend.FE_QPSK)
        if is_real_tuner:
            string = "[%x" % fe.read_status()
            string += ", BER %x" % fe.read_ber()
            string += ", SNR %x" % fe.read_snr()
            string += ", STRENGTH %x]" % fe.read_signal_strength()
        elif feinfo.type == frontend.FE_FILE:
            string = "[%s]" % fe.ts_file_name
        else:
            return
        self.win.addstr(1, 0, string[0:self.width])
