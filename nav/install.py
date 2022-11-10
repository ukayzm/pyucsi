#! /usr/bin/env python3


import frontend
import fcntl
import os
import fnmatch
import db_center
import linuxdvb
import logging
import time
import dvb


class ConfigFrontends:
    def __init__(self):
        self.db = db_center.DbCenter()

    def get_initial_file_params(self, src_key):
        c = self.db.connection.cursor()
        query = '''select src_name from sources where src_key = ?'''
        c.execute(query, [src_key])
        row = c.fetchone()
        if (row is None):
            return []
        ts_dir = os.path.expanduser(row['src_name'])
        params = []
        try:
            for filename in os.listdir(ts_dir):
                if (filename[0] == '.'):
                    continue
                ts = dvb.TsFile(0, src_key)
                ts.pathname = ts_dir + "/" + filename
                params.append(ts)
        except:
            pass
        return params

    def determine_source(self, fe):
        "make association between source and FE according to DB"

        # get sources from DB
        c = self.db.connection.cursor()

        print("configure", fe.fe_filename, '-> ', end='')
        query = """select tuner_key, type, capability
                   from tuners where tuner_name = ?"""
        c.execute(query, [fe.fe_filename])
        row = c.fetchone()
        if (row is None):
            print("no record in tuners")
            return
        if (fe.feinfo.type != row['type']):
            print("type mismatch")
            return
        if (fe.feinfo.caps != row['capability']):
            print("caps mismatch")
            return
        tuner_key = row['tuner_key']

        if (fe.feinfo.type == frontend.FE_OFDM):
            query = """select *
                       from sources join src_tuners
                         on sources.src_key = src_tuners.src_key
                       where tuner_key = ?;"""
            c.execute(query, [tuner_key])
            rows = c.fetchall()
            if (rows is None):
                print("no record in sources or src_tuners")
                return
            fe.sources = []
            for row in rows:
                source = dvb.Source(row['src_key'],
                                    row['delivery_system'],
                                    row['src_name'])
                fe.sources.append(source)
            if (len(fe.sources)):
                fe.source = fe.sources[0]
        elif (fe.feinfo.type == frontend.FE_QPSK):
            query = """select *
                       from sources
                       join sat_lnbs on sources.src_key = sat_lnbs.src_key
                       join lnbs on sat_lnbs.lnb_key = lnbs.lnb_key
                       join lnb_tuners on lnbs.lnb_key = lnb_tuners.lnb_key
                       where lnb_tuners.tuner_key = ?"""
            c.execute(query, [tuner_key])
            rows = c.fetchall()
            if (rows is None or len(rows) == 0):
                print("no record in sources, sat_lnbs, lnbs or lnb_tuners")
                return
            fe.sources = []
            for row in rows:
                source = dvb.SatSource(row['src_key'],
                                       row['delivery_system'],
                                       row['orbital_position'],
                                       row['src_name'])
                source.lo_freq = row['lo_freq']
                source.lo_freq2 = row['lo_freq2']
                source.num_output = row['num_output']
                source.with_motor = row['with_motor']
                source.lnb_name = row['lnb_name']
                source.link_type = row['link_type']
                source.diseqc_version = row['diseqc_version']
                source.continuous_tone = row['continuous_tone']
                fe.sources.append(source)
            fe.source = fe.sources[0]
        elif (fe.feinfo.type == frontend.FE_FILE):
            query = """select *
                       from sources join src_tuners
                         on sources.src_key = src_tuners.src_key
                       where tuner_key = ?;"""
            c.execute(query, [tuner_key])
            rows = c.fetchall()
            if (rows is None):
                print("no record in sources or src_tuners")
                return
            fe.sources = []
            for row in rows:
                source = dvb.Source(row['src_key'],
                                    row['delivery_system'],
                                    row['src_name'])
                fe.sources.append(source)
            if (len(fe.sources)):
                fe.source = fe.sources[0]

        for source in fe.sources:
            if (fe.feinfo.type == 8):
                tps = self.get_initial_file_params(source.src_key)
            else:
                tps = self.db.read_transports(source.src_key)
            source.tps_to_scan = tps

        print(fe.source)

class ConfigFrontendsAuto():
    def __init__(self):
        self.db = db_center.DbCenter()
        self.lnb_freqs = [(5150, 0),
                          (5750, 0),
                          (9750, 0),
                          (10000, 0),
                          (10600, 0),
                          (10700, 0),
                          (10750, 0),
                          (11200, 0),
                          (11300, 0),
                          (11475, 0),
                          (11500, 0)]
        self.lnb_freqs = [(5150, 0),
                          (10700, 0),
                          (11300, 0)]
        self.link_types = [0, 1, 2, 3, 4]   # 0: LNB only, 1-4: DiSEqC A-D
        self.tones = [0, 1]

    def detect_source(self, fe):
        "make association between source and FE automatically"

        print("try to figure out", fe.fe_filename, fe.type_str)
        if (fe.feinfo.type == frontend.FE_QPSK):
            self.figure_out_sat_auto(fe)
        elif (fe.feinfo.type == frontend.FE_OFDM):
            self.figure_out_ter(fe)
        elif (fe.feinfo.type == frontend.FE_FILE):
            self.figure_out_file(fe)
        else:
            return

        c = self.db.connection.cursor()
        query = "delete from tuners where tuner_name = ?"
        c.execute(query, [fe.fe_filename])

        self.db.commit()
        if (fe.feinfo.type == frontend.FE_QPSK):
            self.save_sat(fe)
        elif (fe.feinfo.type == frontend.FE_OFDM):
            self.save_file(fe)
        elif (fe.feinfo.type == frontend.FE_FILE):
            self.save_file(fe)

    def figure_out_file(self, fe):
        c = self.db.connection.cursor()
        fe.sources = []
        query = """select * from sources where delivery_system = 8
                   order by src_key"""
        c.execute(query)
        rows = c.fetchall()
        if rows is None:
            return
        for row in rows:
            source = dvb.Source(row['src_key'],
                                row['delivery_system'],
                                row['src_name'])
            fe.sources.append(source)
        fe.source = fe.sources[0]

    def figure_out_ter(self, fe):
        c = self.db.connection.cursor()
        fe.sources = []
        sources = []
        query = """select * from sources where delivery_system = 2
                   order by src_key"""
        c.execute(query)
        rows = c.fetchall()
        if rows is None:
            return
        for row in rows:
            source = dvb.Source(row['src_key'],
                                row['delivery_system'],
                                row['src_name'])
            source.tps_to_scan = []
            sources.append(source)

        for source in sources:
            tps = self.db.read_transports(source.src_key)
            if (len(tps)):
                source.tps_to_scan = tps
                fe.sources.append(source)

    def figure_out_sat_auto(self, fe):
        org_source = fe.source
        org_sources = fe.sources
        c = self.db.connection.cursor()

        # get sources from DB
        sources = []
        query = """select * from sources where delivery_system = 0
                   order by src_key"""
        c.execute(query)
        rows = c.fetchall()
        if rows is None:
            return
        for row in rows:
            source = dvb.SatSource(row['src_key'],
                                   row['delivery_system'],
                                   row['orbital_position'],
                                   row['src_name'])
            print("src: ", source)
            sources.append(source)

        # construct combination of sources and LNBs
        sat_sources = []
        for link_type in self.link_types:
            for continuous_tone in self.tones:
                for lo_freq, lo_freq2 in self.lnb_freqs:
                    for source in sources:
                        sat_source = dvb.SatSource(source.src_key,
                                                   source.delivery_system,
                                                   source.orbital_position,
                                                   source.src_name)
                        sat_source.lo_freq = lo_freq
                        sat_source.lo_freq2 = lo_freq2
                        sat_source.num_output = 1
                        sat_source.link_type = link_type
                        if (link_type == 0):
                            sat_source.diseqc_version = 0
                        else:
                            sat_source.diseqc_version = 11
                        sat_source.continuous_tone = continuous_tone
                        sat_source.lnb_name = str(sat_source)
                        sat_sources.append(sat_source)

        high_score = 0
        high_sat_source = None
        new_sources = []
        for sat_source in sat_sources:
            home_tps = self.db.read_transports(sat_source.src_key)
            if (len(home_tps) == 0):
                continue

            score = 0
            match = False
            print("try --", str(sat_source))

            for ts in home_tps:
                fe.source = sat_source
                print("    %-35s -> " % ts, end='')
                ret = fe.tune(ts)
                if (ret is False):
                    continue
                time.sleep(1)
                status = fe.read_status()
                print(hex(status))
                if (status & linuxdvb.FE_HAS_LOCK):
                    score += 1

            if (len(home_tps) <= 2):
                if (score == len(home_tps)):
                    match = True
            else:
                if (score > (len(home_tps) / 2)):
                    match = True
            if (match is True):
                if (score > high_score):
                    #remember source
                    high_score = score
                    high_sat_source = sat_source
                for new_src in new_sources:
                    if (new_src.src_key == sat_source.src_key):
                        # duplicated source: discard
                        if (new_src.link_type == 0
                            and sat_source.link_type != 0):
                            new_sources.remove(new_src)
                            new_sources.append(sat_source)
                        break
                else:
                    new_sources.append(sat_source)
            print("  score =", score, "/", high_score)
            print("")

        if (high_sat_source is None):
            fe.source = org_source
            fe.sources = org_sources
        else:
            fe.sources = new_sources
            fe.source = high_sat_source

    def save_file(self, fe):
        c = self.db.connection.cursor()
        query = """insert into tuners (type, capability, is_slave, tuner_name)
                   values (?, ?, 0, ?)"""
        c.execute(query, [fe.feinfo.type, fe.feinfo.caps, fe.fe_filename])
        c.execute('''select last_insert_rowid() from tuners;''')
        row = c.fetchone()
        if (not row):
            return 0
        tuner_key = row[0]

        query = """insert into src_tuners (src_key, tuner_key)
                   values (?, ?)"""
        for source in fe.sources:
            c.execute(query, [source.src_key, tuner_key])
        self.db.commit()

    def save_sat(self, fe):
        c = self.db.connection.cursor()
        query = """delete from lnbs where lnb_key in
                   (select lnb_key from tuners
                    join lnb_tuners on tuners.tuner_key = lnb_tuners.tuner_key
                    where tuner_name = ?"""
        query += " and link_type in ("
        for link_type in self.link_types:
            if (link_type is not self.link_types[0]):
                query += ", "
            query += str(link_type)
        query += ")"
        query += " and continuous_tone in ("
        for tone in self.tones:
            if (tone is not self.tones[0]):
                query += ", "
            query += str(tone)
        query += ")"
        query += ");"
        print(query)
        c.execute(query, [fe.fe_filename])
        query = """insert into tuners (type, capability, is_slave, tuner_name)
                   values (?, ?, 0, ?)"""
        c.execute(query, [fe.feinfo.type, fe.feinfo.caps, fe.fe_filename])
        c.execute('''select last_insert_rowid() from tuners;''')
        row = c.fetchone()
        if (not row):
            return 0
        tuner_key = row[0]

        lnb_query = """insert into lnbs
                       (lo_freq, lo_freq2, num_output, with_motor, lnb_name)
                       values (?, ?, 1, 0, ?)"""
        sat_lnb_query = """insert into sat_lnbs (src_key, lnb_key)
                           values (?, ?)"""
        lnb_tuner_query = """insert into lnb_tuners
                            (lnb_key, tuner_key, link_type, diseqc_version,
                            continuous_tone, scd_band, scd_freq)
                            values (?, ?, ?, ?, ?, 0, 0)"""
        for source in fe.sources:
            c.execute(lnb_query,
                      [source.lo_freq, source.lo_freq2, source.lnb_name])
            c.execute('''select last_insert_rowid() from lnbs;''')
            row = c.fetchone()
            if (not row):
                continue
            lnb_key = row[0]

            c.execute(sat_lnb_query, [source.src_key, lnb_key])
            c.execute(lnb_tuner_query,
                      [lnb_key, tuner_key, source.link_type,
                       source.diseqc_version, source.continuous_tone])

        self.db.commit()

    def reset_transports(self, files):
        c = self.db.connection.cursor()
        for filename in files:
            pathname = "./known-transports/" + filename
            print("execute", pathname)
            schema = open(pathname, 'r')
            query = schema.read()
            schema.close
            c.executescript(query)

        self.db.commit()

class FeList():
    class __impl():
        """ Implementation of the singleton interface """
        def __init__(self):
            self.logger = logging.getLogger('MainLog')

            self.frontends = []

            for card in range(4):
                for dev in range(4):
                    fe = self._check_fe(card, dev)
                    if (fe):
                        self.frontends.append(fe)
            if (len(self.frontends) == 0):
                self.frontends.append(frontend.Frontend())

            default_source = dvb.Source(0, 9, "unknown")
            default_sat_source = dvb.SatSource(0, 9, 0, "unknown")
            for fe in self.frontends:
                type_str = frontend.fe_type[fe.feinfo.type]
                if (fe.feinfo.type == frontend.FE_QPSK):
                    fe.source = default_sat_source
                else:
                    fe.source = default_source
                fe.info_str = "%s (%s - %s from %s)" % (
                    fe.fe_filename, fe.feinfo.name,
                    type_str, str(fe.source))

            self.focused_frontend = self.frontends[0]

        def _check_file_fe(self, card, dev):
            filename = "/dev/dvb/adapter" + str(card) + "/dvr" + str(dev)
            try:
                fd = os.open(filename, os.O_RDONLY)
            except:
                return None
            os.close(fd)
            return frontend.FileFrontend(card, dev)

        def _check_fe(self, card, dev):
            filename = "/dev/dvb/adapter" + str(card) + "/frontend" + str(dev)
            try:
                fd = os.open(filename, os.O_RDONLY)
            except:
                return self._check_file_fe(card, dev)
            info = linuxdvb.dvb_frontend_info()
            fcntl.ioctl(fd, linuxdvb.FE_GET_INFO, info)
            os.close(fd)
            if (info.type == frontend.FE_OFDM):
                return frontend.OfdmFrontend(card, dev)
            elif (info.type == frontend.FE_QPSK):
                return frontend.QpskFrontend(card, dev)
            else:
                # TODO: FE_QAM
                print("FE type: %d" % info.type)
                return None

        def set_frontends(self):
            "make association between source and FE by DB"
            configurer = ConfigFrontends()

            for fe in self.frontends:
                configurer.determine_source(fe)

            for fe in self.frontends:
                type_str = frontend.fe_type[fe.feinfo.type]
                fe.info_str = "%s (%s - %s)" % (
                    fe.fe_filename, fe.feinfo.name, type_str)
                self.logger.info(fe.info_str)

        def get_frontends(self):
            return self.frontends[:]

        def alloc_frontend(self, observer, src_key, ts_key, priority):
            # TODO: observer, ts_key, priority
            pass

        def release_frontend(self, observer, fe):
            # TODO
            pass

        def select_frontend(self, src_key):
            if (self.focused_frontend.source.src_key == src_key):
                return self.focused_frontend

            for fe in self.frontends:
                for src in fe.sources:
                    if (src.src_key == src_key):
                        if (fe.source != src):
                            string = "select src of FE %s" % fe.fe_filename
                            self.logger.info(string)
                            fe.select_source(src_key)
                        self.focused_frontend = fe
                        string = "change FE to %s" % fe.fe_filename
                        self.logger.info(string)
                        return fe
            return None

        def get_focused_frontend(self):
            return self.focused_frontend

        def set_focused_frontend(self, fe):
            if (fe != self.focused_frontend):
                self.focused_frontend = fe
                string = "change FE to %s" % fe.fe_filename
                self.logger.info(string)

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if FeList.__instance is None:
            # Create and remember instance
            FeList.__instance = FeList.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_FeList__instance'] = FeList.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr)

if __name__ == "__main__":
    import sys
    import argparse

    def print_ter_params():
        australia_ter_params = []
        for freq in range(177500, 226501, 7000):
            ts = ts.TsTer(0, 0)
            ts.set_tuning_param(freq, linuxdvb.BANDWIDTH_7_MHZ)
            australia_ter_params.append(ts)
        for freq in range(522500, 816501, 7000):
            ts = dvb.TsTer(0, 0)
            ts.set_tuning_param(freq, linuxdvb.BANDWIDTH_7_MHZ)
            australia_ter_params.append(ts)

        print("PRAGMA foreign_keys = ON;")
        print()
        print("/*")
        print(" * Australia terrestrial")
        print(" */")
        for p in australia_ter_params:
            print('INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";')
            print('INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), %d, %d);' % (int(p.centre_frequency / 100), p.bandwidth))
            print()

        uk_ter_params = []
        for freq in range(474000, 858001, 8000):
            ts = dvb.TsTer(0, 0)
            ts.set_tuning_param(freq, linuxdvb.BANDWIDTH_8_MHZ)
            uk_ter_params.append(ts)

        print("PRAGMA foreign_keys = ON;")
        print()
        print("/*")
        print(" * UK terrestrial")
        print(" */")
        for p in uk_ter_params:
            print('INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";')
            print('INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), %d, %d);' % (int(p.centre_frequency / 100), p.bandwidth))
            print()

    def print_config():
        fe_list = FeList()
        fe_list.set_frontends()
        frontends = fe_list.get_frontends()
        print()
        for fe in frontends:
            print(fe.info_str)
            print(fe)
            print("  sources:")
            for source in fe.sources:
                print("   ", source)
                for ts in source.tps_to_scan:
                    print("      -", ts)
            print()
        print()

    prg_desc = """install transports and configurate their sources.\n
'tp' must match with the file in 'knowk-transports' directory.\n
If 'tp' is 'auto', install and configurate for all 'tp's"""
    parser = argparse.ArgumentParser(description = prg_desc)
    parser.add_argument('-a',
                        action = 'store',
                        type = int,
                        help = "use DVB /dev/dvb/adapterA/")
    parser.add_argument('-d',
                        action = 'store',
                        type = int,
                        help = "0: use LNB, 1-4: use DiSEqC (1-4) (DVB-S only)")
    parser.add_argument('-l',
                        action = 'store',
                        type = int,
                        help = "LNB frequency in MHz (DVB-S only)")
    parser.add_argument('-t',
                        action = 'store',
                        type = int,
                        help = "0: tone off, 1: tone on (DVB-S only)")
    parser.add_argument('tp',
                        action = 'store',
                        nargs = '*',
                        help = "tp in the 'known-transports' directory")

    argv = sys.argv[:]
    argv.pop(0)
    args = parser.parse_args(argv)

    if (len(args.tp)):
        fe_list = FeList()
        configurer = ConfigFrontendsAuto()
        if (args.tp[0] == "auto"):
            files = []
            try:
                for filename in os.listdir("./known-transports"):
                    if (filename[0] != "."):
                        files.append(filename)
            except:
                pass
        else:
            files = []
            for arg in args.tp:
                basename = os.path.basename(arg)
                if (fnmatch.fnmatch(basename, "*.sql") is False):
                    basename += ".sql"
                pathname = "./known-transports/" + basename
                if (os.path.isfile(pathname)):
                    files.append(basename)
        print()
        print("Install known-transports in", files)
        print()

        frontends = fe_list.get_frontends()
        if (args.a is not None):
            for fe in frontends:
                if (fe.card == args.a):
                    frontends = [fe]
                    break

        if (args.d is not None):
            configurer.link_types = [args.d]

        if (args.l is not None):
            configurer.lnb_freqs = [(args.l, 0)]

        if (args.t is not None):
            configurer.tones = [args.t]

        if (len(files)):
            configurer.reset_transports(files)
            print()

            for fe in frontends:
                configurer.detect_source(fe)

    print_config()
    parser.print_help()

    print("")
    print("")
    print("TODO: multiple execution for different satellite source...")
    print("TODO: only one source for terrestrial tuner...")
    print("")

