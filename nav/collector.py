#! /usr/bin/env python3

import poll_loop
import os
import dvbsi
from demux import Demux
import observer


class Collector(observer.Observable):
    def __init__(self):
        observer.Observable.__init__(self)

        self.poller = poll_loop.PollLoop()
        self.card = 0
        self.dev = 0

    def set_demux_dev(self, card, dev):
        self.card = card
        self.dev = dev


class SiCollector(Collector):
    '''collects PSI/SI (service information; defined by ISO and ETSI) data.

    It sets filters for section table on demux, receives and saves sections,
    checks version and CRC values to find out if it is useful and notify to
    user on receiving useful section, completing sub_table or finishing all
    sub_tables.

    Some informations are gathered from the sections to get informations or
    receive other kind of section tables when completing:

        * PAT:    programs, network_pid and actual_tsid
        * NITact: transports and actual_nid
        * SDTact: actual_onid and actual_tsid
        * BAT:    transports

    To get PMTs, programs MUST be set by PAT.
    To get SDToth, usually transports are needed to be set. Otherwise collector
    can not make sub_tables for all SDToth sections, therefore, can not
    determine whether all receiving is finished or not.
    network_pid is needed to get NIT only if NIT is not from DVB-standard PID.
    '''
    def __init__(self):
        Collector.__init__(self)

        # initialize tables
        self.pat = dvbsi.Table(dvbsi.STAG_PROGRAM_ASSOCIATION)
        self.pmt = dvbsi.Table(dvbsi.STAG_PROGRAM_MAP)
        self.bat = dvbsi.Table(dvbsi.STAG_BOUQUET_ASSOCIATION)
        self.nit_act = dvbsi.Table(dvbsi.STAG_NETWORK_INFORMATION_ACTUAL)
        self.nit_oth = dvbsi.Table(dvbsi.STAG_NETWORK_INFORMATION_OTHER)
        self.sdt_act = dvbsi.TableSdt(dvbsi.STAG_SERVICE_DESCRIPTION_ACTUAL)
        self.sdt_oth = dvbsi.TableSdt(dvbsi.STAG_SERVICE_DESCRIPTION_OTHER)
        self.active_tables = []
        self.reset()

        self.tdt_demux = None
        self.tot_demux = None

    def reset(self):
        self.pat.reset()
        self.pmt.reset()
        self.bat.reset()
        self.sdt_act.reset()
        self.sdt_oth.reset()
        self.nit_act.reset()
        self.nit_oth.reset()

        self.tdt_section = None
        self.tot_section = None

        self.programs = []
        self.transports = []

        # initialize ID infos
        self.network_pid = dvbsi.TRANSPORT_NIT_PID
        self.actual_nid = 0
        self.actual_tsid = 0
        self.actual_onid = 0

    def notify_observers(self, result, section, sub_table, table):
        for observer in self.observers:
            observer.on_section(self, result, section, sub_table, table)

    def notify_observers_warning(self, section, string):
        for observer in self.observers:
            observer.on_warning(self, section, string)

    def is_all_complete(self):
        for table in self.active_tables:
            if (table.is_complete() is False):
                return False
        return True

    def process_section2(self, fd, mode, demux, table_id):
        if (mode & poll_loop.POLLERR):
            demux.stop()
            self.notify_observers(dvbsi.RECEIVING_TIMED_OUT, None, None, None)
            return -1

        parser = dvbsi.SECTION_MAP.get(table_id)
        if (parser is None):
            self.notify_observers(dvbsi.ERROR_ON_PARSING, None, None, None)
            return -1

        try:
            raw = os.read(fd, 4096)
        except:
            return
        section = parser(raw)
        if (section.table_id == -1):
            self.notify_observers(dvbsi.ERROR_ON_PARSING, section, None, None)
            return -1

        section.decode()

        if (table_id == dvbsi.STAG_TIME_DATE):
            self.tdt_section = section
        elif (table_id == dvbsi.STAG_TIME_OFFSET):
            self.tot_section = section

        # notify
        self.notify_observers(dvbsi.NEW_SECTION, section, None, None)

    def process_section(self, fd, mode, demux, table):
        if (mode & poll_loop.POLLERR):
            demux.stop()
            self.notify_observers(dvbsi.RECEIVING_TIMED_OUT, None, None, table)
            return -1

        # find out parser
        table_id = table.table_id
        parser = dvbsi.SECTION_MAP.get(table_id)
        if (parser is None):
            string = "table_id(%02x) error" % table_id
            self.notify_observers_warning(None, string)
            return -1

        try:
            raw = os.read(fd, 4096)
        except:
            return
        section = parser(raw)
        if (section.table_id == -1):
            self.notify_observers(dvbsi.ERROR_ON_PARSING, section, None, None)
            return -1

        # find out key & sub_table
        result = table.save(section)
        if ((result & (dvbsi.NEW_SECTION | dvbsi.VERSION_CHANGED)) is 0):
            # this section is already received. just return...
            return 0

        section.decode()

        if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
            if (section.transport_stream_id != self.actual_tsid):
                if (self.actual_tsid != 0):
                    string = "PAT tsid mismatch (%04x != %04x)" % (
                        section.transport_stream_id, self.actual_tsid)
                    self.notify_observers_warning(section, string)
                self.actual_tsid = section.transport_stream_id
        elif (table_id == dvbsi.STAG_SERVICE_DESCRIPTION_ACTUAL):
            if (section.transport_stream_id != self.actual_tsid):
                if (self.actual_tsid != 0):
                    string = "SDT tsid mismatch (%04x != %04x)" % (
                        section.transport_stream_id, self.actual_tsid)
                    self.notify_observers_warning(section, string)
                else:
                    self.actual_tsid = section.transport_stream_id
            self.actual_onid = section.original_network_id
        elif (table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL):
            self.actual_nid = section.network_id

        if (result & dvbsi.COMPLETE_TABLE):
            # pre-process complete table
            if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
                self.on_complete_pat()
            elif (table_id == dvbsi.STAG_PROGRAM_MAP):
                self.on_complete_pmt()
            elif (table_id == dvbsi.STAG_BOUQUET_ASSOCIATION):
                self.on_complete_bat()
            elif (table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL):
                self.on_complete_nit_act()
            elif (table_id == dvbsi.STAG_SERVICE_DESCRIPTION_ACTUAL):
                self.on_complete_sdt_act()
            elif (table_id == dvbsi.STAG_SERVICE_DESCRIPTION_OTHER):
                self.on_complete_sdt_oth()

        key = table.get_key(section)
        sub_table = table.get_sub_table(key)

        self.notify_observers(result, section, sub_table, table)

    def on_complete_pat(self):
        sections = self.pat.get_sections()

        self.programs = []
        for section in sections:
            for program in section.programs:
                if (program.program_number == 0):
                    self.network_pid = program.pid
                else:
                    self.programs.append(program)

    def on_complete_pmt(self):
        pass

    def on_complete_bat(self):
        pass

    def on_complete_sdt_act(self):
        pass

    def on_complete_sdt_oth(self):
        pass

    def on_complete_nit_act(self):
        self.transports = []
        sections = self.nit_act.get_sections()
        for section in sections:
            for transport in section.transports:
                # push transport into queue
                self.transports.append(transport)

    def stop(self):
        for table in self.active_tables:
            if (hasattr(table, 'demux')):
                table.demux.stop()
                self.poller.unregister(table.demux.fileno())
                del(table.demux)
        self.active_tables = []

        if (self.tdt_demux):
            self.tdt_demux.stop()
            self.poller.unregister(self.tdt_demux.fileno())
            self.tdt_demux = None
        if (self.tot_demux):
            self.tot_demux.stop()
            self.poller.unregister(self.tot_demux.fileno())
            self.tot_demux = None

    def stop_table(self, table):
        try:
            self.active_tables.remove(table)
        except:
            return
        if (hasattr(table, 'demux')):
            table.demux.stop()
            self.poller.unregister(table.demux.fileno())
            del(table.demux)

    def start_table(self, table, pid, timeout, flags=0):
        demux = Demux(self.card, self.dev)
        demux.set_filter(pid, [table.table_id], [0xff], None, timeout, flags)
        demux.start()
        self.poller.register(demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_section,
                             demux, table)
        self.active_tables.append(table)
        table.demux = demux

    def start_pat(self, timeout=0, pid=dvbsi.TRANSPORT_PAT_PID):
        self.pat.reset()
        self.start_table(self.pat, pid, timeout)

    def start_pmt(self, pid, timeout=0):
        if (hasattr(self.pmt, 'demux')):
            self.pmt.demux.stop()
            self.poller.unregister(self.pmt.demux.fileno())
            del(self.pmt.demux)
        self.pmt.reset()
        self.start_table(self.pmt, pid, timeout)

    def start_bat(self, timeout=0, pid=dvbsi.TRANSPORT_BAT_PID):
        self.bat.reset()
        self.start_table(self.bat, pid, timeout)

    def start_nit_act(self, timeout=0, pid=dvbsi.TRANSPORT_NIT_PID):
        self.nit_act.reset()
        self.start_table(self.nit_act, pid, timeout)

    def start_nit_oth(self, timeout=0, pid=dvbsi.TRANSPORT_NIT_PID):
        self.nit_oth.reset()
        self.start_table(self.nit_oth, pid, timeout)

    def start_sdt_act(self, timeout=0, pid=dvbsi.TRANSPORT_SDT_PID):
        self.sdt_act.reset()
        self.start_table(self.sdt_act, pid, timeout)

    def start_sdt_oth(self, timeout=0, pid=dvbsi.TRANSPORT_SDT_PID):
        self.sdt_oth.reset()
        for transport in self.transports:
            tsid = transport.transport_stream_id
            onid = transport.original_network_id
            if (tsid == self.actual_tsid and onid == self.actual_onid):
                continue

            key = (dvbsi.STAG_SERVICE_DESCRIPTION_OTHER, tsid, onid)
            self.sdt_oth.new_sub_table(key)

        self.start_table(self.sdt_oth, pid, timeout)

    def start_tdt(self, timeout=0, pid=dvbsi.TRANSPORT_TDT_PID):
        if (self.tdt_demux):
            self.tdt_demux.stop()
            self.poller.unregister(self.tdt_demux.fileno())
            self.tdt_demux = None
        self.tdt_demux = Demux(self.card, self.dev)
        self.tdt_demux.set_filter(pid, [dvbsi.STAG_TIME_DATE],
                                  [0xff], None, timeout, 0)
        self.tdt_demux.start()
        self.poller.register(self.tdt_demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_section2,
                             self.tdt_demux, dvbsi.STAG_TIME_DATE)

    def start_tot(self, timeout=0, pid=dvbsi.TRANSPORT_TOT_PID):
        if (self.tot_demux):
            self.tot_demux.stop()
            self.poller.unregister(self.tot_demux.fileno())
            self.tot_demux = None
        self.tot_demux = Demux(self.card, self.dev)
        self.tot_demux.set_filter(pid, [dvbsi.STAG_TIME_OFFSET],
                                  [0xff], None, timeout, 0)
        self.tot_demux.start()
        self.poller.register(self.tot_demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_section2,
                             self.tot_demux, dvbsi.STAG_TIME_OFFSET)


class EitCollector(Collector):
    def __init__(self):
        Collector.__init__(self)

        # initialize tables
        self.eit_pf = dvbsi.TableEit()
        self.eit_sch = dvbsi.TableEit()
        self.reset()

    def notify_observers(self, result, section, sub_table, svc_table, table):
        for observer in self.observers:
            observer.on_eit_section(self, result, section,
                                    svc_table, sub_table, table)

    def notify_observers_warning(self, section, string):
        for observer in self.observers:
            observer.on_eit_warning(self, section, string)

    def reset(self):
        self.eit_pf.reset()
        self.eit_sch.reset()

    def process_eit(self, fd, mode, demux, table):
        if (mode & poll_loop.POLLERR):
            demux.stop()
            self.notify_observers(dvbsi.RECEIVING_TIMED_OUT,
                                  None, None, None, table)
            demux.start()
            return

        # find out parser
        table_id = dvbsi.STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL
        parser = dvbsi.SECTION_MAP.get(table_id)
        try:
            raw = os.read(fd, 4096)
        except:
            return
        section = parser(raw)
        if (section.table_id == -1):
            self.notify_observers(dvbsi.ERROR_ON_PARSING,
                                  section, None, None, None)
            return

        # find out key & sub_table
        result = table.save(section)
        if ((result & (dvbsi.NEW_SECTION | dvbsi.VERSION_CHANGED)) is 0):
            # this section is already received. just return...
            return

        section.decode()

        svc_key = table.get_svc_table_key(section)
        svc_table = table.get_svc_table(svc_key)

        sub_key = svc_table.get_key(section)
        sub_table = svc_table.get_sub_table(sub_key)

        self.notify_observers(result, section, sub_table, svc_table, table)

    def stop(self):
        if (hasattr(self.eit_pf, 'demux_act')):
            self.eit_pf.demux_act.stop()
            self.poller.unregister(self.eit_pf.demux_act.fileno())
            del(self.eit_pf.demux_act)
        if (hasattr(self.eit_pf, 'demux_oth')):
            self.eit_pf.demux_oth.stop()
            self.poller.unregister(self.eit_pf.demux_oth.fileno())
            del(self.eit_pf.demux_oth)
        if (hasattr(self.eit_sch, 'demux_act')):
            self.eit_sch.demux_act.stop()
            self.poller.unregister(self.eit_sch.demux_act.fileno())
            del(self.eit_sch.demux_act)
        if (hasattr(self.eit_sch, 'demux_oth')):
            self.eit_sch.demux_oth.stop()
            self.poller.unregister(self.eit_sch.demux_oth.fileno())
            del(self.eit_sch.demux_oth)

    def start_eit_pf(self, timeout=0, pid=dvbsi.TRANSPORT_EIT_PID):
        #self.eit_pf.reset()
        demux = Demux(self.card, self.dev)
        demux.set_filter(pid,
                         [dvbsi.STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL],
                         [0xff], None, timeout, 0)
        demux.start()
        self.poller.register(demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_eit,
                             demux, self.eit_pf)
        self.eit_pf.demux_act = demux

        demux = Demux(self.card, self.dev)
        demux.set_filter(pid,
                         [dvbsi.STAG_EVENT_INFORMATION_NOWNEXT_OTHER],
                         [0xff], None, timeout, 0)
        demux.start()
        self.poller.register(demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_eit,
                             demux, self.eit_pf)
        self.eit_pf.demux_oth = demux

    def start_eit_sch(self, timeout=0, pid=dvbsi.TRANSPORT_EIT_PID):
        #self.eit_sch.reset()
        demux = Demux(self.card, self.dev)
        demux.set_filter(pid,
                         [dvbsi.STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL],
                         [0xf0], None, timeout, 0)
        demux.start()
        self.poller.register(demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_eit,
                             demux, self.eit_sch)
        self.eit_sch.demux_act = demux

        demux = Demux(self.card, self.dev)
        demux.set_filter(pid,
                         [dvbsi.STAG_EVENT_INFORMATION_SCHEDULE_OTHER],
                         [0xf0], None, timeout, 0)
        demux.start()
        self.poller.register(demux.fileno(),
                             poll_loop.POLLIN | poll_loop.POLLERR,
                             self.process_eit,
                             demux, self.eit_sch)
        self.eit_sch.demux_oth = demux


if __name__ == "__main__":
    import si_print

    poller = poll_loop.PollLoop()

    class TestSiObserver(observer.SiObserver):
        def on_section(self, si_collector, result, section, sub_table, table):
            if (result == dvbsi.RECEIVING_TIMED_OUT):
                string = "timeout table 0x%02x" % (table.table_id)
                print(string)
                si_collector.stop_table(table)
            elif (result == dvbsi.ERROR_ON_PARSING):
                string = "error on parsing"
                print(string)
                if (section is not None):
                    si_print.print_section(section)
                return
            else:
                si_print.print_section(section)

            if (result & dvbsi.COMPLETE_TABLE):
                table_id = table.table_id
                if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
                    #self.eit_collector.start_eit_sch()
                    si_collector.start_nit_act(21000)
                    si_collector.start_nit_oth(21000)
                    si_collector.start_sdt_act(21000)
                    si_collector.start_tdt()
                    si_collector.start_tot()
                    si_collector.start_bat()
                elif (table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL):
                    si_collector.start_sdt_oth(21000)

            for table in si_collector.active_tables:
                print(hex(table.table_id), table.is_complete())

            if (si_collector.is_all_complete()):
                si_collector.stop()
                poller.stop()

        def on_section2(self, monitor, section):
            si_print.print_section(section)
            monitor.num_section += 1
            pass

        def on_complete_sub_table(self, monitor, sub_table):
            print("complete", sub_table)

        def on_complete_table(self, monitor, table):
            table_id = table.table_id
            print("complete TABLE 0x%02x" % table_id)
            if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
                monitor.stop()
                print("Start NIT ACT")
                monitor.start_nit_act(11000, monitor.network_pid)
                print("Start NIT OTH")
                monitor.start_nit_oth(11000, monitor.network_pid)
                print("Start PMT")
                for program in monitor.programs:
                    print("(PID 0x%04x, SID 0x%04x)" %
                          (program.pid, program.program_number))
            elif (table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL):
                print("Start SDT OTH")
                monitor.start_sdt_oth(11000)

        def on_finish(monitor, result):
            print("finish result =", result)
            #monitor.stop()
            #poller.stop()

    test_si_observer = TestSiObserver()
    si_collector = SiCollector()
    si_collector.register_observer(test_si_observer)
    si_collector.start_pat(5000)

    poller.run()

    sections = []
    sections += si_collector.pat.get_sections()
    sections += si_collector.sdt_act.get_sections()
    sections += si_collector.sdt_oth.get_sections()
    sections += si_collector.nit_act.get_sections()
    sections += si_collector.nit_oth.get_sections()

    if (len(sections) != si_collector.num_section):
        print("Warning: number of section mismatch (%d != %d)" %
              (len(sections), si_collector.num_section))
