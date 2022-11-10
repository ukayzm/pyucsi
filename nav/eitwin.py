#! /usr/bin/env python

import curses
import window
import observer
import si_print


class EitWin(window.Window, observer.SvcObserver):
    def __init__(self, svc_list):
        window.Window.__init__(self)
        self.eit_collector = None
        self.services = []
        self.cur_service = None
        self.svc_list = svc_list
        self.svc_list.register_observer(self)

        string = ",  up/down: change service"
        string += ",  enter: print EIT"
        self.help_string = string

    def set_eit_collector(self, eit_collector):
        self.eit_collector = eit_collector

    def refresh(self):
        if (self.win is None):
            return
        if (self.eit_collector is None):
            return
        self.print_eit_status()
        self.win.refresh()
        window.Window.refresh(self)

    def update(self, svc_list, services, cur_service):
        self.services = services
        self.cur_service = cur_service
        self.refresh()

    def print_eit_status(self):
        get, toget = self.eit_collector.eit_sch.get_progress()
        string = "%4d/%d        " % (get, toget)
        self.win.addstr(0, 0, string[0:self.width - 1])

        if (len(self.services) == 0):
            return

        y = 1
        for service in self.services:
            attr = 0
            svc_table_key = (service.svid, service.tsid, service.onid)
            svc_table = self.eit_collector.eit_sch.get_svc_table(svc_table_key)
            if (svc_table == None):
                string = "          "
            else:
                get, toget = svc_table.get_progress()
                string = "%4d/%d        " % (get, toget)
            if (self.cur_service == service):
                if (self.focused):
                    attr |= curses.A_REVERSE
            self.win.addstr(y, 0, string[0:self.width - 1], attr)
            y += 1

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        if (self.cur_service):
            self.info_win.print_ts(self.cur_service)
            self.info_win.print_service(self.cur_service)
            service = self.cur_service
            svc_table_key = (service.svid, service.tsid, service.onid)
            svc_table = self.eit_collector.eit_sch.get_svc_table(svc_table_key)
            if (svc_table):
                self.info_win.print_svc_table(svc_table)
        self.info_win.win.refresh()

    def move_down(self):
        self.svc_list.move_down()

    def move_up(self):
        self.svc_list.move_up()

    def print_sections(self):
        if (self.cur_service is None):
            return
        service = self.cur_service
        svc_table_key = (service.svid, service.tsid, service.onid)
        svc_table = self.eit_collector.eit_sch.get_svc_table(svc_table_key)
        if (svc_table is None):
            return
        sections = svc_table.get_sections()
        for section in sections:
            si_print.print_section(section)

    def print_all_sections(self):
        sections = self.eit_collector.eit_sch.get_sections()
        for section in sections:
            si_print.print_section(section)

