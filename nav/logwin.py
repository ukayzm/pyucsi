#! /usr/bin/env python

import curses
import window
import observer


class LogWin(window.Window, observer.SvcObserver, observer.LogObserver):
    def __init__(self, handler):
        window.Window.__init__(self)
        self.handler = handler
        self.handler.register_observer(self)
        self.cur_index = 0
        self.top_index = 0

        string = ",  up/down: scroll log"
        self.help_string = string

    def read_screen_info(self):
        self.height, width = self.win.getmaxyx()
        self.width = width - 1

    def refresh(self):
        if (self.win is None):
            return
        self.print_logs()
        self.win.refresh()
        window.Window.refresh(self)

    def print_logs(self):
        num_logs = self.handler.get_num_logs()
        if (num_logs == 0):
            return
        if (self.focused):
            from_log = self.top_index
            to_log = from_log + self.height
            if (to_log > num_logs):
                to_log = num_logs
        else:
            to_log = num_logs
            from_log = to_log - self.height
            if (from_log < 0):
                from_log = 0

        logs = self.handler.get_logs(from_log, to_log)

        y = 0
        for log in logs:
            attr = 0
            if (self.focused and y + self.top_index == self.cur_index):
                attr |= curses.A_REVERSE
            string = log.ljust(self.width)[0:self.width - 2]
            try:
                self.win.addstr(y, 0, string, attr)
            except:
                pass
            y += 1

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        self.info_win.win.refresh()

    def on_log(self, handler, string):
        num_logs = self.handler.get_num_logs()
        max_logs = self.handler.get_max_logs()
        if (num_logs == max_logs):
            self.move_up()
        else:
            self.refresh()

    def get_num_logs(self):
        return len(self.logs)

    def set_focus(self):
        window.Window.set_focus(self)
        num_logs = self.handler.get_num_logs()
        self.cur_index = num_logs - 1
        if (self.cur_index < 0):
            self.cur_index = 0
        self.top_index = num_logs - self.height
        if (self.top_index < 0):
            self.top_index = 0
        self.refresh()

    def move_up(self):
        if (self.cur_index > 0):
            self.cur_index -= 1
            if (self.top_index > self.cur_index):
                self.top_index = self.cur_index
        self.refresh()

    def move_down(self):
        num_logs = self.handler.get_num_logs()
        if (self.cur_index < num_logs - 1):
            self.cur_index += 1
            last_index = self.top_index + self.height
            if (last_index <= self.cur_index):
                self.top_index += 1
        self.refresh()
