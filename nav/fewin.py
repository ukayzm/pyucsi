#! /usr/bin/env python

import curses
import linuxdvb
import window
import observer
import logging
import frontend
import install
import os


class FeWin(window.Window, observer.FeObserver):
    def __init__(self):
        window.Window.__init__(self)

        self.logger = logging.getLogger('MainLog')
        self.fe_list = install.FeList()

        frontends = self.fe_list.get_frontends()

        for fe in frontends:
            fe.register_observer(self)

        fe = self.fe_list.get_focused_frontend()
        string = "start with FE %s" % fe.fe_filename
        self.logger.info(string)
        self.scan_param_index = -1

        string = ",  left/right: change FE"
        string += ",  up/down: change scan frequency"
        string += ",  enter: manual scan"
        self.help_string = string

    def refresh(self):
        if (self.win is None):
            return
        fe = self.fe_list.get_focused_frontend()
        self.print_fe_status(fe.read_status())
        self.print_fe_param()
        self.win.refresh()
        window.Window.refresh(self)

    def print_fe_status(self, status):
        if (status & linuxdvb.FE_HAS_LOCK):
            string = "Lck"
        else:
            string = "try"
        self.win.addstr(0, 0, string)

    def get_manual_scan_param(self):
        if (self.scan_param_index == -1):
            return None
        fe = self.fe_list.get_focused_frontend()
        if (len(fe.source.tps_to_scan) <= 0):
            return None
        return fe.source.tps_to_scan[self.scan_param_index]

    def print_fe_param(self):
        attr = 0
        if (self.focused):
            attr |= curses.A_REVERSE
        fe = self.fe_list.get_focused_frontend()
        if (fe.feinfo.type == frontend.FE_FILE):
            if (self.focused == False or self.scan_param_index == -1):
                file_name = fe.ts_file_name
            else:
                tp_to_scan = fe.source.tps_to_scan[self.scan_param_index]
                file_name = tp_to_scan.pathname
            string = os.path.basename(file_name)
        else:
            polarization = -1
            if (self.focused == False or self.scan_param_index == -1):
                param = fe.get_frontend()
                freq = int(param.frequency / 1000)
                if (fe.feinfo.type == frontend.FE_QPSK):
                    freq = fe.get_sat_frequency(freq)
                    polarization = fe.get_polarization()
            else:
                tp = fe.source.tps_to_scan[self.scan_param_index]
                freq = tp.frequency
                if (fe.feinfo.type == frontend.FE_QPSK):
                    polarization = fe.get_polarization()

            if (fe.feinfo.type == frontend.FE_QPSK):
                string = "%6d MHz" % freq
                if (polarization == 0):
                    string += ", H    "
                elif (polarization == 1):
                    string += ", V    "
                else:
                    string += "       "
            else:
                string = "%6d kHz       " % freq
        self.win.addstr(0, 4, string[0:self.width - 5], attr)
        if (fe.feinfo.type == frontend.FE_QPSK):
            string = "LNB %6d MHz   " % fe.source.lo_freq
        else:
            string = "                 "
        self.win.addstr(1, 0, string[0:self.width - 1])

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        fe = self.fe_list.get_focused_frontend()
        self.info_win.print_fe(fe)
        self.info_win.win.refresh()

    def move_left(self):
        frontends = self.fe_list.get_frontends()
        if (len(frontends) < 2):
            return
        fe = self.fe_list.get_focused_frontend()
        fe_index = frontends.index(fe)
        fe_index -= 1
        fe_index %= len(frontends)
        fe = frontends[fe_index]
        self.fe_list.set_focused_frontend(fe)
        self.scan_param_index = self.guess_scan_param_index()
        self.refresh()

    def move_right(self):
        frontends = self.fe_list.get_frontends()
        if (len(frontends) < 2):
            return
        fe = self.fe_list.get_focused_frontend()
        fe_index = frontends.index(fe)
        fe_index += 1
        fe_index %= len(frontends)
        fe = frontends[fe_index]
        self.fe_list.set_focused_frontend(fe)
        self.scan_param_index = self.guess_scan_param_index()
        self.refresh()

    def guess_scan_param_index(self):
        fe = self.fe_list.get_focused_frontend()
        if (len(fe.source.tps_to_scan) <= 0):
            return -1
        fe_type = fe.feinfo.type
        if (fe_type == frontend.FE_FILE):
            cur_param = fe.ts_file_name
            try:
                param_index = fe.source.tps_to_scan.index(cur_param)
            except:
                return 0
            return param_index
        elif (fe_type == frontend.FE_QPSK):
            cur_freq = int(fe.get_frontend().frequency / 1000)
            polarization = fe.get_polarization()
            for param in fe.source.tps_to_scan:
                if (cur_freq == param.frequency and
                    polarization == param.pozarization):
                    return fe.source.tps_to_scan.index(param)
        else:
            cur_freq = int(fe.get_frontend().frequency / 1000)
            for param in fe.source.tps_to_scan:
                if (cur_freq == param.frequency):
                    return fe.source.tps_to_scan.index(param)
        return 0

    def move_up(self):
        if (self.scan_param_index == -1):
            return
        fe = self.fe_list.get_focused_frontend()
        self.scan_param_index -= 1
        self.scan_param_index %= len(fe.source.tps_to_scan)
        self.refresh()

    def move_down(self):
        if (self.scan_param_index == -1):
            return
        fe = self.fe_list.get_focused_frontend()
        self.scan_param_index += 1
        self.scan_param_index %= len(fe.source.tps_to_scan)
        self.refresh()

    def set_focus(self):
        self.scan_param_index = self.guess_scan_param_index()
        window.Window.set_focus(self)

    def update(self, fe, event):
        if (self.win is None):
            return
        if (fe.feinfo.type == frontend.FE_FILE):
            string = fe.ts_file_name
        else:
            fe_freq = int(event.parameters.frequency / 1000)
            if (fe.feinfo.type == frontend.FE_QPSK):
                lo_freq = fe.source.lo_freq
                sat_freq = fe.get_sat_frequency(fe_freq)
                string = str(sat_freq) + " MHz"
                string += " (lo_freq: %d MHz" % fe.source.lo_freq
                string += ", fe_freq: %d MHz)" % fe_freq
            else:
                string = str(fe_freq) + " kHz"
        string += " (%02x) - " % event.status
        if (event.status & frontend.FE_LOOPED):
            string += "looped"
        elif (event.status & linuxdvb.FE_HAS_LOCK):
            string += "Locked"
        elif (event.status & linuxdvb.FE_REINIT):
            string += "try"
        else:
            string += "no signal"
        self.logger.info(string)
        self.print_fe_status(event.status)
        self.print_fe_param()
        self.win.refresh()

