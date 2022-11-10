#! /usr/bin/env python

import curses
import window
import observer
import logging
import dvbsi
import binascii
import si_print
import datetime

class Utc(datetime.tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=0)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "UTC"

class SiWin(window.Window, observer.SvcObserver, observer.SiObserver):
    def __init__(self):
        window.Window.__init__(self)
        self.win = None
        self.logger = logging.getLogger('MainLog')
        self.focused_table = 0
        self.si_collector = None

        string = ",  up/down: change table"
        string += ",  enter: print table"
        self.help_string = string

    def set_si_collector(self, si_collector):
        self.si_collector = si_collector
        self.si_collector.register_observer(self)
        self.refresh()

    def refresh(self):
        if (self.win is None):
            return
        if (self.si_collector):
            self.print_collector_status()
        self.win.refresh()
        window.Window.refresh(self)

    def print_collector_status(self):
        attr = 0
        if (self.focused and self.focused_table == 0):
            attr |= curses.A_REVERSE
        string = "PAT "
        if (hasattr(self.si_collector.pat, 'demux')):
            get, toget = self.si_collector.pat.get_progress()
            string += "%2d/%d " % (get, toget)
        else:
            string += "      "
        self.win.addstr(0, 0, string, attr)

        attr = 0
        if (self.focused and self.focused_table == 1):
            attr |= curses.A_REVERSE
        string = "PMT "
        if (hasattr(self.si_collector.pmt, 'demux')):
            get, toget = self.si_collector.pmt.get_progress()
            string += "%2d/%d " % (get, toget)
        else:
            string += "      "
        self.win.addstr(1, 0, string, attr)

        attr = 0
        if (self.focused and self.focused_table == 2):
            attr |= curses.A_REVERSE
        string = "SDT "
        if (hasattr(self.si_collector.sdt_act, 'demux')):
            get, toget = self.si_collector.sdt_act.get_progress()
            string += "%2d/%d " % (get, toget)
        else:
            string += "      "

        if (hasattr(self.si_collector.sdt_oth, 'demux')):
            get, toget = self.si_collector.sdt_oth.get_progress()
            string += ", %2d/%d " % (get, toget)
        else:
            string += "        "
        self.win.addstr(2, 0, string, attr)

        attr = 0
        if (self.focused and self.focused_table == 3):
            attr |= curses.A_REVERSE
        string = "NIT "
        if (hasattr(self.si_collector.nit_act, 'demux')):
            get, toget = self.si_collector.nit_act.get_progress()
            string += "%2d/%d " % (get, toget)
        else:
            string += "      "

        if (hasattr(self.si_collector.nit_oth, 'demux')):
            get, toget = self.si_collector.nit_oth.get_progress()
            string += ", %2d/%d " % (get, toget)
        else:
            string += "        "
        self.win.addstr(3, 0, string, attr)

        attr = 0
        if (self.focused and self.focused_table == 4):
            attr |= curses.A_REVERSE
        string = "BAT "
        if (hasattr(self.si_collector.bat, 'demux')):
            get, toget = self.si_collector.bat.get_progress()
            string += "%2d/%d " % (get, toget)
        else:
            string += "      "
        self.win.addstr(4, 0, string, attr)

        attr = 0
        if (self.focused and self.focused_table == 5):
            attr |= curses.A_REVERSE
        string = "TDT "
        if (self.si_collector.tdt_section):
            utc_time = self.si_collector.tdt_section.utc_time
            dt = dvbsi.dvbdate_to_datetime(utc_time)
            string += "%02d%02d%02d %02d:%02d:%02d" % (
                dt.year % 100, dt.month, dt.day,
                dt.hour, dt.minute, dt.second)
        else:
            string += "        "
        self.win.addstr(5, 0, string[0:self.width], attr)

        attr = 0
        if (self.focused and self.focused_table == 6):
            attr |= curses.A_REVERSE
        string = "TOT "
        if (self.si_collector.tot_section):
            offstring = "       "
            td = datetime.timedelta(0)
            for dsc in self.si_collector.tot_section.descriptors:
                if dsc.tag == dvbsi.DTAG_LOCAL_TIME_OFFSET:
                    # TODO: check country code and region id
                    lto_dsc = dvbsi.LocalTimeOffsetDescriptor(dsc.data)
                    if (len(lto_dsc.entries) == 0):
                        break
                    lto = lto_dsc.entries[0]
                    hour = dvbsi.bcd_to_integer(lto.local_time_offset[0])
                    minute = dvbsi.bcd_to_integer(lto.local_time_offset[1])
                    offset = hour * 60 + minute
                    if (lto.local_time_offset_polarity == 1):
                        offstring = "-"
                        td = datetime.timedelta(minutes=-offset)
                    else:
                        offstring = "+"
                        td = datetime.timedelta(minutes=offset)
                    offstring += "%02d:%02d " % (hour, minute)
                    break
            string += offstring

            utc_time = self.si_collector.tot_section.utc_time
            dt = dvbsi.dvbdate_to_datetime(utc_time) + td
            string += "%02d:%02d:%02d" % (dt.hour, dt.minute, dt.second)
        else:
            string += "        "
        self.win.addstr(6, 0, string[0:self.width], attr)

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        self.info_win.win.refresh()

    def print_sections(self):
        if (self.focused_table == 0):
            sections = self.si_collector.pat.get_sections()
        elif (self.focused_table == 1):
            sections = self.si_collector.pmt.get_sections()
        elif (self.focused_table == 2):
            sections = self.si_collector.sdt_act.get_sections()
            sections += self.si_collector.sdt_oth.get_sections()
        elif (self.focused_table == 3):
            sections = self.si_collector.nit_act.get_sections()
            sections += self.si_collector.nit_oth.get_sections()
        elif (self.focused_table == 4):
            sections = self.si_collector.bat.get_sections()
        elif (self.focused_table == 5):
            if (self.si_collector.tdt_section == None):
                return
            sections = [self.si_collector.tdt_section]
        elif (self.focused_table == 6):
            if (self.si_collector.tot_section == None):
                return
            sections = [self.si_collector.tot_section]
        else:
            return

        for section in sections:
            si_print.print_section(section)

    def move_up(self):
        self.focused_table -= 1
        self.focused_table %= 7
        self.refresh()

    def move_down(self):
        self.focused_table += 1
        self.focused_table %= 7
        self.refresh()

    def on_section(self, si_collector, result, section, sub_table, table):
        self.refresh()

