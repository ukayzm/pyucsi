#! /usr/bin/env python3


import dvbsi
import linuxdvb
from datetime import datetime


NETWORK_TYPE_SATELLITE = 0
NETWORK_TYPE_CABLE = 1
NETWORK_TYPE_TERRESTRIAL = 2
NETWORK_TYPE_FILE = 8
NETWORK_TYPE_UNKNOWN = 9


AUDIO_CODEC_MPEG_MONO_LEFT = 1
AUDIO_CODEC_MPEG_MONO_RIGHT = 2
AUDIO_CODEC_MPEG_STEREO = 3
AUDIO_CODEC_AC3 = 4
AUDIO_CODEC_E_AC3 = 5
AUDIO_CODEC_DTS = 6
AUDIO_CODEC_AAC = 7
AUDIO_CODEC_HE_AAC_V1 = 8
AUDIO_CODEC_HE_AAC_V2 = 9


STREAM_CLASS_UNCLASSIFIED = 0
STREAM_CLASS_VIDEO = 1
STREAM_CLASS_AUDIO = 2
STREAM_CLASS_DVB_SUBTITLE = 3
STREAM_CLASS_TELETEXT = 4


class Event():
    def __init__(self, evt_key, evid, start_time, end_time, evt_name,
                 svc_key, svc_name, ts_key, description=""):
        self.start_time = start_time
        self.end_time = end_time
        self.evt_name = evt_name
        self.svc_key = svc_key
        self.svc_name = svc_name
        self.ts_key = ts_key
        self.evt_key = evt_key
        self.evid = evid
        self.description = description
        self.prog_crid = ""
        self.season = 0
        self.episode = 0
        self.total_episodes = 0
        self.imi = ""
        self.split_number = 1
        self.total_splits = 1
        self.series_crids = []
        self.time_offset = 0    # just for testing...

    def mean_time(self):
        return int((self.start_time + self.end_time) / 2)

    def duration(self):
        return self.end_time - self.start_time

    def __eq__(self, other):
        return self.evt_key == other.evt_key

    def __str__(self):
        string = "event[%d] %s" % (self.evt_key, self.evt_name)
        if (self.episode):
            string += ", ep %d" % self.episode
            if (self.total_episodes):
                string += " of %d" % self.total_episodes
        if (self.season):
            string += ", season %d" % self.season
        if (self.total_splits > 1):
            string += ", split %d/%d" % (self.split_number, self.total_splits)
        if len(self.prog_crid) or len(self.imi):
            string += " ["
            string += "%s" % self.prog_crid
            string += " %s" % self.imi
            string += "]"
        string += " (%s" % self.svc_name
        string += ", evid 0x%04x" % self.evid
        dt = datetime.utcfromtimestamp(self.start_time + self.time_offset)
        string += dt.strftime(", %a %d %b %H:%M")
        dt = datetime.utcfromtimestamp(self.end_time + self.time_offset)
        string += dt.strftime(" - %H:%M")
        string += ")"
        return string


class Service():
    def __init__(self, svc_key, lcn, svc_name, prov_name, _type,
                 tsid, onid, svid, ts_key, src_key, delivery_system):
        self.svc_key = svc_key
        if (lcn is None):
            lcn = 0
        if (svc_name is None):
            svc_name = "%04x.%04x.%04x" % (onid, tsid, svid)
        if (prov_name is None):
            prov_name = ""
        self.lcn = lcn
        self.svc_name = svc_name
        self.prov_name = prov_name
        self._type = _type
        self.tsid = tsid
        self.onid = onid
        self.svid = svid
        self.ts_key = ts_key
        self.src_key = src_key
        self.delivery_system = delivery_system

    def __str__(self):
        string = str(self.lcn) + ". " + self.svc_name
        return string

    def detail_string(self):
        string = 'svc[%d] ' % self.svc_key
        if (self.delivery_system == NETWORK_TYPE_SATELLITE):
            string += "S"
        elif (self.delivery_system == NETWORK_TYPE_CABLE):
            string += "C"
        elif (self.delivery_system == NETWORK_TYPE_TERRESTRIAL):
            string += "T"
        elif (self.delivery_system == NETWORK_TYPE_FILE):
            string += "F"
        else:
            string += "?"
        string += " %04x.%04x.%04x" % (self.onid, self.tsid, self.svid)
        string += ' ' + self.__str__()
        string += '  [ts_key %d, src_key %d]' % (self.ts_key, self.src_key)
        return string


class Source:
    def __init__(self, src_key, delivery_system, src_name):
        self.src_key = src_key
        self.delivery_system = delivery_system
        self.src_name = src_name
        self.tps_to_scan = []

    def __str__(self):
        return self.src_name


class SatSource(Source):
    def __init__(self, src_key, delivery_system, orbital_position, src_name):
        Source.__init__(self, src_key, delivery_system, src_name)
        self.lo_freq = 0
        self.lo_freq2 = 0
        self.num_output = 0
        self.with_motor = 0
        self.lnb_name = ""
        self.link_type = 0
        self.diseqc_version = 0
        self.continuous_tone = 0
        self.orbital_position = orbital_position

    def __str__(self):
        type_name = ["LNB", "DiSEqC A", "DiSEqC B", "DiSEqC C", "DiSEqC D"]
        string = type_name[self.link_type]
        string += ", 22 kHz tone "
        if (self.continuous_tone == 0):
            string += "OFF"
        else:
            string += "ON"
        string += ", lo %d" % self.lo_freq
        if (self.lo_freq2 != 0):
            string += ", %d" % self.lo_freq2
        string += " MHz"
        string += ", " + self.src_name
        return string


class Transport():
    def __init__(self, ts_key, src_key, nid=0, onid=0, tsid=0):
        self.ts_key = ts_key
        self.src_key = src_key
        self.nid = nid
        self.tsid = tsid
        self.onid = onid
        self.ts_name = "void transport"
        self.time_offset = 0
        self.tag = 0
        self.length = 0
        self.data = ""

    def is_the_same_as(self, ts):
        return False

    def __str__(self):
        return self.ts_name


class TsTer(dvbsi.TerrestrialDeliverySystemDescriptor, Transport):
    def __init__(self, ts_key, src_key, nid=0, onid=0, tsid=0):
        Transport.__init__(self, ts_key, src_key, nid, onid, tsid)
        self.tag = dvbsi.DTAG_TERRESTRIAL_DELIVERY_SYSTEM
        self.frequency = 0
        self.bandwidth = 0
        self.code_rate_hp_stream = 7
        self.code_rate_lp_stream = 7
        self.constellation = 3
        self.transmission_mode = 3
        self.guard_interval = 4
        self.hierarchy_information = 0
        self.priority = 0
        self.time_slicing_indicator = 0
        self.mpe_fec_indicator = 0
        self.reserved1 = 0
        self.other_frequency_flag = 0
        self.reserved2 = 0

    def set_tuning_param(self, freq, bandwidth, code_rate_HP=7,
                         code_rate_LP=7, constellation=3,
                         transmission_mode=3, guard_interval=4,
                         hierarchy_information=0):
        self.frequency = freq
        self.bandwidth = bandwidth
        self.code_rate_hp_stream = code_rate_HP
        self.code_rate_lp_stream = code_rate_LP
        self.constellation = constellation
        self.transmission_mode = transmission_mode
        self.guard_interval = guard_interval
        self.hierarchy_information = hierarchy_information

    def copy_tuning_param(self, dsc):
        self.frequency = dsc.frequency
        self.bandwidth = dsc.bandwidth
        self.priority = dsc.priority
        self.time_slicing_indicator = dsc.time_slicing_indicator
        self.mpe_fec_indicator = dsc.mpe_fec_indicator
        self.other_frequency_flag = dsc.other_frequency_flag
        self.code_rate_hp_stream = dsc.code_rate_HP
        self.code_rate_lp_stream = dsc.code_rate_LP
        self.constellation = dsc.constellation
        self.transmission_mode = dsc.transmission_mode
        self.guard_interval = dsc.guard_interval
        self.hierarchy_information = dsc.hierarchy_information

    def is_the_same_as(self, ts):
        if (self.src_key != ts.src_key):
            return False
        if (self.frequency != ts.frequency):
            return False
        return True

    def __str__(self):
        bw_str = linuxdvb.fe_bandwidth[self.bandwidth]
        return "%6d kHz, %s" % (self.frequency, bw_str[10:])

    def detail_param_str(self):
        return dvbsi.TerrestrialDeliverySystemDescriptor.__str__(self)


class TsSat(dvbsi.SatelliteDeliverySystemDescriptor, Transport):
    def __init__(self, ts_key, src_key, nid=0, onid=0, tsid=0):
        Transport.__init__(self, ts_key, src_key, nid, onid, tsid)
        self.tag = dvbsi.DTAG_SATELLITE_DELIVERY_SYSTEM
        self.frequency = 0
        self.fec_inner = 0
        self.symbol_rate = 0
        self.orbital_position = 0
        self.polarization = 4
        self.roll_off = 0
        self.modulation_system = 0
        self.modulation_type = 0

    def set_tuning_param(self, freq, polarization, symbol_rate, fec_inner,
                         modulation_system, orbital_position):
        self.frequency = freq
        if (fec_inner is None or fec_inner < 1 or fec_inner >= 10):
            self.fec_inner = 0
        else:
            self.fec_inner = fec_inner
        self.modulation_system = modulation_system
        self.symbol_rate = symbol_rate
        self.polarization = polarization

    def copy_tuning_param(self, dsc):
        self.frequency = dsc.frequency
        self.fec_inner = dsc.fec_inner
        self.modulation_system = dsc.modulation_system
        self.symbol_rate = dsc.symbol_rate
        self.orbital_position = dsc.orbital_position
        self.polarization = dsc.polarization
        self.roll_off = dsc.roll_off
        self.modulation_system = dsc.modulation_system
        self.modulation_type = dsc.modulation_type

    def is_the_same_as(self, ts):
        if (self.src_key != ts.src_key):
            return False
        if (self.frequency != ts.frequency):
            return False
        if (self.polarization != ts.polarization):
            return False
        if (self.orbital_position != ts.orbital_position):
            return False
        return True

    def __str__(self):
        fec_inner_str = [
            "0(?)", "1/2", "2/3", "3/4",
            "5/6", "7/8", "8/9", "3/5",
            "4/5", "9/10", "10(?)", "11(?)",
            "12(?)", "13(?)", "14(?)", "15(?)"]

        string = str(self.frequency) + " MHz, "
        if (self.polarization is 0):
            string += "H"
        elif (self.polarization is 1):
            string += "V"
        elif (self.polarization is 2):
            string += "L"
        elif (self.polarization is 3):
            string += "R"
        string += ", " + str(self.symbol_rate) + ", "
        string += fec_inner_str[self.fec_inner] + ", DVB-S"
        if (self.modulation_system is 1):
            string += "2"
        return string


class TsFile(Transport):
    def __init__(self, ts_key, src_key, nid=0, onid=0, tsid=0):
        Transport.__init__(self, ts_key, src_key, nid, onid, tsid)
        self.pathname = ""

    def is_the_same_as(self, ts):
        if (self.src_key != ts.src_key):
            return False
        if (self.pathname != ts.pathname):
            return False
        return True

    def __str__(self):
        return self.pathname


class RsvLink():
    def __init__(self, rsv_key, sched_key, pathname):
        self.rsv_key = rsv_key
        self.sched_key = sched_key
        self.pathname = pathname

    def __eq__(self, other):
        if self.rsv_key != other.rsv_key:
            return False
        if self.sched_key != other.sched_key:
            return False
        return True


class Schedule():
    STATUS_STRING = ['scheduled', 'refused', 'ready', 'pending',
                     'running', 'completed', 'incomplete', 'failed']

    def __init__(self, sched_name, action, start_time, end_time):
        self.sched_key = 0
        self.sched_name = sched_name
        self.description = ""
        self.action = action
        self.start_time = start_time
        self.end_time = end_time
        self.status = 0
        self.actual_start_time = 0
        self.running_time = 0
        self.error = 0
        self.svc_key = 0
        self.svc_name = ""
        self.evid = 0
        self.prog_crid = ""
        self.season = 0
        self.episode = 0
        self.total_episodes = 0
        self.imi = ""
        self.split_number = 1
        self.total_splits = 1
        self.conflict = 0
        self.start_padding = 0
        self.end_padding = 0
        self.rsv_links = []
        self.time_offset = 0    # just for testing...

    def __str__(self):
        string = "sched[%d]" % self.sched_key
        string += " " + Reservation.ACTION_STR[self.action]
        string += " <"
        #string += " <svc_key %d, " % self.svc_key
        dt = datetime.utcfromtimestamp(self.start_time + self.time_offset)
        string += dt.strftime("%a %d %b ")
        string += "(-%d) " % (self.start_padding // 60)
        string += dt.strftime("%H:%M")
        string += " - "
        dt = datetime.utcfromtimestamp(self.end_time + self.time_offset)
        string += dt.strftime("%H:%M")
        string += " (+%d)" % (self.end_padding // 60)
        if (len(self.svc_name)):
            string += ", %s>" % self.svc_name
        else:
            string += ", svc_key %d>" % self.svc_key
        string += ", " + self.sched_name
        if (self.episode):
            string += ", ep %d" % self.episode
            if (self.total_episodes):
                string += " of %d" % self.total_episodes
        if (self.season):
            string += ", season %d" % self.season
        if (self.total_splits > 1):
            string += ", split %d/%d" % (self.split_number, self.total_splits)
        if len(self.imi):
            string += " [%s]" % self.imi
        string += ", %s" % self.STATUS_STRING[self.status]
        if (len(self.rsv_links)):
            string += ", referred by"
        for link in self.rsv_links:
            string += " rsv[" + str(link.rsv_key) + "]"
        return string

    def duration(self):
        return self.end_time - self.start_time

    def is_commonly_overlapping_with(self, others):
        '''returns True if this event and all others passed by parameter
        share the same period of overlapping'''
        start_time = self.start_time
        end_time = self.end_time
        for other in others:
            cond = other.is_overlapping_with_period(start_time, end_time)
            if (cond is False):
                return False
            if (start_time < other.start_time):
                start_time = other.start_time
            if (other.end_time < end_time):
                end_time = other.end_time
        return True

    def is_overlapping_with(self, other):
        ret = self.is_overlapping_with_period(other.start_time, other.end_time)
        return ret

    def is_overlapping_with_period(self, start_time, end_time):
        if (self.start_time < end_time and start_time < self.end_time):
            return True
        return False

    def is_near_to(self, other, how_near=10800):
        e1 = other.end_time + how_near
        e2 = self.end_time + how_near
        if (self.start_time < e1 and other.start_time < e2):
            return True
        return False

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __eq__(self, other):
        return self.start_time == other.start_time


class Reservation():
    ACTION_STR = ["",
                  "turn on into standby mode",
                  "turn on into operation mode",
                  "enter into standby mode",
                  "",
                  "",
                  "",
                  "",
                  "",
                  "",
                  "watch",
                  "record",
                  "update channel list",
                  "collect EIT",
                  "update S/W (OTA)",
                  "notify to user",
                  "refresh current time",
                  "update EMM",
                  "execute installation wizard"]

    ACTION_TURN_ON_INTO_STANDBY = 1
    ACTION_TURN_ON_INTO_OPERATION = 2
    ACTION_ENTER_INTO_STANDBY = 3
    ACTION_WATCH = 10
    ACTION_RECORD = 11

    TARGET_STR = ["", "service", "event", "kerword", "program CRID",
                  "series CRID"]

    TARGET_NONE = 0
    TARGET_SERVICE = 1
    TARGET_EVENT = 2
    TARGET_KEYWORD = 3
    TARGET_PROGRAM_CRID = 4
    TARGET_SERIES_CRID = 5

    def __init__(self, rsv_name, action):
        self.rsv_key = 0
        self.deactivated = 0
        self.rsv_name = rsv_name
        self.description = ""
        self.action = action
        self.target = 0
        self.svc_key = 0
        self.svc_name = ""
        self.evid = 0
        self.do_when = 0
        self.replan_when = 0
        self.booked_time = 0
        self.priority = 0
        self.directory = ""
        self.rsv_links = []

    def refer_string(self):
        string = ""
        if (len(self.rsv_links)):
            string += ", refers to"
        for link in self.rsv_links:
            string += " sched[" + str(link.sched_key) + "]"
        return string

    def basic_string(self):
        string = "rsv[%d] " % self.rsv_key
        string += self.rsv_name
        string += ", " + self.ACTION_STR[self.action]
        string += " " + self.TARGET_STR[self.target]
        if (self.do_when == 3):
            string += " on standby"
        elif (self.do_when == 4):
            string += " on operation"
        return string

    def __str__(self):
        string = self.basic_string()
        string += self.refer_string()
        return string


class ReservationDaily(Reservation):
    def __init__(self, rsv_name, action, yyyymmdd, hhmmss, duration,
                 day_of_week=0):
        Reservation.__init__(self, rsv_name, action)
        self.yyyymmdd = yyyymmdd
        self.hhmmss = hhmmss
        self.duration = duration
        self.day_of_week = day_of_week
        self.do_when = 1
        self.replan_when = 0x1 | 0x80

    def __str__(self):
        string = self.basic_string()
        if (len(self.svc_name)):
            string += " <%s>" % self.svc_name
        else:
            string += " <svc_key %d>" % self.svc_key
        string += " at %d" % (self.hhmmss // 10000)
        string += ":%02d" % ((self.hhmmss // 100) % 100)
        string += ":%02d" % (self.hhmmss % 100)
        if (self.duration):
            string += " for %d" % (self.duration // 3600)
            string += ":%02d" % ((self.duration // 60) % 60)
            string += ":%02d" % (self.duration % 60)
        if (self.yyyymmdd):
            string += " from %d" % (self.yyyymmdd // 10000)
            string += "-%02d" % ((self.yyyymmdd // 100) % 100)
            string += "-%02d" % (self.yyyymmdd % 100)
        if (self.day_of_week == 0x41):
            string += " on weekend"
        elif (self.day_of_week == 0x3e):
            string += " on weekday"
        elif (self.day_of_week == 0x7f):
            string += " on everyday"
        elif (self.day_of_week != 0):
            string += " on"
            if (self.day_of_week & 0x01):
                string += " Sun"
            if (self.day_of_week & 0x02):
                string += " Mon"
            if (self.day_of_week & 0x04):
                string += " Tue"
            if (self.day_of_week & 0x08):
                string += " Wed"
            if (self.day_of_week & 0x10):
                string += " Thu"
            if (self.day_of_week & 0x20):
                string += " Fri"
            if (self.day_of_week & 0x40):
                string += " Sat"
        string += self.refer_string()
        return string


class TBW(ReservationDaily):
    def __init__(self, rsv_name, svc_key, yyyymmdd, hhmmss, duration,
                 day_of_week=0):
        ReservationDaily.__init__(self, rsv_name, Reservation.ACTION_WATCH,
                                  yyyymmdd, hhmmss, duration, day_of_week)
        self.svc_key = svc_key
        self.target = self.TARGET_SERVICE


class TBR(ReservationDaily):
    def __init__(self, rsv_name, svc_key, yyyymmdd, hhmmss, duration,
                 day_of_week=0):
        ReservationDaily.__init__(self, rsv_name, Reservation.ACTION_RECORD,
                                  yyyymmdd, hhmmss, duration, day_of_week)
        self.svc_key = svc_key
        self.target = self.TARGET_SERVICE


class ReservationEvent(Reservation):
    def __init__(self, rsv_name, action, svc_key, evid):
        Reservation.__init__(self, rsv_name, action)
        self.target = self.TARGET_EVENT
        self.svc_key = svc_key
        self.evid = evid
        self.do_when = 0
        self.replan_when = 0x1 | 0x10 | 0x80

    def __str__(self):
        string = self.basic_string()
        if (len(self.svc_name)):
            string += " <%s" % self.svc_name
        else:
            string += " <svc_key %d" % self.svc_key
        string += ", evid 0x%04x>" % self.evid
        string += self.refer_string()
        return string


class EBR(ReservationEvent):
    def __init__(self, rsv_name, svc_key, evid):
        ReservationEvent.__init__(self, rsv_name, Reservation.ACTION_RECORD,
                                  svc_key, evid)


class EBW(ReservationEvent):
    def __init__(self, rsv_name, svc_key, evid):
        ReservationEvent.__init__(self, rsv_name, Reservation.ACTION_WATCH,
                                  svc_key, evid)


class PBR(Reservation):
    def __init__(self, rsv_name, svc_key, evid, prog_crid):
        Reservation.__init__(self, rsv_name, Reservation.ACTION_RECORD)
        self.target = self.TARGET_PROGRAM_CRID
        self.svc_key = svc_key
        self.evid = evid
        self.prog_crid = prog_crid
        self.replan_when = 0x1 | 0x10 | 0x80

    def __str__(self):
        string = self.basic_string()
        string += " <" + self.prog_crid + ">"
        if (len(self.svc_name)):
            string += ", <%s" % self.svc_name
        else:
            string += ", <svc_key %d" % self.svc_key
        string += ", evid 0x%04x> is preferred" % self.evid
        string += self.refer_string()
        return string


class SBR(Reservation):
    def __init__(self, rsv_name, svc_key, evid, series_id):
        Reservation.__init__(self, rsv_name, Reservation.ACTION_RECORD)
        self.target = self.TARGET_SERIES_CRID
        self.svc_key = svc_key
        self.evid = evid
        self.series_id = series_id
        self.replan_when = 0x1 | 0x10 | 0x80
        self.max_space = 0
        self.del_day = 0
        self.del_number = 0
        self.del_space = 0
        self.del_played_first = 0

    def __str__(self):
        string = self.basic_string()
        string += " <%s>" % self.series_id
        if (len(self.directory)):
            string += " to directory [%s]" % self.directory
        if (len(self.svc_name)):
            string += ", %s is preferred" % self.svc_name
        elif (self.svc_key):
            string += ", svc_key %d is preferred" % self.svc_key
        if (self.del_day or self.del_number or self.del_space):
            string += ", will be deleted"
            if (self.del_day):
                string += " after "
                if (self.del_day == 1):
                    string += "1 day"
                else:
                    string += "%d days" % self.del_day
            if (self.del_number):
                if (self.del_day == 0):
                    string += " after "
                else:
                    string += " or "
                if (self.del_number == 1):
                    string += "1 episode"
                else:
                    string += "%d episodes" % self.del_number
            if (self.del_space):
                if (self.del_day or self.del_number):
                    string += " or"
                string += " when < %d MB free" % self.del_space
                if (self.max_space):
                    string += " out of %d MB" % self.max_space
                else:
                    string += " in entire HDD"
        string += self.refer_string()
        return string


if __name__ == "__main__":
    event = Event(1, 0xbeef, 12345678, 12345678 + 4800, "World News 9",
                  1, "BBC world", 1)
    event.season = 3
    event.episode = 5
    event.total_episodes = 18
    event.imi = "#1"
    event.split_number = 1
    event.total_splits = 2
    print(event)

    sched = Schedule("Game of Thrones", Reservation.ACTION_RECORD,
                     12345678, 12345678 + 4800)
    sched.sched_key = 12
    sched.svc_key = 1
    sched.start_padding = 3 * 60
    sched.end_padding = 5 * 60
    print(sched)
    sched.episode = 4
    sched.status = 1
    print(sched)
    sched.start_padding = 0
    sched.status = 2
    print(sched)
    sched.season = 2
    sched.end_padding = 0
    sched.status = 3
    print(sched)
    sched.start_padding = 3 * 60
    sched.status = 4
    print(sched)
    sched.imi = "#2"
    sched.status = 5
    print(sched)
    sched.total_episodes = 8
    sched.status = 6
    print(sched)
    sched.season = 0
    sched.total_splits = 2
    sched.status = 7
    print(sched)

    ebw = EBW("Lost", 5, 0xdeed)
    ebw.rsv_key = 8
    print(ebw)

    ebr = EBR("Lost", 5, 0xdeed)
    ebr.rsv_key = 7
    print(ebr)

    pbr = PBR("Lost", 5, 0xdeed, "prog.test.com/deed")
    pbr.rsv_key = 7
    print(pbr)

    sbr = SBR("Flash forward", 3, 0xdeed, "series.test.com/1234")
    sbr.rsv_key = 5
    sbr.del_played_first = 1
    sbr.directory = "/videos/Flash forward_00"
    print(sbr)
    sbr.del_space = 1
    print(sbr)
    sbr.del_space = 0
    sbr.del_number = 10
    print(sbr)
    sbr.del_day = 5
    print(sbr)
    sbr.del_space = 1
    print(sbr)
    sbr.max_space = 1024 * 20
    print(sbr)

    tbw = TBW("time-based watching", 4, 0, 123456, 3600)
    tbw.rsv_key = 5
    print(tbw)
    tbw.day_of_week = 0x3e
    print(tbw)

    tbr = TBR("time-based recording", 4, 0, 123456, 3600)
    tbr.rsv_key = 9
    print(tbr)
    tbr.duration = 0
    print(tbr)
    tbr.yyyymmdd = 20131014
    print(tbr)
    tbr.day_of_week = 0x3e
    print(tbr)
    tbr.day_of_week = 0x1
    print(tbr)
    tbr.day_of_week |= 0x1 << 6
    print(tbr)
    tbr.day_of_week |= 0x2
    print(tbr)
    tbr.day_of_week |= 0x8
    print(tbr)
    tbr.day_of_week = 0x7f
    print(tbr)
