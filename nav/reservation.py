#! /usr/bin/env python3


import dvb
import logging
import db_center
from datetime import datetime, timedelta


class ReservationMgr():
    def __init__(self):
        self.db = db_center.DbCenter()
        self.logger = logging.getLogger('MainLog')

    def remove_reservation(self, rsv_key):
        self.db.remove_reservation(rsv_key)
        self.db.commit()
        self.logger.info("removed: rsv[%d]" % rsv_key)

    def _copy_event_to_sched(self, event, sched):
        sched.description = event.description
        sched.svc_key = event.svc_key
        sched.svc_name = event.svc_name
        sched.evid = event.evid
        sched.prog_crid = event.prog_crid
        sched.season = event.season
        sched.episode = event.episode
        sched.total_episodes = event.total_episodes
        sched.imi = event.imi
        sched.split_number = event.split_number
        sched.total_splits = event.total_splits
        sched.time_offset = event.time_offset

    def make_ebr(self, event):
        rsv = dvb.EBR(event.evt_name, event.svc_key, event.evid)
        rsv.description = event.description
        rsv_key = self.db.save_reservation(rsv)
        rsv = self.db.read_reservation(rsv_key)

        # make schedule
        sched = self.db.read_schedule_of_period(rsv.action,
                                                event.svc_key,
                                                event.start_time,
                                                event.end_time)
        if (sched):
            self._copy_event_to_sched(event, sched)
            self.db.save_schedule(sched)
            self.logger.info("shared: " + str(sched))
        else:
            sched = dvb.Schedule(event.evt_name, rsv.action,
                                 event.start_time, event.end_time)
            self._copy_event_to_sched(event, sched)
            self.db.save_schedule(sched)
            self.logger.info("added: " + str(sched))

        self.db.link_rsv_sched(rsv, sched)
        self.db.commit()

        rsv = self.db.read_reservation(rsv_key)
        self.logger.info("added: " + str(rsv))
        return rsv

    def make_sbr(self, seed_event, series_crid):
        rsv = dvb.SBR(seed_event.evt_name, seed_event.svc_key,
                      seed_event.evid, series_crid)
        rsv.description = "series CRID: " + series_crid
        rsv_key = self.db.save_reservation(rsv)

        # make schedules
        prog_crids = self.db.get_prog_crid_list_of_series(series_crid)
        for prog_crid in prog_crids:
            alternatives = self.db.get_alternatives_of_program(prog_crid)
            if (len(alternatives) == 0):
                continue
            if (seed_event in alternatives):
                event = seed_event
            else:
                event = alternatives[0]

            # check if it is already scheduled?
            sched = self.db.read_schedule_of_period(rsv.action,
                                                    event.svc_key,
                                                    event.start_time,
                                                    event.end_time)
            if (sched):
                self._copy_event_to_sched(event, sched)
                self.db.save_schedule(sched)
                self.logger.info("shared: " + str(sched))
            else:
                sched = dvb.Schedule(event.evt_name, rsv.action,
                                     event.start_time, event.end_time)
                self._copy_event_to_sched(event, sched)
                self.db.save_schedule(sched)
                self.logger.info("added: " + str(sched))

            self.db.link_rsv_sched(rsv, sched)
        self.db.commit()

        rsv = self.db.read_reservation(rsv_key)
        self.logger.info("added: " + str(rsv))
        return rsv

    def make_tbr(self, name, svc_key, yyyymmdd, hhmmss, duration,
                 day_of_week):
        rsv = dvb.TBR(name, svc_key, yyyymmdd, hhmmss, duration, day_of_week)
        rsv_key = self.db.save_reservation(rsv)
        rsv = self.db.read_reservation(rsv_key)

        # make schedules
        self.reschedule_tbr(rsv)
        self.db.commit()

        rsv = self.db.read_reservation(rsv_key)
        self.logger.info("added: " + str(rsv))
        return rsv

    def reschedule_tbr(self, rsv):
        yyyymmdd = rsv.yyyymmdd
        hhmmss = rsv.hhmmss
        if (yyyymmdd == 0):
            dt = datetime.now()
            yyyymmdd = dt.year * 10000 + dt.month * 100 + dt.day
        time_offset = self.db.read_time_offset_of_svc(rsv.svc_key)
        # TODO: set tzinfo to dt
        dt = datetime(yyyymmdd // 10000, (yyyymmdd // 100) % 100,
                      (yyyymmdd % 100), hhmmss // 10000,
                      (hhmmss // 100) % 100, hhmmss % 100)
        # TODO: set schedule according to day_of_week.
        # in this implementation, make all 7 days for test...
        self.logger.info("reschedule day_of_week: " + hex(rsv.day_of_week))
        for i in range(0, 7):
            timestamp = (dt - datetime(1970, 1, 1)) // timedelta(seconds=1)
            start_time = int(timestamp) - time_offset
            end_time = start_time + rsv.duration
            dt_weekday = dt.isoweekday()
            if (dt_weekday == 7):
                dt_weekday = 0
            week_flag = 1 << dt_weekday

            sched = self.db.read_schedule_of_period(rsv.action,
                                                    rsv.svc_key,
                                                    start_time,
                                                    end_time)
            if (rsv.day_of_week == 0 and i == 0):
                schedule_it = True
            elif (week_flag & rsv.day_of_week):
                schedule_it = True
            else:
                schedule_it = False
            if (schedule_it):
                # add schedule
                if (sched):
                    rsv_link = dvb.RsvLink(rsv, sched, "")
                    if (rsv_link in sched.rsv_links):
                        self.logger.info("already scheduled: " + str(sched))
                    else:
                        self.logger.info("shared: " + str(sched))
                        self.db.link_rsv_sched(rsv, sched)
                else:
                    sched = dvb.Schedule(rsv.rsv_name, rsv.action,
                                         start_time, end_time)
                    sched.svc_key = rsv.svc_key
                    sched.time_offset = time_offset
                    # TODO: set rest of fields for a representative event.
                    self.db.save_schedule(sched)
                    self.logger.info("added: " + str(sched))
                    self.db.link_rsv_sched(rsv, sched)
            else:
                # remove schedule
                if (sched):
                    self.logger.info("remove link: " + str(sched))
                    self.db.unlink_rsv_sched(rsv, sched)

            dt += timedelta(1)
