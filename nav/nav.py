#! /usr/bin/env python3


import curses
import sys
import traceback
import poll_loop
import scanner
import monitor
import db_center
import svcwin
import evtwin
import infowin
import fewin
import siwin
import eitwin
import logwin
import svclist
import window
import install
import observer
import logging
import logging.handlers
import os


GRID_TOP_MARGIN = 12
GRID_BOTTOM_MARGIN = 11
EITWIN_WIDTH = 11
MONWIN_WIDTH = 20
FEWIN_WIDTH = 20
FEWIN_HEIGHT = 2
SVCWIN_WIDTH = 24


class LogContainer(logging.handlers.MemoryHandler, observer.Observable):
    def __init__(self, max_logs=100):
        logging.handlers.MemoryHandler.__init__(self, max_logs)
        self.logs = []
        self.max_logs = max_logs
        observer.Observable.__init__(self)

    def emit(self, record):
        string = self.format(record)
        self.logs.append(string)
        if (len(self.logs) > self.max_logs):
            self.logs.pop(0)
        self.notify_observers(string)

    def notify_observers(self, string):
        for observer in self.observers:
            observer.on_log(self, string)

    def get_num_logs(self):
        return len(self.logs)

    def get_max_logs(self):
        return self.max_logs

    def get_logs(self, from_log, to_log):
        return self.logs[from_log:to_log]


class CursorNavigator():
    def __init__(self):
        self.db = db_center.DbCenter()
        self.poller = poll_loop.PollLoop()
        self.poller.register_timer(self.check_status, 1000, 1000)
        self.init_logger()

        self.fe_list = install.FeList()
        self.fe_list.set_frontends()
        self.log_win = None

        self.stdscr = curses.initscr()
        self.height, self.width = self.stdscr.getmaxyx()
        self.svc_list = svclist.SvcList()
        self.svc_list.set_window_height(self.height - GRID_TOP_MARGIN -
                                        GRID_BOTTOM_MARGIN - 1)
        self.svc_list.read_services()
        self.scanner = scanner.Scanner(self.svc_list)
        self.scanner.on_scan_all_finished = self.on_scan_all_finished
        self.monitor = monitor.Monitor(self.svc_list)
        self.time_offset = 0
        self.win_mode = True
        self.help_string = "q: quit, space: refresh"
        self.help_string += ", TAB/S-TAB: window"
        self.help_string += ", o: order"

    def init_logger(self):
        try:
            os.mkdir('logs')
        except OSError:
            pass

        self.logger = logging.getLogger('MainLog')
        self.logger.setLevel(logging.DEBUG)

        string = '%(asctime)s - %(levelname)-8s - %(message)s'
        formatter = logging.Formatter(string)

        self.log_handler = LogContainer(1000)
        self.log_handler.setLevel(logging.INFO)
        #self.log_handler.setLevel(logging.DEBUG)
        self.log_handler.setFormatter(formatter)

        self.logger.addHandler(self.log_handler)

        handler = logging.handlers.TimedRotatingFileHandler('logs/nav.log',
                                                            when='D',
                                                            backupCount=7)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def init_screen(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

    def restore_screen(self):
        for w in self.windows:
            w.win = None
        self.info_win.win = None
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.endwin()

    def reinit_screen(self):
        self.init_screen()

        self.windows.append(self.svc_win)
        self.windows.append(self.evt_win)
        self.windows.append(self.eit_win)
        self.windows.append(self.log_win)
        self.windows.append(self.fe_win)
        self.windows.append(self.si_win)
        self.focused_window = self.windows[self.last_focus_index]

        self.resize()

    def resizer(self):
        return
        c = self.stdscr.getch()
        if (c == curses.KEY_RESIZE):
            self.resize()

    def resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.svc_list.set_window_height(self.height - GRID_TOP_MARGIN -
                                        GRID_BOTTOM_MARGIN - 1)
        self.info_win.resize(GRID_TOP_MARGIN, self.width - MONWIN_WIDTH,
                             0, MONWIN_WIDTH, self.info_win)
        self.log_win.resize(GRID_BOTTOM_MARGIN - 1, self.width,
                            self.height - GRID_BOTTOM_MARGIN, 0, self.info_win)
        self.svc_win.resize(self.height - GRID_TOP_MARGIN - GRID_BOTTOM_MARGIN,
                            SVCWIN_WIDTH, GRID_TOP_MARGIN, 0, self.info_win)
        self.evt_win.resize(self.height - GRID_TOP_MARGIN - GRID_BOTTOM_MARGIN,
                            self.width - EITWIN_WIDTH - SVCWIN_WIDTH,
                            GRID_TOP_MARGIN, SVCWIN_WIDTH, self.info_win)
        self.fe_win.resize(FEWIN_HEIGHT, FEWIN_WIDTH,
                           0, 0, self.info_win)
        self.si_win.resize(GRID_TOP_MARGIN - FEWIN_HEIGHT, MONWIN_WIDTH,
                           FEWIN_HEIGHT, 0, self.info_win)
        self.eit_win.resize(self.height - GRID_TOP_MARGIN - GRID_BOTTOM_MARGIN,
                            EITWIN_WIDTH,
                            GRID_TOP_MARGIN, self.width - EITWIN_WIDTH,
                            self.info_win)

        self.svc_list.notify_observers()

        # print help
        self.print_help()
        self.stdscr.refresh()

    def init_windows(self):
        self.windows = []

        self.svc_win = svcwin.SvcWin(self.svc_list)
        self.evt_win = evtwin.EvtWin(self.svc_list)
        self.info_win = infowin.InfoWin()
        self.fe_win = fewin.FeWin()
        self.si_win = siwin.SiWin()
        self.eit_win = eitwin.EitWin(self.svc_list)
        self.log_win = logwin.LogWin(self.log_handler)

        self.windows.append(self.svc_win)
        self.windows.append(self.evt_win)
        self.windows.append(self.eit_win)
        self.windows.append(self.log_win)
        self.windows.append(self.fe_win)
        self.windows.append(self.si_win)
        self.focused_window = self.windows[0]

        self.evt_win.set_eit_collector(self.monitor.eit_collector)
        self.eit_win.set_eit_collector(self.monitor.eit_collector)

        self.svc_win.set_focus()

        self.resize()

        self.evt_win.reposition()
        self.evt_win.refresh()

    def print_help(self):
        string = self.help_string
        string += self.focused_window.help_string
        string += "                                                   "
        string += "                                                   "
        self.stdscr.addstr(self.height - 1, 0, string[0:self.width - 1])

    def refresh(self):
        for w in self.windows:
            w.refresh()

        # print help
        self.print_help()
        self.stdscr.refresh()

    def check_status(self):
        self.fe_win.refresh()
        self.eit_win.refresh()
        self.evt_win.refresh()
        return

    def full_scan_other(self):
        self.monitor.stop()
        self.scanner.start(True, False)
        self.si_win.set_si_collector(self.scanner.si_collector)

    def full_scan(self):
        self.monitor.stop()
        self.scanner.start()
        self.si_win.set_si_collector(self.scanner.si_collector)

    def get_enter(self):
        key = self.stdscr.getch()
        if (key == 10):
            self.win_mode = True
            self.reinit_screen()

    def key_callback(self, fd, mode):
        if (self.win_mode is False):
            return self.get_enter()

        key = self.stdscr.getch()
        if (key == ord('q')):
            self.poller.stop()
            return

        if (key == curses.KEY_RESIZE):
            self.resize()

        result = self.focused_window.on_keydown(key)
        if (result == window.KEY_PROCESSED):
            return

        if (key == ord(' ')):
            self.evt_win.reposition()
            self.resize()
        elif (key == ord('S')):
            if (self.focused_window == self.evt_win):
                pass
            elif (self.focused_window == self.svc_win):
                self.full_scan_other()
        elif (key == ord('s')):
            if (self.focused_window == self.evt_win):
                self.evt_win.sbr()
            elif (self.focused_window == self.svc_win):
                self.full_scan()
        elif (key == ord('o')):
            self.svc_list.order_plus()
        elif (key == ord('O')):
            self.svc_list.order_minus()
        elif (key == 9):
            # TAB
            self.focused_window.unset_focus()
            focus_index = self.windows.index(self.focused_window)
            focus_index += 1
            focus_index %= len(self.windows)
            self.focused_window = self.windows[focus_index]
            self.focused_window.set_focus()
            self.print_help()
            self.stdscr.refresh()
        elif (key == curses.KEY_BTAB):
            # BTAB
            self.focused_window.unset_focus()
            focus_index = self.windows.index(self.focused_window)
            focus_index -= 1
            focus_index %= len(self.windows)
            self.focused_window = self.windows[focus_index]
            self.focused_window.set_focus()
            self.print_help()
            self.stdscr.refresh()
        elif (key == curses.KEY_UP or key == ord('k')):
            prev_svc = self.svc_list.get_cur_service()
            self.focused_window.move_up()
            cur_service = self.svc_list.get_cur_service()
            if (prev_svc != cur_service):
                self.monitor.start_pmt()
        elif (key == curses.KEY_DOWN or key == ord('j')):
            prev_svc = self.svc_list.get_cur_service()
            self.focused_window.move_down()
            cur_service = self.svc_list.get_cur_service()
            if (prev_svc != cur_service):
                self.monitor.start_pmt()
        elif (key == curses.KEY_LEFT or key == ord('h')):
            self.focused_window.move_left()
        elif (key == curses.KEY_RIGHT or key == ord('l')):
            self.focused_window.move_right()
        elif (key == ord('p') and self.focused_window == self.eit_win):
            self.restore_screen()
            print()
            print("======================================================")
            self.focused_window.print_all_sections()
            print("press enter...")
            self.win_mode = False
            self.last_focus_index = self.windows.index(self.focused_window)
        elif (key == 10):
            # ENTER
            if (self.focused_window == self.svc_win):
                cur_service = self.svc_list.get_cur_service()
                if (cur_service):
                    self.scanner.stop()
                    self.monitor.tune(cur_service)
                    self.si_win.set_si_collector(self.monitor.si_collector)
            elif (self.focused_window == self.si_win or
                  self.focused_window == self.evt_win or
                  self.focused_window == self.eit_win):
                self.restore_screen()
                print()
                print("======================================================")
                self.focused_window.print_sections()
                print("press enter...")
                self.win_mode = False
                self.last_focus_index = self.windows.index(self.focused_window)
            elif (self.focused_window == self.fe_win):
                param = self.fe_win.get_manual_scan_param()
                if (param):
                    self.monitor.stop()
                    self.scanner.start_one_tp(param)
                    self.si_win.set_si_collector(self.scanner.si_collector)
            else:
                self.logger.debug("[getch(): %d]" % key)
        elif (key == ord('e') and self.focused_window == self.evt_win):
            self.evt_win.ebr()
        elif (self.focused_window == self.evt_win and
              ord('0') <= key and key <= ord('7')):
            if (key == ord('0')):
                set_day_of_week = 0
            else:
                set_day_of_week = 0x40 >> (ord('7') - key)
            self.evt_win.tbr(set_day_of_week)
        else:
            self.logger.debug("[getch(): %d]" % key)

    def on_scan_all_finished(self, scanner):
        self.si_win.set_si_collector(self.monitor.si_collector)
        self.monitor.start()

    def ttrun(self):
        try:
            self.init_screen()
            self.init_windows()
            self.refresh()
            self.poller.register_resizer(self.resizer)
            self.poller.register(sys.stdin.fileno(),
                                 poll_loop.POLLIN | poll_loop.POLLERR,
                                 self.key_callback)
            self.poller.run()
            self.restore_screen()
            self.db.sync_events()

        except:
            self.restore_screen()
            traceback.print_exc()


if __name__ == "__main__":
    guide = CursorNavigator()
    guide.ttrun()
