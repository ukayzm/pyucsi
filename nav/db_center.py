#! /usr/bin/env python3


from sqlite3 import dbapi2 as sqlite
import dvbsi
from private import dtg
from private import boxer
import os
#from private import huffman
import dvb


class DbSqlite3:
    class Impl:
        """ Implementation of the singleton interface """

        event_tables = ['events', 'event_genres', 'event_parental_ratings',
                        'event_items', 'event_texts', 'series_crids',
                        'programs']

        dbs = ["install", "services", "events", "settings"]

        def create_db(self, db, schema):
            print("creating", db)

            try:
                os.remove(db)
            except:
                pass

            schema = open(schema, 'r')
            sql = schema.read()
            schema.close()

            con = sqlite.connect(db)
            c = con.cursor()
            c.executescript(sql)
            con.commit()
            con.close()

        def __init__(self):
            for db_name in self.dbs:
                db_file_name = db_name + ".db"
                schema_file_name = db_name + ".sql"
                try:
                    dbfile = open(db_file_name)
                    dbfile.close()
                except:
                    self.create_db(db_file_name, schema_file_name)

            self.connection = sqlite.connect(":memory:")
            self.connection.row_factory = sqlite.Row
            c = self.connection.cursor()

            c.execute('''ATTACH DATABASE 'services.db' AS svcdb''')
            c.execute('''ATTACH DATABASE 'install.db' AS instdb''')
            c.execute('''ATTACH DATABASE 'settings.db' AS setdb''')

            schema = open('events.sql', 'r')
            sql = schema.read()
            schema.close()

            c.executescript(sql)

            self.load_events_db()

            self.connection.commit()

        def load_events_db(self):
            print("loading events.db...")

            c = self.connection.cursor()

            # copy contents from events.db
            c.execute('''ATTACH DATABASE 'events.db' AS filedb''')

            for table in self.event_tables:
                query = "INSERT OR IGNORE INTO " + table
                query += " SELECT * from filedb." + table + ";"
                c.execute(query)

            c.execute('''DETACH filedb''')

            self.connection.commit()

            print("done.")

        def sync_events_db(self):
            print("syncing events.db...")

            c = self.connection.cursor()

            c.execute('''ATTACH DATABASE 'events.db' AS filedb''')

            for table in self.event_tables:
                query = "DELETE FROM filedb." + table + ";"
                c.execute(query)

            for table in self.event_tables:
                query = "INSERT INTO filedb." + table
                query += " SELECT * from " + table + ";"
                c.execute(query)

            c.execute('''DETACH filedb''')

            self.connection.commit()

            print("done.")

        def get_connection(self):
            return self.connection

    # storage for the instance reference
    singleton = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if DbSqlite3.singleton is None:
            # Create and remember instance
            DbSqlite3.singleton = DbSqlite3.Impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_DbSqlite3__instance'] = DbSqlite3.singleton

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.singleton, attr)

    def __setattr__(self, attr):
        """ Delegate access to implementation """
        return setattr(self.singleton, attr)


class DbCenter:
    def __init__(self):
        self.sqlite_db = DbSqlite3()
        self.connection = self.sqlite_db.get_connection()

    def commit(self):
        self.connection.commit()
        return

    def sync_events(self):
        self.sqlite_db.sync_events_db()

    def save_network(self, nid, net_name):
        c = self.connection.cursor()

        c.execute('''select * from networks where nid = ?''', [nid])
        row = c.fetchone()

        if (not row):
            if (net_name is None):
                c.execute('''insert into networks (nid) values(?)''', [nid])
            else:
                q = 'insert into networks (nid, net_name) values(?, ?)'
                c.execute(q, [nid, net_name])
        elif (net_name is not None and row['net_name'] != net_name):
            c.execute('''update networks set net_name = ? where nid = ?''',
                      [net_name, nid])
        return

    def save_bouquet(self, bid, bq_name):
        c = self.connection.cursor()
        c.execute('''select * from bouquets where bid = ?''', [bid])
        row = c.fetchone()

        if (not row):
            c.execute('''insert into bouquets (bid, bq_name) values(?, ?)''',
                      [bid, bq_name])
        else:
            c.execute('''update bouquets set bq_name = ?
                      where bid = ? and bq_name != ?''',
                      [bq_name, bid, bq_name])
        return

    def update_transport(self, ts_key, nid, onid, tsid):
        c = self.connection.cursor()
        c.execute('''update transports set
                  nid = ?, tsid = ?, onid = ?
                  where ts_key = ? and
                  (nid != ? or nid is null or
                   tsid != ? or tsid is null or
                   onid != ? or onid is null)''',
                  [nid, tsid, onid, ts_key, nid, tsid, onid])
        return

    def save_transport(self, src_key, nid, onid, tsid):
        c = self.connection.cursor()
        c.execute('''select * from transports
                       where nid = ? and tsid = ? and onid = ?
                         and src_key = ?''',
                  [nid, tsid, onid, src_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into transports (nid, tsid, onid, src_key)
                           values(?, ?, ?, ?)''', [nid, tsid, onid, src_key])
        return

    def save_time_offset(self, ts_key, time_offset):
        c = self.connection.cursor()
        c.execute('update transports set time_offset = ? where ts_key = ?',
                  [time_offset, ts_key])
        self.connection.commit()

    def read_time_offset(self, ts_key):
        c = self.connection.cursor()
        c.execute('select time_offset from transports where ts_key = ?',
                  [ts_key])
        row = c.fetchone()
        if (not row or row['time_offset'] is None):
            return 0
        return row['time_offset']

    def read_time_offset_of_svc(self, svc_key):
        c = self.connection.cursor()
        c.execute('''select time_offset from transports
                  join services on transports.ts_key = services.ts_key
                  where svc_key = ?''', [svc_key])
        row = c.fetchone()
        if (not row or row['time_offset'] is None):
            return 0
        return row['time_offset']

    def save_transport_default_authority(self, ts_key, def_auth):
        c = self.connection.cursor()
        c.execute('''insert or replace into default_authorities_ts
                  (ts_key, default_authority) values (?, ?)''',
                  [ts_key, def_auth])

    def read_transport_default_authority(self, ts_key):
        c = self.connection.cursor()
        c.execute('''select default_authority from default_authorities_ts
                  where ts_key = ?''', [ts_key])
        row = c.fetchone()
        if (not row):
            return None
        return row[0]

    def save_default_authority(self, svc_key, def_auth):
        c = self.connection.cursor()
        c.execute('''insert or replace into default_authorities
                  (svc_key, default_authority)
                  values (?, ?)''', [svc_key, def_auth])

    def save_file_param(self, ts_key, dsc):
        c = self.connection.cursor()
        pathname = dsc.pathname

        c.execute('''select * from ts_params_file
                     where ts_key = ?''', [ts_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into ts_params_file
                      (ts_key, pathname)
                      values(?, ?)''',
                      [ts_key, pathname])
        else:
            if (row['pathname'] != pathname):
                c.execute('''update ts_params_file set pathname = ?
                          where ts_key = ?''',
                          [pathname, ts_key])
        return

    def save_ter_param(self, ts_key, dsc):
        c = self.connection.cursor()

        c.execute('''select * from ts_params_ter where ts_key = ?''', [ts_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into ts_params_ter
                      (ts_key, freq, bandwidth, code_rate_HP,
                      code_rate_LP, constellation, transmission_mode,
                      guard_interval, hierarchy_information)
                      values(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      [ts_key,
                       dsc.frequency,
                       dsc.bandwidth,
                       dsc.code_rate_hp_stream,
                       dsc.code_rate_lp_stream,
                       dsc.constellation,
                       dsc.transmission_mode,
                       dsc.guard_interval,
                       dsc.hierarchy_information])
        else:
            if ( row['freq'] != dsc.frequency or
                 row['code_rate_HP'] != dsc.code_rate_hp_stream or
                 row['code_rate_LP'] != dsc.code_rate_lp_stream or
                 row['constellation'] != dsc.constellation or
                 row['transmission_mode'] != dsc.transmission_mode or
                 row['guard_interval'] != dsc.guard_interval or
                 row['hierarchy_information'] != dsc.hierarchy_information):
                c.execute('''update ts_params_ter
                          set freq = ?, code_rate_HP = ?,
                          code_rate_LP = ?,
                          constellation = ?,
                          transmission_mode = ?,
                          guard_interval = ?,
                          hierarchy_information= ?
                          where ts_key = ?''',
                          [dsc.frequency,
                           dsc.code_rate_hp_stream,
                           dsc.code_rate_lp_stream,
                           dsc.constellation,
                           dsc.transmission_mode,
                           dsc.guard_interval,
                           dsc.hierarchy_information,
                           ts_key])
        return

    def get_ter_param(self, ts_key):
        c = self.connection.cursor()
        c.execute('select * from ts_params_ter where ts_key = ?', [ts_key])
        return c.fetchone()

    def get_sat_param(self, ts_key):
        c = self.connection.cursor()
        c.execute('select * from ts_params_sat where ts_key = ?', [ts_key])
        return c.fetchone()

    def get_file_param(self, ts_key):
        c = self.connection.cursor()
        c.execute('select * from ts_params_file where ts_key = ?', [ts_key])
        return c.fetchone()

    def _set_sat_transport(self, ts, row):
        if (row['freq'] is not None):
            ts.frequency = row['freq']
        if (row['orbital_position'] is not None):
            ts.orbital_position = row['orbital_position']
        if (row['polarization'] is not None):
            ts.polarization = row['polarization']
        if (row['roll_off'] is not None):
            ts.roll_off = row['roll_off']
        if (row['modulation_system'] is not None):
            ts.modulation_system = row['modulation_system']
        if (row['modulation_type'] is not None):
            ts.modulation_type = row['modulation_type']
        if (row['symbol_rate'] is not None):
            ts.symbol_rate = row['symbol_rate']
        if (row['fec_inner'] is None or row['fec_inner'] < 1 or
            row['fec_inner'] >= 10):
            ts.fec_inner = 0
        else:
            ts.fec_inner = row['fec_inner']
        if (row['signal_strength'] is not None):
            ts.signal_strength = row['signal_strength']
        if (row['signal_quality'] is not None):
            ts.signal_quality = row['signal_quality']

    def _set_ter_transport(self, ts, row):
        if (row['freq'] is not None):
            ts.frequency = row['freq']
        if (row['bandwidth'] is not None):
            ts.bandwidth = row['bandwidth']
        return
        if (row['code_rate_HP'] is not None):
            ts.code_rate_hp_stream = row['code_rate_HP']
        if (row['code_rate_LP'] is not None):
            ts.code_rate_lp_stream = row['code_rate_LP']
        if (row['constellation'] is not None):
            ts.constellation = row['constellation']
        if (row['transmission_mode'] is not None):
            ts.transmission_mode = row['transmission_mode']
        if (row['guard_interval'] is not None):
            ts.guard_interval = row['guard_interval']
        if (row['hierarchy_information'] is not None):
            ts.hierarchy_information = row['hierarchy_information']
        if (row['signal_strength'] is not None):
            ts.signal_strength = row['signal_strength']
        if (row['signal_quality'] is not None):
            ts.signal_quality = row['signal_quality']

    def _set_file_transport(self, ts, row):
        if (row['pathname'] is not None):
            ts.pathname = row['pathname']

    def _get_sat_transports(self, src_key, orbital_position):
        c = self.connection.cursor()
        transports = []
        query = """select * from transports
                   join ts_params_sat
                     on transports.ts_key = ts_params_sat.ts_key
                   join sources on transports.src_key = sources.src_key
                   where sources.src_key = ?"""
        c.execute(query, [src_key])
        rows = c.fetchall()
        if rows is None:
            return transports
        for row in rows:
            ts = dvb.TsSat(row['ts_key'], row['src_key'], row['nid'],
                           row['onid'], row['tsid'])
            self._set_sat_transport(ts, row)
            if (orbital_position is not None):
                ts.orbital_position = orbital_position
            transports.append(ts)
        return transports

    def _get_ter_transports(self, src_key):
        c = self.connection.cursor()
        transports = []
        query = """select * from transports
                   join ts_params_ter
                     on transports.ts_key = ts_params_ter.ts_key
                   join sources on transports.src_key = sources.src_key
                   where sources.src_key = ?"""
        c.execute(query, [src_key])
        rows = c.fetchall()
        if rows is None:
            return transports
        for row in rows:
            ts = dvb.TsTer(row['ts_key'], row['src_key'], row['nid'],
                           row['onid'], row['tsid'])
            self._set_ter_transport(ts, row)
            transports.append(ts)
        return transports

    def _get_file_transports(self, src_key):
        c = self.connection.cursor()
        transports = []
        query = """select * from transports
                   join ts_params_file
                     on transports.ts_key = ts_params_file.ts_key
                   join sources on transports.src_key = sources.src_key
                   where sources.src_key = ?"""
        c.execute(query, [src_key])
        rows = c.fetchall()
        if rows is None:
            return transports
        for row in rows:
            ts = dvb.TsFile(row['ts_key'], row['src_key'], row['nid'],
                            row['onid'], row['tsid'])
            self._set_file_transport(ts, row)
            transports.append(ts)
        return transports

    def read_transports(self, src_key):
        c = self.connection.cursor()
        c.execute('''select delivery_system, orbital_position from sources
                     where src_key = ?''', [src_key])
        row = c.fetchone()
        if (row is None):
            return []
        delivery_system = row['delivery_system']
        orbital_position = row['orbital_position']
        if (delivery_system == 0):
            return self._get_sat_transports(src_key, orbital_position)
        elif (delivery_system == 2):
            return self._get_ter_transports(src_key)
        elif (delivery_system == 8):
            return self._get_file_transports(src_key)
        else:
            return []

    def read_transport(self, ts_key):
        c = self.connection.cursor()
        query = """select * from transports
                   join sources on transports.src_key = sources.src_key
                   where ts_key = ?"""
        c.execute(query, [ts_key])
        row = c.fetchone()
        if (not row):
            return dvb.Transport(0, 0)
        delivery_system = row['delivery_system']
        if (delivery_system == 0):
            ts = dvb.TsSat(ts_key, row['src_key'], row['nid'],
                           row['onid'], row['tsid'])
            query = """select * from transports
                       join ts_params_sat
                         on transports.ts_key = ts_params_sat.ts_key
                       where transports.ts_key = ?"""
            c.execute(query, [ts_key])
            row = c.fetchone()
            if (not row):
                return ts
            self._set_sat_transport(ts, row)
            return ts
        elif (delivery_system == 2):
            ts = dvb.TsTer(ts_key, row['src_key'], row['nid'],
                           row['onid'], row['tsid'])
            query = """select * from transports
                       join ts_params_ter
                         on transports.ts_key = ts_params_ter.ts_key
                       where transports.ts_key = ?"""
            c.execute(query, [ts_key])
            row = c.fetchone()
            if (not row):
                return ts
            self._set_ter_transport(ts, row)
            return ts
        elif (delivery_system == 8):
            ts = dvb.TsFile(ts_key, row['src_key'], row['nid'],
                            row['onid'], row['tsid'])
            query = """select * from transports
                       join ts_params_file
                         on transports.ts_key = ts_params_file.ts_key
                       where transports.ts_key = ?"""
            c.execute(query, [ts_key])
            row = c.fetchone()
            if (not row):
                return ts
            self._set_file_transport(ts, row)
            return ts
        else:
            return dvb.Transport(0, 0)

    def save_sat_param(self, ts_key, dsc):
        c = self.connection.cursor()

        c.execute('''select * from ts_params_sat where ts_key = ?''',
                  [ts_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into ts_params_sat
                      (ts_key, freq, polarization, roll_off,
                      modulation_system,
                      modulation_type, symbol_rate, fec_inner)
                      values(?, ?, ?, ?, ?, ?, ?, ?)''',
                      [ts_key,
                       dsc.frequency,
                       dsc.polarization,
                       dsc.roll_off,
                       dsc.modulation_system,
                       dsc.modulation_type,
                       dsc.symbol_rate,
                       dsc.fec_inner])
        else:
            if (row['freq'] != dsc.frequency or
              row['roll_off'] != dsc.roll_off or
              row['modulation_system'] != dsc.modulation_system or
              row['modulation_type'] != dsc.modulation_type or
              row['symbol_rate'] != dsc.symbol_rate or
              row['fec_inner'] != dsc.fec_inner):
                c.execute('''update ts_params_sat
                          set freq = ?, roll_off = ?, modulation_system = ?,
                          modulation_type = ?, symbol_rate = ?, fec_inner = ?
                          where ts_key = ?''',
                          [dsc.frequency,
                           dsc.roll_off,
                           dsc.modulation_system,
                           dsc.modulation_type,
                           dsc.symbol_rate,
                           dsc.fec_inner,
                           ts_key])
        return

    def _get_default_authority(self, svc_key):
        c = self.connection.cursor()
        c.execute('''select default_authority
                  from default_authorities
                  where svc_key = ?''', [svc_key])
        row = c.fetchone()
        if (not row or row[0] is None):
            default_authority = ""
        else:
            default_authority = row[0]
        return default_authority

    def save_event(self, onid, tsid, svid, svc_key, version_number, event):
        start_time = dvbsi.dvbdate_to_unixtime(event.start_time)
        end_time = start_time + dvbsi.dvbduration_to_seconds(event.duration)
        c = self.connection.cursor()

        c.execute('''select * from events
                  where svc_key = ? and evid = ?''',
                  [svc_key, event.event_id])
        row = c.fetchone()
        if (not row):
            # inserting event is applied immediately
            c.execute('''insert into events
                      (svc_key, evid, start_time, end_time, version_number)
                      values (?, ?, ?, ?, ?)''',
                      [svc_key, event.event_id,
                       start_time, end_time, version_number])
        elif (row['start_time'] != start_time or
              row['end_time'] != end_time or
              row['version_number'] != version_number):
            # updating event is applied immediately
            c.execute('''update events
                      set start_time = ?, end_time = ?, version_number = ?
                      where svc_key = ? and evid = ?''',
                      [start_time, end_time, version_number,
                       svc_key, event.event_id])

        c.execute('''select evt_key from events
                  where svc_key = ? and evid = ?''',
                  [svc_key, event.event_id])
        row = c.fetchone()
        evt_key = row['evt_key']

        for raw_dsc in event.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_SHORT_EVENT):
                dsc = dvbsi.ShortEventDescriptor(raw_dsc.data)
                self.save_event_text(evt_key, dsc)
            elif (raw_dsc.tag == dvbsi.DTAG_EXTENDED_EVENT):
                dsc = dvbsi.ExtendedEventDescriptor(raw_dsc.data)
                self.save_event_extended(evt_key, dsc)
            elif (raw_dsc.tag == dvbsi.DTAG_PARENTAL_RATING):
                dsc = dvbsi.ParentalRatingDescriptor(raw_dsc.data)
                self.save_event_parental_rating(evt_key, dsc)
            elif (raw_dsc.tag == dvbsi.DTAG_CONTENT):
                dsc = dvbsi.ContentDescriptor(raw_dsc.data)
                self.save_event_genres(evt_key, dsc)

        prog_crid = None
        prog_imi = None
        season = 0
        episode = 0
        total_episodes = 0

        def_auth = self._get_default_authority(svc_key)

        # save series CRID & find program CRID
        for raw_dsc in event.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_CONTENT_IDENTIFIER):
                dsc = dvbsi.ContentIdentifierDescriptor(raw_dsc.data)
                for dvb_crid in dsc.crids:
                    if (dvb_crid.location != 0):
                        continue
                    if (dvb_crid.crid_type == dtg.CRID_TYPE_SERIES_CRID
                     or dvb_crid.crid_type == dvbsi.CRID_TYPE_SERIES_CRID):
                        crid, imi = self.make_crid_imi(def_auth,
                                                       dvb_crid.crid_byte)
                        self.save_series_crid(evt_key, crid)
                    elif (dvb_crid.crid_type == dtg.CRID_TYPE_PROGRAM_CRID or
                          dvb_crid.crid_type == dvbsi.CRID_TYPE_PROGRAM_CRID):
                        crid, imi = self.make_crid_imi(def_auth,
                                                       dvb_crid.crid_byte)
                        prog_crid = crid
                        prog_imi = imi
            elif (raw_dsc.tag == boxer.DTAG_CBI):
                dsc = boxer.CBIDescriptor(raw_dsc.data)
                if (dsc.cbitype == 1):
                    info = dsc.basic_info
                    season = info.season
                    episode = info.episode
                    total_episodes = info.episode_total
                    if (info.series_id != 0):
                        cbi_def_auth = "%x.%x.%x" % (onid, tsid, svid)
                        crid = cbi_def_auth + "/" + hex(info.series_id)
                        self.save_series_crid(evt_key, crid)
                        if (info.episode != 0 and prog_crid is None):
                            crid += "/" + str(info.season)
                            crid += "/" + str(info.episode)
                            prog_crid = crid

        # save program CRID
        if (prog_crid or prog_imi or season or episode or total_episodes):
            self.save_program(evt_key, prog_crid, prog_imi, season,
                              episode, total_episodes)

    def save_event_text(self, evt_key, dsc):
        raw_str = dsc.event_name
        if (len(raw_str) > 0 and raw_str[0] == 0x1f):
            #evt_name = dtg.decompress_string(raw_str)
            #evt_name = huffman.decode_freesat(raw_str).decode("utf-8")
            pass
        else:
            charset, used = dvbsi.dvb_charset(raw_str)
            evt_name = raw_str[used:].decode(charset, 'replace')

        raw_str = dsc.text
        if (len(raw_str) > 0 and raw_str[0] == 0x1f):
            #short_text = dtg.decompress_string(raw_str)
            #short_text = huffman.decode_freesat(raw_str).decode("utf-8")
            pass
        else:
            charset, used = dvbsi.dvb_charset(raw_str)
            short_text = raw_str[used:].decode(charset, 'replace')

        c = self.connection.cursor()
        c.execute('''select * from event_texts
                  where evt_key = ? and lang = ?''',
                  [evt_key, dsc.language_code])

        row = c.fetchone()
        if (not row):
            c.execute('''insert into event_texts
                      (evt_key, lang, evt_name, short_text)
                      values (?, ?, ?, ?)''',
                      [evt_key, dsc.language_code, evt_name, short_text])
        elif (row['evt_name'] != evt_name or row['short_text'] != short_text):
            c.execute('''update event_texts
                      set evt_name = ?, short_text = ?
                      where evt_key = ? and lang = ?''',
                      [evt_name, short_text, evt_key, dsc.language_code])

    def save_event_extended(self, evt_key, dsc):
        raw_str = dsc.text
        if (len(raw_str) > 0 and raw_str[0] == 0x1f):
            #extended_text = dtg.decompress_string(raw_str)
            #extended_text = huffman.decode_freesat(raw_str).decode("utf-8")
            pass
        else:
            charset, used = dvbsi.dvb_charset(raw_str)
            extended_text = raw_str[used:].decode(charset, 'replace')

        c = self.connection.cursor()
        c.execute('''select * from event_texts
                  where evt_key = ? and lang = ?''',
                  [evt_key, dsc.language_code])

        row = c.fetchone()
        if (not row):
            c.execute('''insert into event_texts
                      (evt_key, lang, extended_text)
                      values (?, ?, ?)''',
                      [evt_key, dsc.language_code, extended_text])
        elif (row['extended_text'] != extended_text):
            c.execute('''update event_texts
                      set extended_text = ?
                      where evt_key = ? and lang = ?''',
                      [extended_text, evt_key, dsc.language_code])

    def save_event_genres(self, evt_key, dsc):
        c = self.connection.cursor()
        c.execute('''delete from event_genres where evt_key = ?;''', [evt_key])
        for content in dsc.contents:
            c.execute('''insert into event_genres
                      (evt_key, level_1, level_2, user_byte)
                      values (?, ?, ?, ?);''',
                      [evt_key,
                       content.content_nibble_level_1,
                       content.content_nibble_level_2,
                       content.user_byte])

    def save_event_parental_rating(self, evt_key, dsc):
        c = self.connection.cursor()
        c.execute('''delete from event_parental_ratings where evt_key = ?;''',
                  [evt_key])
        for rating in dsc.parental_ratings:
            c.execute('''insert into event_parental_ratings
                      (evt_key, country_code, rating)
                      values (?, ?, ?);''',
                      [evt_key, rating.country_code, rating.rating])

    def save_series_crid(self, evt_key, series_crid):
        c = self.connection.cursor()
        c.execute('''select * from series_crids
                  where evt_key = ? and series_crid = ?''',
                  [evt_key, series_crid])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into series_crids (evt_key, series_crid)
                      values (?, ?)''', [evt_key, series_crid])

    def save_program(self, evt_key, prog_crid, imi, season, episode,
                     total_episodes):
        c = self.connection.cursor()
        c.execute('''select * from programs where evt_key = ?''',
                  [evt_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into programs
                      (evt_key, prog_crid, imi, season, episode,
                      total_episodes) values (?, ?, ?, ?, ?, ?)''',
                      [evt_key, prog_crid, imi, season, episode,
                       total_episodes])
        elif (row['prog_crid'] != prog_crid or row['imi'] != imi or
              row['season'] != season or row['episode'] != episode or
              row['total_episodes'] != total_episodes):
            c.execute('''update programs
                      set prog_crid = ?, imi = ?, season = ?, episode = ?,
                      total_episodes = ? where evt_key = ?''',
                      [prog_crid, imi, season, episode, total_episodes,
                       evt_key])

    def make_crid_imi(self, default_authority, crid_byte):
        # separate crid_byte into three fields: authority, data and imi
        if (crid_byte.startswith("crid://")):
            crid_byte = crid_byte[7:]
        authority, slash, data_imi = crid_byte.partition("/")
        if (authority == ''):
            authority = default_authority
        i = data_imi.rfind("#", len(data_imi) - 3)
        if (i > 0):
            data = data_imi[0:i]
            imi = data_imi[i:]
        else:
            data = data_imi
            imi = ""
        return "/".join([authority, data]), imi

    def save_lcn(self, svc_key, visible, selectable, lcn):
        c = self.connection.cursor()
        query = 'select visible, selectable, lcn from lcn where svc_key = ?'
        c.execute(query, [svc_key])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into lcn (svc_key, visible, selectable, lcn)
                      values (?, ?, ?, ?)''',
                      [svc_key, visible, selectable, lcn])
        elif (row['lcn'] != lcn or
              row['visible'] != visible or
              row['selectable'] != selectable):
            c.execute('''update lcn set visible = ?, selectable = ?, lcn = ?
                      where svc_key = ?''',
                      [visible, selectable, lcn, svc_key])

    def _row_to_event(self, row):
        c = self.connection.cursor()
        evt_key = row['evt_key']
        evt = dvb.Event(evt_key,
                        row['evid'],
                        row['start_time'],
                        row['end_time'],
                        row['evt_name'],
                        row['svc_key'],
                        row['svc_name'],
                        row['ts_key'])
        if (row['prog_crid']):
            evt.prog_crid = row['prog_crid']
        if (row['imi']):
            evt.imi = row['imi']
        evt.season = row['season']
        evt.episode = row['episode']
        evt.total_episodes = row['total_episodes']

        evt.time_offset = self.read_time_offset(evt.ts_key)

        q = 'select * from series_crids where evt_key = ?'
        c.execute(q, [evt_key])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                evt.series_crids.append(row['series_crid'])
        return evt

    def read_event(self, evt_key):
        c = self.connection.cursor()
        q = '''select * from events
            join services on events.svc_key = services.svc_key
            left outer join event_texts
             on events.evt_key = event_texts.evt_key
            left outer join programs
             on events.evt_key = programs.evt_key
            where events.evt_key = ?'''
        c.execute(q, [evt_key])
        row = c.fetchone()
        if (not row):
            return None
        evt = self._row_to_event(row)
        return evt

    def get_ts_key(self, tsid, onid, nid, src_key=0):
        c = self.connection.cursor()
        c.execute('''select ts_key from transports
                  where nid = ? and tsid = ? and onid = ? and src_key = ?''',
                  [nid, tsid, onid, src_key])
        row = c.fetchone()
        if (not row):
            return None
        return row[0]

    def get_ts_key2(self, tsid, onid, src_key=0):
        c = self.connection.cursor()
        c.execute('''select ts_key from transports
                  where tsid = ? and onid = ? and src_key = ?''',
                  [tsid, onid, src_key])
        row = c.fetchone()
        if (not row):
            return None
        return row[0]

    def get_svc_key(self, tsid, onid, svid, src_key, nid=-1):
        c = self.connection.cursor()
        if (nid == -1):
            c.execute(''' select svc_key from services
                      inner join transports
                      on services.ts_key = transports.ts_key
                      where tsid = ? and onid = ? and svid = ?
                            and src_key = ?''',
                      [tsid, onid, svid, src_key])
        else:
            c.execute(''' select svc_key from services
                      inner join transports
                      on services.ts_key = transports.ts_key
                      where tsid = ? and onid = ? and svid = ?
                      and nid = ? and src_key = ?''',
                      [tsid, onid, svid, nid, src_key])
        row = c.fetchone()
        if (not row):
            return None
        return row[0]

    def get_svc_key2(self, ts_key, svid):
        c = self.connection.cursor()
        c.execute(''' select svc_key from services
                  where ts_key = ? and svid = ?''',
                  [ts_key, svid])
        row = c.fetchone()
        if (not row):
            return None
        return row[0]

    def reset_temp_services(self):
        c = self.connection.cursor()
        c.execute('''delete from services_temp''')

    def insert_temp_service(self, ts_key, service):
        for dsc in service.descriptors:
            if (dsc.tag == dvbsi.DTAG_SERVICE):
                svc_dsc = dvbsi.ServiceDescriptor(dsc.data)
                break
        else:
            # no service descriptor: nothings to be done.
            return

        raw_name = svc_dsc.service_name
        charset, used = dvbsi.dvb_charset(raw_name)
        svc_name = raw_name[used:].decode(charset, 'replace')

        raw_name = svc_dsc.service_provider_name
        charset, used = dvbsi.dvb_charset(raw_name)
        prv_name = raw_name[used:].decode(charset, 'replace')

        c = self.connection.cursor()
        c.execute('''insert or replace into services_temp
                  (ts_key, svid, svc_name, prov_name, type, ca)
                  values(?, ?, ?, ?, ?, ?)''',
                  [ts_key, service.service_id, svc_name, prv_name,
                   svc_dsc.service_type, service.free_ca_mode])

    def insert_temp_service_list(self, ts_key, service_list):
        c = self.connection.cursor()
        for service in service_list:
            c.execute('''insert or replace into services_temp
                      (ts_key, svid, type) values (?, ?, ?)''',
                      [ts_key, service.service_id, service.service_type])

    def insert_temp_service2(self, ts_key, svid):
        c = self.connection.cursor()
        c.execute(''' select svid from services_temp
                  where ts_key = ? and svid = ?''',
                  [ts_key, svid])
        row = c.fetchone()
        if (not row):
            c.execute('''insert into services_temp
                      (ts_key, svid, type) values (?, ?, 0)''',
                      [ts_key, svid])

    def get_temp_services(self):
        c = self.connection.cursor()
        c.execute('''select * from services_temp''')
        row = c.fetchall()
        if (not row):
            return []
        return row

    def get_services_to_be_removed(self):
        c = self.connection.cursor()
        c.execute('''select OLD.svc_key, OLD.ts_key, OLD.svid, OLD.svc_name,
                  OLD.prov_name, OLD.type, OLD.ca
                  from services as OLD
                  left outer join services_temp as NEW
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where NEW.svid is null and OLD.ts_key
                  in (select distinct ts_key from services_temp);''')
        row = c.fetchall()
        if (not row):
            return []
        return row

    def get_services_to_be_updated(self):
        c = self.connection.cursor()
        c.execute('''select OLD.svc_key, NEW.ts_key, NEW.svid, NEW.svc_name,
                  NEW.prov_name, NEW.type, NEW.ca
                  from services_temp as NEW
                  join services as OLD
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where OLD.svc_name != NEW.svc_name
                  or OLD.prov_name != NEW.prov_name
                  or OLD.type != NEW.type
                  or OLD.ca != NEW.ca;''')
        row = c.fetchall()
        if (not row):
            return []
        return row

    def get_services_to_be_inserted(self):
        c = self.connection.cursor()
        c.execute('''select NEW.ts_key, NEW.svid, NEW.svc_name, NEW.prov_name,
                  NEW.type, NEW.ca
                  from services_temp as NEW
                  left outer join services as OLD
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where OLD.svid is null;''')
        row = c.fetchall()
        if (not row):
            return []
        return row

    def apply_temp_services(self):
        c = self.connection.cursor()

        # delete services
        c.execute('''delete from services
                  where svc_key in (
                  select OLD.svc_key
                  from services as OLD
                  left outer join services_temp as NEW
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where NEW.svid is null and OLD.ts_key in
                  (select distinct ts_key from services_temp));''')

        # modify services
        c.execute('''replace into services
                  (svc_key, ts_key, svid, svc_name, prov_name, type, ca)
                  select OLD.svc_key, NEW.ts_key, NEW.svid, NEW.svc_name,
                  NEW.prov_name, NEW.type, NEW.ca
                  from services_temp as NEW
                  join services as OLD
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where OLD.svc_name != NEW.svc_name
                  or OLD.prov_name != NEW.prov_name
                  or OLD.type != NEW.type
                  or OLD.ca != NEW.ca''')

        # insert services
        c.execute('''insert into services
                  (ts_key, svid, svc_name, prov_name, type, ca)
                  select NEW.ts_key, NEW.svid, NEW.svc_name, NEW.prov_name,
                  NEW.type, NEW.ca
                  from services_temp as NEW
                  left outer join services as OLD
                  on OLD.svid = NEW.svid and OLD.ts_key = NEW.ts_key
                  where OLD.svid is null;''')

    def save_bouquet_service(self, bid, tsid, onid, svid, nid):
        c = self.connection.cursor()
        c.execute('''insert or ignore into bouquet_services
                  (bid, svc_key) values (?,
                  (select svc_key from services
                   inner join transports
                   on services.ts_key = transports.ts_key
                   where tsid = ? and onid = ? and svid = ?
                   and nid = ?))''',
                  [bid, tsid, onid, svid, nid])

    def delete_all_streams_of(self, svc_key):
        c = self.connection.cursor()
        c.execute('''delete from streams where svc_key = ?''',
                  [svc_key])

    def save_stream(self, svc_key, stream, component_tag, stream_class):
        c = self.connection.cursor()
        c.execute('''insert into streams
                  (svc_key, stream_type, pid, component_tag, stream_class)
                  values (?, ?, ?, ?, ?)''',
                  [svc_key, stream.stream_type, stream.pid, component_tag,
                   stream_class])
        c.execute('''select last_insert_rowid() from streams;''')
        row = c.fetchone()
        if (not row):
            return 0
        return row[0]

    def save_audio_stream(self, strm_key, lang, codec, audio_type, mix_type,
                          editorial_classification, num_channel):
        c = self.connection.cursor()
        c.execute('''insert into streams_audio
                  (strm_key, lang, codec, audio_type, mix_type,
                  editorial_classification, num_channel)
                  values (?, ?, ?, ?, ?, ?, ?)''',
                  [strm_key, lang, codec, audio_type, mix_type,
                   editorial_classification, num_channel])

    def save_dvb_subtitle_stream(self, strm_key, lang, subtitling_type,
                                 composition_page_id, ancillary_page_id):
        c = self.connection.cursor()
        c.execute('''insert into streams_dvb_subtitle
                  (strm_key, lang,
                   subtitling_type, composition_page_id, ancillary_page_id)
                  values (?, ?, ?, ?, ?)''',
                  [strm_key, lang,
                   subtitling_type, composition_page_id, ancillary_page_id])

    def save_teletext_stream(self, strm_key, lang, teletext_type,
                             magazine_number, page_number):
        c = self.connection.cursor()
        c.execute('''insert into streams_teletext
                  (strm_key, lang, teletext_type, magazine_number, page_number)
                  values (?, ?, ?, ?, ?)''',
                  [strm_key, lang, teletext_type,
                   magazine_number, page_number])

    def _save_rsvs_program(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_program where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (not row):
            q = '''insert into rsvs_program (rsv_key, prog_crid)
                values (?, ?)'''
            c.execute(q, [rsv.rsv_key, rsv.prog_crid])
        elif (row['prog_crid'] != rsv.prog_crid):
            q = '''update rsvs_program set prog_crid = ? where rsv_key = ?'''
            c.execute(q, [rsv.prog_crid, rsv.rsv_key])

    def _save_rsvs_series(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_series where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (not row):
            q = '''insert into rsvs_series (rsv_key, series_id,
                max_space, del_day, del_number, del_space, del_played_first)
                values (?, ?, ?, ?, ?, ?, ?)'''
            c.execute(q, [rsv.rsv_key, rsv.series_id,
                          rsv.max_space, rsv.del_day, rsv.del_number,
                          rsv.del_space, rsv.del_played_first])
        elif (row['series_id'] != rsv.series_id or
              row['max_space'] != rsv.max_space or
              row['del_day'] != rsv.del_day or
              row['del_number'] != rsv.del_number or
              row['del_space'] != rsv.del_space or
              row['del_played_first'] != rsv.del_played_first):
            q = '''update rsvs_series set series_id = ?, max_space = ?,
                del_day = ?, del_number = ?, del_space = ?,
                del_played_first = ? where rsv_key = ?'''
            c.execute(q, [rsv.series_id, rsv.max_space, rsv.del_day,
                          rsv.del_number, rsv.del_space,
                          rsv.del_played_first, rsv.rsv_key])

    def _save_rsvs_daily(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_daily where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (not row):
            q = '''insert into rsvs_daily (rsv_key, yyyymmdd, hhmmss,
                duration, day_of_week) values (?, ?, ?, ?, ?)'''
            c.execute(q, [rsv.rsv_key, rsv.yyyymmdd, rsv.hhmmss,
                          rsv.duration, rsv.day_of_week])
        elif (row['yyyymmdd'] != rsv.yyyymmdd or
              row['hhmmss'] != rsv.hhmmss or
              row['duration'] != rsv.duration or
              row['day_of_week'] != rsv.day_of_week):
            q = '''update rsvs_daily set yyyymmdd = ?, hhmmss = ?,
                duration = ?, day_of_week = ? where rsv_key = ?'''
            c.execute(q, [rsv.yyyymmdd, rsv.hhmmss, rsv.duration,
                          rsv.day_of_week, rsv.rsv_key])

    def save_reservation(self, rsv):
        c = self.connection.cursor()
        if (rsv.rsv_key != 0):
            q = 'select * from reservations where rsv_key = ?'
            c.execute(q, [rsv.rsv_key])
            row = c.fetchone()
            if (not row):
                rsv.rsv_key = 0
        if (rsv.rsv_key == 0):
            q = '''insert into reservations (deactivated, rsv_name,
                description, action, target, svc_key, evid, do_when,
                replan_when, priority, directory)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            c.execute(q, [rsv.deactivated, rsv.rsv_name, rsv.description,
                          rsv.action, rsv.target, rsv.svc_key, rsv.evid,
                          rsv.do_when, rsv.replan_when, rsv.priority,
                          rsv.directory])
            c.execute('select last_insert_rowid()')
            row = c.fetchone()
            rsv.rsv_key = row[0]
            if (isinstance(rsv, dvb.SBR)):
                self._save_rsvs_series(rsv)
            elif (isinstance(rsv, dvb.PBR)):
                self._save_rsvs_program(rsv)
            elif (isinstance(rsv, dvb.ReservationDaily)):
                self._save_rsvs_daily(rsv)
            return rsv.rsv_key
        if (row['deactivated'] != rsv.deactivated
         or row['rsv_name'] != rsv.rsv_name
         or row['description'] != rsv.description
         or row['action'] != rsv.action
         or row['target'] != rsv.target
         or row['svc_key'] != rsv.svc_key
         or row['evid'] != rsv.evid
         or row['do_when'] != rsv.do_when
         or row['replan_when'] != rsv.replan_when
         or row['priority'] != rsv.priority
         or row['directory'] != rsv.directory):
            q = '''update reservations set deactivated = ?, rsv_name = ?,
                description = ?, action = ?, target = ?, svc_key = ?,
                evid = ?, do_when = ?, replan_when = ?, priority = ?,
                directory = ?  where rsv_key = ?'''
            c.execute(q, [rsv.deactivated, rsv.rsv_name, rsv.description,
                          rsv.action, rsv.target, rsv.svc_key, rsv.evid,
                          rsv.do_when, rsv.replan_when, rsv.priority,
                          rsv.directory, rsv.rsv_key])
        if (isinstance(rsv, dvb.SBR)):
            self._save_rsvs_series(rsv)
        elif (isinstance(rsv, dvb.PBR)):
            self._save_rsvs_program(rsv)
        elif (isinstance(rsv, dvb.ReservationDaily)):
            self._save_rsvs_daily(rsv)
        return rsv.rsv_key

    def _row_to_reservation(self, row):
        if (row['target'] == dvb.Reservation.TARGET_EVENT):
            if (row['action'] == dvb.Reservation.ACTION_RECORD):
                rsv = dvb.EBR(row['rsv_name'], row['svc_key'], row['evid'])
            elif (row['action'] == dvb.Reservation.ACTION_WATCH):
                rsv = dvb.EBW(row['rsv_name'], row['svc_key'], row['evid'])
            else:
                rsv = dvb.ReservationEvent(row['rsv_name'], row['action'])
                rsv.svc_key = row['svc_key']
                rsv.evid = row['evid']
        elif (row['target'] == dvb.Reservation.TARGET_PROGRAM_CRID):
            rsv = dvb.PBR(row['rsv_name'], row['svc_key'], row['evid'], "")
        elif (row['target'] == dvb.Reservation.TARGET_SERIES_CRID):
            rsv = dvb.SBR(row['rsv_name'], row['svc_key'], row['evid'], "")
        elif (row['do_when'] == 1):
            if (row['action'] == dvb.Reservation.ACTION_RECORD and
                row['target'] == dvb.Reservation.TARGET_SERVICE):
                rsv = dvb.TBR(row['rsv_name'], row['svc_key'], 0, 0, 0, 0)
                rsv.evid = row['evid']
            elif (row['action'] == dvb.Reservation.ACTION_WATCH and
                  row['target'] == dvb.Reservation.TARGET_SERVICE):
                rsv = dvb.TBW(row['rsv_name'], row['svc_key'], 0, 0, 0, 0)
                rsv.evid = row['evid']
            else:
                rsv = dvb.ReservationDaily(row['rsv_name'], row['action'],
                                           0, 0, 0)
                rsv.target = row['target']
                rsv.svc_key = row['svc_key']
                rsv.evid = row['evid']
        else:
            rsv = dvb.Reservation(row['rsv_name'], row['action'])
            rsv.target = row['target']
            rsv.svc_key = row['svc_key']
            rsv.evid = row['evid']
        rsv.rsv_key = row['rsv_key']
        rsv.deactivated = row['deactivated']
        rsv.description = row['description']
        rsv.do_when = row['do_when']
        rsv.replan_when = row['replan_when']
        rsv.booked_time = row['booked_time']
        rsv.priority = row['priority']
        rsv.directory = row['directory']
        rsv.svc_name = row['svc_name']
        return rsv

    def remove_reservation(self, rsv_key):
        c = self.connection.cursor()
        q = '''delete from reservations where rsv_key = ?'''
        c.execute(q, [rsv_key])

    def read_all_reservations(self):
        reservations = []
        c = self.connection.cursor()
        q = '''select * from reservations
            join services on reservations.svc_key = services.svc_key'''
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            rsv = self._row_to_reservation(row)
            reservations.append(rsv)
        for rsv in reservations:
            if (isinstance(rsv, dvb.SBR)):
                self._get_rsvs_series(rsv)
            elif (isinstance(rsv, dvb.PBR)):
                self._get_rsvs_program(rsv)
            elif (isinstance(rsv, dvb.ReservationDaily)):
                self._get_rsvs_daily(rsv)
            rsv.rsv_links = self.get_rsv_links_of_rsv(rsv)
        return reservations

    def read_reservation(self, rsv_key):
        c = self.connection.cursor()
        q = '''select * from reservations
            join services on reservations.svc_key = services.svc_key
            where rsv_key = ?'''
        c.execute(q, [rsv_key])
        row = c.fetchone()
        if (not row):
            return None
        rsv = self._row_to_reservation(row)
        if (isinstance(rsv, dvb.SBR)):
            self._get_rsvs_series(rsv)
        elif (isinstance(rsv, dvb.PBR)):
            self._get_rsvs_program(rsv)
        elif (isinstance(rsv, dvb.ReservationDaily)):
            self._get_rsvs_daily(rsv)
        rsv.rsv_links = self.get_rsv_links_of_rsv(rsv)
        return rsv

    def get_ebr_key(self, svc_key, evid):
        c = self.connection.cursor()
        q = '''select rsv_key from reservations where svc_key = ?
            and evid = ? and action = ? and target = ?'''
        action = dvb.Reservation.ACTION_RECORD
        target = dvb.Reservation.TARGET_EVENT
        c.execute(q, [svc_key, evid, action, target])
        row = c.fetchone()
        if (row):
            return row['rsv_key']
        return 0

    def get_pbr_key(self, prog_crid):
        c = self.connection.cursor()
        q = '''select rsv_key from rsvs_program where prog_crid = ?'''
        c.execute(q, [prog_crid])
        row = c.fetchone()
        if (row):
            return row['rsv_key']
        return 0

    def get_sbr_key(self, series_id):
        c = self.connection.cursor()
        q = '''select rsv_key from rsvs_series where series_id = ?'''
        c.execute(q, [series_id])
        row = c.fetchone()
        if (row):
            return row['rsv_key']
        return 0

    def get_tbr_key(self, svc_key, yyyymmdd, hhmmss, duration):
        c = self.connection.cursor()
        q = '''select rsvs_daily.rsv_key from rsvs_daily join reservations
            on rsvs_daily.rsv_key = reservations.rsv_key
            where svc_key = ? and action = ? and target = ?
            and yyyymmdd = ? and hhmmss = ? and duration = ?'''
        action = dvb.Reservation.ACTION_RECORD
        target = dvb.Reservation.TARGET_SERVICE
        c.execute(q, [svc_key, action, target, yyyymmdd, hhmmss, duration])
        row = c.fetchone()
        if (row):
            return row['rsv_key']
        return 0

    def get_rsv_links_of_rsv(self, rsv):
        rsv_links = []
        c = self.connection.cursor()
        q = '''select sched_key, pathname from rsv_links
            where rsv_key = ? order by sched_key, pathname'''
        c.execute(q, [rsv.rsv_key])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                sched_key = row['sched_key'] if (row['sched_key']) else 0
                pathname = row['pathname'] if (row['pathname']) else ""
                rsv_link = dvb.RsvLink(rsv.rsv_key, sched_key, pathname)
                rsv_links.append(rsv_link)
        return rsv_links

    def _get_rsvs_daily(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_daily where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (row):
            rsv.yyyymmdd = row['yyyymmdd']
            rsv.hhmmss = row['hhmmss']
            rsv.duration = row['duration']
            rsv.day_of_week = row['day_of_week']

    def _get_rsvs_program(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_program where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (row):
            rsv.prog_crid = row['prog_crid']

    def _get_rsvs_series(self, rsv):
        c = self.connection.cursor()
        q = 'select * from rsvs_series where rsv_key = ?'
        c.execute(q, [rsv.rsv_key])
        row = c.fetchone()
        if (row):
            rsv.series_id = row['series_id']
            rsv.max_space = row['max_space']
            rsv.del_day = row['del_day']
            rsv.del_number = row['del_number']
            rsv.del_space = row['del_space']
            rsv.del_played_first = row['del_played_first']

    def save_schedule(self, sched):
        c = self.connection.cursor()
        if (sched.sched_key != 0):
            q = 'select * from schedules where sched_key = ?'
            c.execute(q, [sched.sched_key])
            row = c.fetchone()
            if (not row):
                sched.sched_key = 0

        if (sched.sched_key == 0):
            q = '''insert into schedules (sched_name, description, action,
                start_time, end_time, status, actual_start_time,
                running_time, svc_key, evid, prog_crid, season, episode,
                total_episodes, imi, split_number, total_splits, conflict,
                start_padding, end_padding) values (?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            c.execute(q, [sched.sched_name, sched.description, sched.action,
                          sched.start_time, sched.end_time, sched.status,
                          sched.actual_start_time, sched.running_time,
                          sched.svc_key, sched.evid, sched.prog_crid,
                          sched.season, sched.episode, sched.total_episodes,
                          sched.imi, sched.split_number, sched.total_splits,
                          sched.conflict, sched.start_padding,
                          sched.end_padding])
            c.execute('select last_insert_rowid()')
            row = c.fetchone()
            sched.sched_key = row[0]
            return

        if (row['sched_name'] != sched.sched_name
         or row['description'] != sched.description
         or row['action'] != sched.action
         or row['start_time'] != sched.start_time
         or row['end_time'] != sched.end_time
         or row['status'] != sched.status
         or row['actual_start_time'] != sched.actual_start_time
         or row['running_time'] != sched.running_time
         or row['svc_key'] != sched.svc_key
         or row['evid'] != sched.evid
         or row['prog_crid'] != sched.prog_crid
         or row['season'] != sched.season
         or row['episode'] != sched.episode
         or row['total_episodes'] != sched.total_episodes
         or row['imi'] != sched.imi
         or row['split_number'] != sched.split_number
         or row['total_splits'] != sched.total_splits
         or row['conflict'] != sched.conflict
         or row['start_padding'] != sched.start_padding
         or row['end_padding'] != sched.end_padding):
            q = '''update schedules set sched_name = ?, description = ?,
                action = ?, start_time = ?, end_time = ?, status = ?,
                actual_start_time = ?, running_time = ?, svc_key = ?,
                evid = ?, prog_crid = ?, season = ?, episode = ?,
                total_episodes = ?, imi = ?, split_number = ?,
                total_splits = ?, conflict = ?, start_padding = ?,
                end_padding = ? where sched_key = ?'''
            c.execute(q, [sched.sched_name, sched.description, sched.action,
                          sched.start_time, sched.end_time, sched.status,
                          sched.actual_start_time, sched.running_time,
                          sched.svc_key, sched.evid, sched.prog_crid,
                          sched.season, sched.episode, sched.total_episodes,
                          sched.imi, sched.split_number, sched.total_splits,
                          sched.conflict, sched.start_padding,
                          sched.end_padding, sched.sched_key])

    def remove_schedule(self, sched_key):
        c = self.connection.cursor()
        q = '''delete from schedules where sched_key = ?'''
        c.execute(q, [sched_key])

    def link_rsv_sched(self, rsv, sched):
        c = self.connection.cursor()
        q = 'select * from rsv_links where rsv_key = ? and sched_key = ?'
        c.execute(q, [rsv.rsv_key, sched.sched_key])
        row = c.fetchone()
        if (not row):
            q = '''insert into rsv_links (rsv_key, sched_key)
                values (?, ?)'''
            c.execute(q, [rsv.rsv_key, sched.sched_key])
            rsv_link = dvb.RsvLink(rsv.rsv_key, sched.sched_key, "")
            rsv.rsv_links.append(rsv_link)
            sched.rsv_links.append(rsv_link)
        return

    def unlink_rsv_sched(self, rsv, sched):
        c = self.connection.cursor()
        if (rsv):
            q = 'delete from rsv_links where rsv_key = ? and sched_key = ?'
            c.execute(q, [rsv.rsv_key, sched.sched_key])
            rsv_link = dvb.RsvLink(rsv.rsv_key, sched.sched_key, "")
            try:
                rsv.rsv_links.remove(rsv_link)
            except:
                pass
        else:
            q = 'delete from rsv_links where rsv_key = NULL and sched_key = ?'
            c.execute(q, [sched.sched_key])
            rsv_link = dvb.RsvLink(None, sched.sched_key, "")
        try:
            sched.rsv_links.remove(rsv_link)
        except:
            pass
        return

    def save_rsv_sched_pathname(self, rsv, sched, pathname):
        c = self.connection.cursor()
        if (rsv is None):
            q = 'select * from rsv_links where sched_key = ?'
            c.execute(q, [sched.sched_key])
            row = c.fetchone()
            if (not row):
                q = '''insert into rsv_links (sched_key, pathname)
                    values (?, ?)'''
                c.execute(q, [sched.sched_key, pathname])
            elif (row['pathname'] != pathname):
                q = 'update rsv_links set pathname = ? where sched_key = ?'
                c.execute(q, [pathname, sched.sched_key])
            return
        q = 'select * from rsv_links where rsv_key = ? and sched_key = ?'
        c.execute(q, [rsv.rsv_key, sched.sched_key])
        row = c.fetchone()
        if (not row):
            q = '''insert into rsv_links (rsv_key, sched_key, pathname)
                values (?, ?, ?)'''
            c.execute(q, [rsv.rsv_key, sched.sched_key, pathname])
        elif (row['pathname'] != pathname):
            q = '''update rsv_links set pathname = ?
                where rsv_key = ? and sched_key = ?'''
            c.execute(q, [pathname, rsv.rsv_key, sched.sched_key])

    def read_rsv_sched_pathname(self, rsv, sched):
        pathname = None
        c = self.connection.cursor()
        if (rsv is None):
            q = 'select * from rsv_links where sched_key = ?'
            c.execute(q, [sched.sched_key])
            row = c.fetchone()
            if (row):
                pathname = row['pathname']
            return pathname
        q = 'select * from rsv_links where rsv_key = ? and sched_key = ?'
        c.execute(q, [rsv.rsv_key, sched.sched_key])
        row = c.fetchone()
        if (row):
            pathname = row['pathname']
        return pathname

    def get_rsv_links_of_schedule(self, sched):
        rsv_links = []
        c = self.connection.cursor()
        q = '''select rsv_key, pathname from rsv_links
            where sched_key = ? order by rsv_key, pathname'''
        c.execute(q, [sched.sched_key])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                rsv_key = row['rsv_key'] if (row['rsv_key']) else 0
                pathname = row['pathname'] if (row['pathname']) else ""
                rsv_link = dvb.RsvLink(rsv_key, sched.sched_key, pathname)
                rsv_links.append(rsv_link)
        return rsv_links

    def _row_to_schedule(self, row):
        sched = dvb.Schedule(row['sched_name'], row['action'],
                             row['start_time'], row['end_time'])
        sched.sched_key = row['sched_key']
        sched.rsv_links = []
        sched.description = row['description']
        sched.status = row['status']
        sched.actual_start_time = row['actual_start_time']
        sched.running_time = row['running_time']
        sched.svc_key = row['svc_key']
        sched.svc_name = row['svc_name']
        sched.evid = row['evid']
        sched.prog_crid = row['prog_crid']
        sched.season = row['season']
        sched.episode = row['episode']
        sched.total_episodes = row['total_episodes']
        sched.imi = row['imi']
        sched.split_number = row['split_number']
        sched.total_splits = row['total_splits']
        sched.conflict = row['conflict']
        sched.start_padding = row['start_padding']
        sched.end_padding = row['end_padding']
        sched.time_offset = row['time_offset']
        return sched

    def read_schedules_of_rsv(self, rsv):
        schedules = []
        c = self.connection.cursor()
        q = '''select * from rsv_links
            join schedules on rsv_links.sched_key = schedules.sched_key
            join services on schedules.svc_key = services.svc_key
            join transports on transports.ts_key = services.ts_key
            where rsv_key = ?'''
        c.execute(q, [rsv.rsv_key])
        rows = c.fetchall()
        if rows is None:
            return schedules
        for row in rows:
            sched = self._row_to_schedule(row)
            schedules.append(sched)
        for sched in schedules:
            sched.rsv_links = self.get_rsv_links_of_schedule(sched)
        return schedules

    def read_schedule_of_period(self, action, svc_key, start_time, end_time):
        c = self.connection.cursor()
        q = '''select * from schedules
            join services on schedules.svc_key = services.svc_key
            join transports on transports.ts_key = services.ts_key
            where action = ? and schedules.svc_key = ? and start_time = ?
            and end_time = ?'''
        c.execute(q, [action, svc_key, start_time, end_time])
        row = c.fetchone()
        if row is None:
            return None
        sched = self._row_to_schedule(row)
        sched.rsv_links = self.get_rsv_links_of_schedule(sched)
        return sched

    def is_period_scheduled(self, action, svc_key, start_time, end_time):
        c = self.connection.cursor()
        q = '''select count(*) from schedules where action = ? and
            svc_key = ? and start_time = ? and end_time = ?'''
        c.execute(q, [action, svc_key, start_time, end_time])
        row = c.fetchone()
        if (row and row[0]):
            return True
        return False

    def is_moment_scheduled(self, action, svc_key, moment):
        c = self.connection.cursor()
        q = '''select count(*) from schedules where action = ? and
            svc_key = ? and start_time <= ? and ? <= end_time'''
        c.execute(q, [action, svc_key, moment, moment])
        row = c.fetchone()
        if (row and row[0]):
            return True
        return False

    def read_all_schedules(self):
        schedules = []
        c = self.connection.cursor()
        q = '''select * from schedules
            join services on schedules.svc_key = services.svc_key
            join transports on transports.ts_key = services.ts_key
            order by start_time, schedules.svc_key'''
        c.execute(q)
        rows = c.fetchall()
        if rows is None:
            return schedules
        for row in rows:
            sched = self._row_to_schedule(row)
            schedules.append(sched)
        for sched in schedules:
            sched.rsv_links = self.get_rsv_links_of_schedule(sched)
        return schedules

    def read_all_services(self, order_by=None):
        services = []
        c = self.connection.cursor()
        q = '''select services.svc_key, services.svc_name, prov_name, type,
            tsid, onid, nid, svid, services.ts_key,
            sources.src_key, delivery_system, lcn
            from (services join transports
                      on services.ts_key = transports.ts_key)
                  join sources
                      on transports.src_key = sources.src_key
                  left outer join lcn
                      on services.svc_key = lcn.svc_key'''
        if (order_by is not None and len(order_by)):
            q += ' ' + order_by
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            svc = dvb.Service(row['svc_key'], row['lcn'],
                              row['svc_name'], row['prov_name'],
                              row['type'],
                              row['tsid'], row['onid'], row['svid'],
                              row['ts_key'],
                              row['src_key'], row['delivery_system'])
            services.append(svc)
        return services

    def get_prog_crid_list_of_series(self, series_crid):
        prog_crids = []
        c = self.connection.cursor()
        q = '''select distinct(prog_crid) from series_crids
               join programs
                 on series_crids.evt_key = programs.evt_key
               where series_crids.series_crid = ?;'''
        c.execute(q, [series_crid])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                prog_crids.append(row['prog_crid'])
        return prog_crids

    def get_alternatives_of_program(self, prog_crid):
        alternatives = []
        c = self.connection.cursor()
        q = '''select * from programs
            join events on programs.evt_key = events.evt_key
            join services on events.svc_key = services.svc_key
            left outer join event_texts
             on events.evt_key = event_texts.evt_key
            where prog_crid = ?
            order by start_time, events.svc_key'''
        c.execute(q, [prog_crid])
        rows = c.fetchall()
        if (rows):
            for row in rows:
                event = self._row_to_event(row)
                alternatives.append(event)
        return alternatives

    def get_settings(self, name, user_key=0):
        c = self.connection.cursor()
        q = '''select value from programs where name = ? and user_key = ?'''
        c.execute(q, name, user_key)
        row = c.fetchone()
        if (row):
            return row['value']
        return None


if __name__ == "__main__":
    db = DbCenter()
    db.sync_events()
    print()

    print("services:")
    #svcs = db.read_all_services('order by lcn')
    svcs = db.read_all_services()
    for svc in svcs:
        print(svc.detail_string())
    print()

    print("reservations:")
    rsvs = db.read_all_reservations()
    for rsv in rsvs:
        print(rsv)
    print()

    print("schedules:")
    scheds = db.read_all_schedules()
    for sched in scheds:
        print(sched)
    print()
