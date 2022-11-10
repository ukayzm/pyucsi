import window
import curses
import dvb
import logging
import observer
import si_print
import db_center
import reservation
from datetime import datetime


class EvtWin(window.Window, observer.SvcObserver):
    def __init__(self, svc_list):
        window.Window.__init__(self)
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.eit_collector = None
        self.cur_evt = -1
        self.cur_event = None
        self.left_sec = 0
        self.cursor_sec = 0
        self.logger = logging.getLogger('MainLog')
        self.services = []
        self.cur_service = None
        self.svc_list = svc_list
        self.svc_list.register_observer(self)
        self.rsv_mgr = reservation.ReservationMgr()

        string = ", hjkl: move"
        string += ", enter: print section"
        string += ", s: sbr"
        string += ", p: pbr"
        string += ", e: ebr"
        string += ", 01234567: tbr"
        string += ", E: ebw"
        string += ", )!@#$%^&: tbw"
        self.help_string = string

    def set_eit_collector(self, eit_collector):
        self.eit_collector = eit_collector

    def read_screen_info(self):
        height, width = self.win.getmaxyx()
        self.height = height - 1
        self.width = width - 3

    def refresh(self):
        if (self.win is None):
            return
        if (self.eit_collector is None):
            return
        self.win.clear()
        self.print_grid()
        self.win.refresh()
        window.Window.refresh(self)

    def update(self, svc_list, services, cur_service):
        self.services = services
        self.cur_service = cur_service
        if (self.cur_service):
            self.read_events()
            # set current event according to cursor_sec
            i = 0
            for event in self.cur_service.events:
                if (event.start_time <= self.cursor_sec and
                    self.cursor_sec <= event.end_time):
                    self.cur_evt = i
                    break
                i += 1
        self.refresh()

    def read_events(self):
        for service in self.services:
            self.read_events_of_service(service)
        if (self.cur_service is None):
            return
        if (self.cur_evt >= len(self.cur_service.events)):
            self.cur_evt = len(self.cur_service.events) - 1

    def read_events_of_service(self, service):
        c = self.connection.cursor()
        right_sec = self.left_sec + self.width * 120
        c.execute('''select events.evt_key, events.evid,
                  start_time, end_time, evt_name
                  from events left outer join event_texts
                  on events.evt_key = event_texts.evt_key
                  where start_time < ? and end_time > ?
                    and events.svc_key = ?
                  order by start_time''',
                  [right_sec, self.left_sec, service.svc_key])
        rows = c.fetchall()

        service.events = []
        if (not rows):
            event = dvb.Event(0, 0, 0, 0x7fffffff, "", service.svc_key,
                              service.svc_name, service.ts_key)
            service.events.append(event)
            return

        if (rows[0]['start_time'] > self.left_sec):
            event = dvb.Event(0, 0, 0, rows[0]['start_time'], "",
                              service.svc_key, service.svc_name,
                              service.ts_key)
            service.events.append(event)

        prev_evt_key = 0
        for row in rows:
            if (row['evt_name'] is None):
                evt_name = "(" + hex(row['evid']) + ")"
            else:
                #evt_name = row['evt_name'].encode('ascii', 'replace')
                evt_name = row['evt_name']
            if (row['evt_key'] != prev_evt_key):
                event = dvb.Event(row['evt_key'], row['evid'],
                                  row['start_time'], row['end_time'], evt_name,
                                  service.svc_key, service.svc_name,
                                  service.ts_key)
                service.events.append(event)
                prev_evt_key = row['evt_key']

        last_time = event.end_time
        if (last_time < right_sec):
            event = dvb.Event(0, 0, last_time, 0x7fffffff, "",
                              service.svc_key, service.svc_name,
                              service.ts_key)
            service.events.append(event)

    def print_grid(self):
        # get time offset
        if (self.cur_service is not None):
            ts_key = self.cur_service.ts_key
            time_offset = self.db.read_time_offset(ts_key)
        else:
            time_offset = 0

        # print time_offset
        string = "(%+d:%02d)  " % ((time_offset // 3600),
                                  ((time_offset % 3600) // 60))
        self.win.addstr(0, 6, string)

        # print ruler
        x = -2
        right_sec = self.left_sec + self.width * 120

        for sec in range(self.left_sec,
                         right_sec + 1,
                         3600):
            local_sec = sec + time_offset
            minute = int(local_sec / 60)
            hour = int(minute / 60) % 24
            minute = minute % 60
            string = "%02d:%02d" % (hour, minute)
            if (x < 0):
                self.win.addstr(0, 0, string)
            else:
                self.win.addstr(0, x, string)
            x = x + 30

        # print services
        if (len(self.services) == 0):
            return

        # print event grid
        for y, service in enumerate(self.services):
            for event in service.events:
                self.print_event(y + 1, event, False)

        if (self.focused is False):
            return

        y = 1
        for service in self.services:
            if (self.cur_service == service):
                event = service.events[self.cur_evt]
                self.print_event(y, event, True)
                break
            y += 1

    def print_event(self, y, event, highlight):
        start_pos = int((event.start_time - self.left_sec) / 120)
        if (start_pos < 0):
            start_pos = 0
            start_char = '('
        else:
            start_char = '['
        if (event.evid == 0):
            start_char = ':'

        end_pos = int((event.end_time - self.left_sec) / 120) - 1
        if (end_pos > self.width - 1):
            end_pos = self.width - 1
            end_char = ')'
        else:
            end_char = ']'
        if (event.evid == 0):
            end_char = ':'

        name_width = end_pos - start_pos - 1
        if (name_width < 0):
            name_width = 0
            evt_name = ""
        else:
            evt_name = event.evt_name[:name_width].center(name_width)

        event_str = "%c%s%c" % (start_char, evt_name, end_char)

        attr = 0
        if (highlight):
            attr |= curses.A_REVERSE

        # check if it is reserved to be recorded
        action = dvb.Reservation.ACTION_RECORD
        is_scheduled = self.db.is_period_scheduled(action,
                                                   event.svc_key,
                                                   event.start_time,
                                                   event.end_time)
        if (is_scheduled is False):
            action = dvb.Reservation.ACTION_WATCH
            is_scheduled = self.db.is_period_scheduled(action,
                                                       event.svc_key,
                                                       event.start_time,
                                                       event.end_time)
        if (is_scheduled):
            attr |= curses.A_BOLD | curses.A_UNDERLINE

        if (start_pos + len(event_str) > self.width):
            str_width = self.width - start_pos
            event_str = event_str[0:str_width]

        try:
            self.win.addstr(y, start_pos + 1, event_str, attr)
        except:
            pass

    def reposition(self):
        if (self.cur_service is None):
            return

        min_time = 0
        max_time = 0
        max_start_time = 0

        c = self.connection.cursor()
        c.execute('''select min(start_time) from events
                  where svc_key = ?''', [self.cur_service.svc_key])
        row = c.fetchone()
        if (row and row[0]):
            min_time = int(row[0] / 3600) * 3600

        c.execute('''select max(end_time) from events
                  where svc_key = ?''', [self.cur_service.svc_key])
        row = c.fetchone()
        if (row and row[0]):
            max_time = row[0]

        c.execute('''select max(start_time) from events
                  where svc_key = ?''', [self.cur_service.svc_key])
        row = c.fetchone()
        if (row and row[0]):
            max_start_time = row[0]

        if (min_time and max_time and max_start_time):
            scr_time_width = self.width * 120
            if (self.left_sec + scr_time_width < min_time):
                self.left_sec = min_time
                self.cursor_sec = min_time
            elif (max_time <= self.left_sec):
                self.left_sec = int(max_start_time / 3600) * 3600
                self.cursor_sec = max_time - 1

        self.read_events()
        if (self.cur_evt > 0):
            self.cur_evt = 0
        self.cur_evt = 0

        # set current event according to cursor_sec
        i = 0
        for event in self.cur_service.events:
            if (event.start_time <= self.cursor_sec and
                self.cursor_sec <= event.end_time):
                self.cur_evt = i
                break
            i += 1

    def move_page_left(self):
        scr_time_width = self.width * 120
        offset = int(scr_time_width / 3600) * 3600
        offset = 3600
        self.left_sec -= offset
        if (self.left_sec < 0):
            self.left_sec = 0
        self.read_events()
        self.cur_evt = 0

    def move_page_right(self):
        scr_time_width = self.width * 120
        offset = int(scr_time_width / 3600) * 3600
        offset = 3600
        self.left_sec += offset
        self.read_events()
        self.cur_evt = len(self.cur_service.events) - 1

    def move_left(self):
        if (len(self.services) == 0):
            return
        if (self.cur_evt <= 0):
            self.move_page_left()
        else:
            self.cur_evt -= 1
            cur_event = self.cur_service.events[self.cur_evt]
            if (cur_event.start_time != 0):
                time_diff = cur_event.end_time - cur_event.start_time
                self.cursor_sec = cur_event.start_time + int(time_diff / 2)
        self.refresh()

    def move_right(self):
        if (len(self.services) == 0):
            return
        if (self.cur_evt < len(self.cur_service.events) - 1):
            self.cur_evt += 1

            # save cursor_sec
            cur_event = self.cur_service.events[self.cur_evt]
            if (cur_event.start_time != 0):
                time_diff = cur_event.end_time - cur_event.start_time
                self.cursor_sec = cur_event.start_time + int(time_diff / 2)
        else:
            self.move_page_right()
        self.refresh()

    def print_info(self):
        if (self.info_win.win is None):
            return
        self.info_win.win.clear()
        if (self.cur_service):
            cur_event = self.cur_service.events[self.cur_evt]
            self.info_win.print_ts(self.cur_service)
            self.info_win.print_service(self.cur_service)
            self.info_win.print_event(cur_event)
        self.info_win.win.refresh()

    def move_down(self):
        self.svc_list.move_down()

    def move_up(self):
        self.svc_list.move_up()

    def print_alternatives(self, prog_crid):
        c = self.connection.cursor()
        q = '''select * from programs where prog_crid = ?'''
        c.execute(q, [prog_crid])
        rows = c.fetchall()
        if (rows is None):
            # error
            return
        print("alternatives:")
        for row in rows:
            print(self.db.read_event(row['evt_key']))

    def print_series_tree(self, series_crid):
        c = self.connection.cursor()

        print("series CRID:", series_crid)
        q = '''select distinct(prog_crid) from series_crids
               join programs
                 on series_crids.evt_key = programs.evt_key
               where series_crids.series_crid = ?;'''
        c.execute(q, [series_crid])
        rows = c.fetchall()
        if (rows is None):
            return
        for row in rows:
            self.print_alternatives(row['prog_crid'])
            print("")

        q = '''select series_crids.evt_key from series_crids
               left outer join programs
                 on series_crids.evt_key = programs.evt_key
               where series_crids.series_crid = ?
                 and programs.evt_key ISNULL;'''
        c.execute(q, [series_crid])
        rows = c.fetchall()
        if (rows is None):
            return
        for row in rows:
            print("no alternatives:")
            print(self.db.read_event(row['evt_key']))
            print("")

    def print_sections(self):
        self.print_eit_section()

        cur_event = self.cur_service.events[self.cur_evt]

        c = self.connection.cursor()
        c.execute('''select series_crid from series_crids
                  where evt_key = ?''', [cur_event.evt_key])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                self.print_series_tree(row['series_crid'])
            return
        c = self.connection.cursor()
        c.execute('''select prog_crid from programs
                  where evt_key = ?''', [cur_event.evt_key])
        row = c.fetchone()
        if (row):
            self.print_alternatives(row['prog_crid'])
            return
        print(self.db.read_event(cur_event.evt_key))

    def print_eit_section(self):
        if (self.cur_service is None):
            return
        if (self.cur_evt < 0):
            return
        service = self.cur_service
        cur_event = self.cur_service.events[self.cur_evt]

        svc_table_key = (service.svid, service.tsid, service.onid)
        svc_table = self.eit_collector.eit_sch.get_svc_table(svc_table_key)
        if (svc_table is None):
            return
        sections = svc_table.get_sections()
        for section in sections:
            svid = section.service_id
            tsid = section.transport_stream_id
            onid = section.original_network_id
            if (svid != service.svid):
                continue
            if (tsid != service.tsid):
                continue
            if (onid != service.onid):
                continue
            for event in section.events:
                evid = event.event_id
                if (evid == cur_event.evid):
                    si_print.print_section(section)
                    return

    def ebr(self):
        cur_event = self.cur_service.events[self.cur_evt]
        event = self.db.read_event(cur_event.evt_key)
        rsv_key = self.db.get_ebr_key(event.svc_key, event.evid)
        if (rsv_key):
            self.logger.info("removing EBR for " + str(event))
            self.rsv_mgr.remove_reservation(rsv_key)
        else:
            self.logger.info("making EBR for " + str(event))
            self.rsv_mgr.make_ebr(event)

    def sbr(self):
        cur_event = self.cur_service.events[self.cur_evt]
        event = self.db.read_event(cur_event.evt_key)
        if (len(event.series_crids) == 0):
            self.logger.info("No series CRID for " + str(event))
            return

        # TODO: all series_crids should be considered.
        series_crid = event.series_crids[0]

        rsv_key = self.db.get_sbr_key(series_crid)
        if (rsv_key):
            self.logger.info("removing SBR for " + str(event))
            self.rsv_mgr.remove_reservation(rsv_key)
        else:
            self.logger.info("making SBR for " + str(event))
            self.rsv_mgr.make_sbr(event, series_crid)

    def tbr(self, set_day_of_week):
        cur_event = self.cur_service.events[self.cur_evt]
        event = self.db.read_event(cur_event.evt_key)
        dt = datetime.utcfromtimestamp(event.start_time + event.time_offset)
        hhmmss = dt.hour * 10000 + dt.minute * 100 + dt.second
        yyyymmdd = dt.year * 10000 + dt.month * 100 + dt.day
        duration = event.duration()
        self.logger.info(str(yyyymmdd) + str(hhmmss) + ":" + str(duration))
        self.logger.info(str(event.start_time))
        rsv_key = self.db.get_tbr_key(event.svc_key, yyyymmdd, hhmmss,
                                      duration)
        if (set_day_of_week == 0 and rsv_key):
            self.logger.info("removing TBR for " + str(event))
            self.rsv_mgr.remove_reservation(rsv_key)
            return
        if (rsv_key):
            self.logger.info("updating TBR for " + str(event))
            rsv = self.db.read_reservation(rsv_key)
            new_day_of_week = rsv.day_of_week ^ set_day_of_week
            rsv.day_of_week = new_day_of_week
            self.db.save_reservation(rsv)
            self.rsv_mgr.reschedule_tbr(rsv)
            self.db.commit()
        else:
            self.logger.info("making TBR for " + str(event))
            self.rsv_mgr.make_tbr(event.evt_name, event.svc_key, yyyymmdd,
                                  hhmmss, duration, set_day_of_week)
