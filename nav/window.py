#! /usr/bin/env python

import curses

KEY_PROCESSED = 0
KEY_NOT_PROCESSED = 1

class Window():
    def __init__(self):
        self.focused = False
        self.win = None
        self.info_win = None
        self.width = 0
        self.height = 0
        self.help_string = ""

    def read_screen_info(self):
        self.height, self.width = self.win.getmaxyx()

    def resize(self, height, width, y, x, info_win):
        self.info_win = info_win
        self.win = curses.newwin(height, width, y, x)
        self.read_screen_info()
        self.refresh()

    def print_info(self):
        pass

    def refresh(self):
        if (self.focused and self.win):
            self.print_info()

    def on_keydown(self, key):
        return KEY_NOT_PROCESSED

    def set_focus(self):
        self.focused = True
        self.refresh()

    def unset_focus(self):
        self.focused = False
        self.refresh()

    def move_down(self):
        pass

    def move_up(self):
        pass

    def move_left(self):
        pass

    def move_right(self):
        pass

