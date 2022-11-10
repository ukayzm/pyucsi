#! /usr/bin/env python

import window
import observer
import curses
import dvb
import logging
import db_center


class SvcWin(window.Window, observer.SvcObserver):
    def __init__(self, svc_list):
        window.Window.__init__(self)
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.logger = logging.getLogger('MainLog')
        self.services = []
        self.cur_service = None
        self.svc_list = svc_list
        self.svc_list.register_observer(self)

        string = ", s: scan"
        string += ", S: scan_other"
        string += ", jk: change service"
        string += ", enter: tune"
        self.help_string = string

    def read_screen_info(self):
        height, width = self.win.getmaxyx()
        self.height = height - 1
        self.width = width

    def refresh(self):
        if (self.win is None):
            return
        self.win.clear()
        self.print_services()
        self.win.refresh()
        window.Window.refresh(self)

    def update(self, svc_list, services, cur_service):
        self.services = services
        self.cur_service = cur_service
        self.refresh()

    def print_services(self):
        # print services
        if (len(self.services) == 0):
            return

        y = 1
        for service in self.services:
            attr = 0
            if (self.cur_service == service):
                string = ">"
                if (self.focused):
                    attr |= curses.A_REVERSE
            else:
                string = " "

            self.win.addstr(y, 0, string)

            # print service name
            if (service.lcn):
                svc_name = "%2d. " % service.lcn
            else:
                svc_name = "    "
            svc_name += service.svc_name + "                "
            width = self.width - 2
            try:
                self.win.addstr(y, 1, svc_name[0:width], attr)
            except:
                pass
            y += 1

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        if (self.cur_service):
            self.info_win.print_ts(self.cur_service)
            self.info_win.print_service(self.cur_service)
            self.info_win.print_stream(self.cur_service)
        self.info_win.win.refresh()

    def move_down(self):
        self.svc_list.move_down()

    def move_up(self):
        self.svc_list.move_up()
