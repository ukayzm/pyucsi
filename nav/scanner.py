#! /usr/bin/env python

import collector
import observer
import dvbsi
import db_center
import linuxdvb
import frontend
import logging
import poll_loop
import install
import dvb


class ScanParams():
    def __init__(self, frontends):
        self.frontends = frontends
        self.n_cur_tp = 0
        self.tps_to_scan = []
        self.logger = logging.getLogger('MainLog')

    def __iter__(self):
        self.tps_to_scan = []
        self.n_cur_tp = 0
        for fe in self.frontends:
            for src in fe.sources:
                for tp_to_add in src.tps_to_scan:
                    if (self.add_transport(tp_to_add) is True):
                        self.n_cur_tp += 1
        self.n_cur_tp = 0
        return self

    def add_transport(self, tp_to_add):
        for tp in self.tps_to_scan:
            if (tp.is_the_same_as(tp_to_add)):
                return False
        else:
            self.tps_to_scan.insert(self.n_cur_tp, tp_to_add)
            return True

    def __next__(self):
        self.n_cur_tp += 1
        num_tps = len(self.tps_to_scan)
        if (num_tps == 0 or num_tps < self.n_cur_tp):
            raise StopIteration
        return self.tps_to_scan[self.n_cur_tp - 1]


class Scanner(observer.SiObserver):
    def __init__(self, svc_list):
        self.db = db_center.DbCenter()
        self.fe_list = install.FeList()
        self.si_collector = collector.SiCollector()
        self.si_collector.register_observer(self)
        self.poller = poll_loop.PollLoop()
        self.svc_list = svc_list
        self.on_scan_all_finished = None
        self.working = False
        self.logger = logging.getLogger('MainLog')
        self.scan_sdt_other = False
        self.scan_nit_other = False

        self.scan_params = None
        self.cur_tp = None

    def start(self, sdt_other=False, nit_other=False):
        if (self.working):
            self.stop()
        log_str = "start scanner"
        log_str += " (sdt_other: " + str(sdt_other)
        log_str += ", nit_other: " + str(nit_other) + ")"
        self.logger.info(log_str)

        self.scan_sdt_other = sdt_other
        self.scan_nit_other = nit_other
        frontends = self.fe_list.get_frontends()
        self.scan_params = ScanParams(frontends)
        self.scan_params.__iter__()
        self.working = True
        self.go_next()

    def start_one_tp(self, tp):
        if (self.working):
            self.stop()
        self.logger.info("start scanner (one TP)")
        self.scan_params = ScanParams([])
        self.scan_params.add_transport(tp)
        self.scan_params.__iter__()
        self.working = True
        self.go_next()

    def go_next(self):
        if (self.working is False):
            return

        self.si_collector.stop()
        self.si_collector.reset()
        try:
            self.cur_tp = self.scan_params.__next__()
        except StopIteration:
            string = "scan finished"
            self.logger.info(string)
            self.stop()
            # notify to observers
            if (self.on_scan_all_finished):
                self.on_scan_all_finished(self)
            return 0

        self.cur_fe = self.fe_list.select_frontend(self.cur_tp.src_key)
        self.si_collector.set_demux_dev(self.cur_fe.card, self.cur_fe.dev)
        self.cur_fe.tune(self.cur_tp)
        #self.logger.debug(self.cur_tp.detail_param_str())
        self.poller.register_timer(self.all_scan_timer, 3000, 0)
        self.si_collector.start_pat(3000)

    def stop(self):
        if (self.working is False):
            return
        self.fe_to_scan = []
        self.logger.info("stop scanner")
        self.si_collector.stop()
        self.si_collector.reset()
        self.poller.unregister_timer(self.all_scan_timer)
        self.working = False

    def on_section(self, si_collector, result, section, sub_table, table):
        if (result == dvbsi.RECEIVING_TIMED_OUT):
            string = "scan timed out - section not received"
            self.logger.info(string)
            if (table is not None):
                tid = table.table_id
                string = "timed-out table ID: " + hex(tid)
                self.logger.info(string)
                is_ok = (tid == dvbsi.STAG_NETWORK_INFORMATION_OTHER or
                         tid == dvbsi.STAG_SERVICE_DESCRIPTION_OTHER or
                         tid == dvbsi.STAG_BOUQUET_ASSOCIATION)
                if (is_ok):
                    si_collector.stop_table(table)
                    result = 0
            else:
                status = self.cur_fe.read_status()
                if (status & linuxdvb.FE_HAS_LOCK):
                    self.go_next()
                return

        if (result == dvbsi.ERROR_ON_PARSING):
            string = "scan ERROR_ON_PARSING"
            self.logger.info(string)
            return

        if (result < 0):
            string = "scan ERROR %d" % result
            self.logger.info(string)
            return

        if (result & dvbsi.COMPLETE_TABLE):
            table_id = table.table_id
            if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
                si_collector.start_nit_act(21000)
                si_collector.start_sdt_act(21000)
                if (self.scan_sdt_other):
                    si_collector.start_sdt_oth(21000)
                if (self.scan_nit_other):
                    si_collector.start_nit_oth(21000)
                #si_collector.start_bat(21000)

        if (si_collector.is_all_complete()):
            num_changed = self.save(si_collector)
            if (num_changed):
                self.svc_list.read_services()
                self.svc_list.notify_observers()

            self.check_network_search(si_collector)
            self.go_next()

    def create_tp(self, dsc, ts_key, src_key):
        if (dsc.tag == dvbsi.DTAG_SATELLITE_DELIVERY_SYSTEM):
            tp = dvb.TsSat(ts_key, src_key)
        elif (dsc.tag == dvbsi.DTAG_SATELLITE_DELIVERY_SYSTEM):
            tp = dvb.TsTer(ts_key, src_key)
        else:
            return None
        return tp

    def check_network_search(self, si_collector):
        if (self.cur_tp.tag == 0):
            return

        nits = si_collector.nit_act.get_sections()
        if (self.scan_nit_other):
            nits += si_collector.nit_oth.get_sections()
        need_to_check = False
        for nit in nits:
            for tp in nit.transports:
                for raw_dsc in tp.descriptors:
                    if (raw_dsc.tag == self.cur_tp.tag):
                        dsc_parser = dvbsi.DESCRIPTOR_MAP.get(raw_dsc.tag)
                        if (dsc_parser is None):
                            continue
                        dsc = dsc_parser(raw_dsc.data)
                        dsc.src_key = self.cur_tp.src_key
                        if (self.cur_tp.is_the_same_as(dsc)):
                            need_to_check = True
                            break
        if (need_to_check is False):
            return

        for nit in nits:
            for tp in nit.transports:
                for raw_dsc in tp.descriptors:
                    if (raw_dsc.tag == self.cur_tp.tag):
                        dsc_parser = dvbsi.DESCRIPTOR_MAP.get(raw_dsc.tag)
                        if (dsc_parser is None):
                            continue
                        dsc = dsc_parser(raw_dsc.data)
                        if (dsc.tag == dvbsi.DTAG_SATELLITE_DELIVERY_SYSTEM):
                            op = self.cur_fe.source.orbital_position
                            if (dsc.orbital_position != op):
                                continue
                        tp = self.create_tp(dsc, 0, self.cur_tp.src_key)
                        if (tp is None):
                            continue
                        tp.copy_tuning_param(dsc)
                        if (self.scan_params.add_transport(tp) is True):
                            self.logger.info("Network search: new TP %s" % tp)

    def save(self, si_collector):
        src_key = self.cur_fe.source.src_key

        nits = si_collector.nit_act.get_sections()
        if (self.scan_nit_other):
            nits += si_collector.nit_oth.get_sections()
        sdts = si_collector.sdt_act.get_sections()
        if (self.scan_sdt_other):
            sdts += si_collector.sdt_oth.get_sections()
        pats = si_collector.pat.get_sections()

        # save network
        for nit in nits:
            net_name = None
            for raw_dsc in nit.descriptors:
                if (raw_dsc.tag == dvbsi.DTAG_NETWORK_NAME):
                    dsc = dvbsi.NetworkNameDescriptor(raw_dsc.data)
                    raw_name = dsc.network_name
                    charset, used = dvbsi.dvb_charset(raw_name)
                    net_name = raw_name[used:].decode(charset, 'replace')
                    break
            self.db.save_network(nit.network_id, net_name)

        # transport streams
        if (self.scan_sdt_other):
            for nit in nits:
                nid = nit.network_id
                for transport in nit.transports:
                    tsid = transport.transport_stream_id
                    onid = transport.original_network_id
                    self.db.save_transport(src_key, nid, onid, tsid)
        else:
            ts_key = self.cur_tp.ts_key
            if (ts_key):
                self.db.update_transport(ts_key,
                                         si_collector.actual_nid,
                                         si_collector.actual_onid,
                                         si_collector.actual_tsid)
            else:
                self.db.save_transport(src_key,
                                       si_collector.actual_nid,
                                       si_collector.actual_onid,
                                       si_collector.actual_tsid)
                ts_key = self.db.get_ts_key(si_collector.actual_tsid,
                                            si_collector.actual_onid,
                                            si_collector.actual_nid,
                                            src_key)

            status = self.cur_fe.read_status()
            fe_type = self.cur_fe.feinfo.type
            if (status & linuxdvb.FE_HAS_LOCK):
                self.cur_fe.get_tuning_param(self.cur_tp)
                if (fe_type == frontend.FE_OFDM):
                    self.db.save_ter_param(ts_key, self.cur_tp)
                elif (fe_type == frontend.FE_QPSK):
                    self.db.save_sat_param(ts_key, self.cur_tp)
                elif (fe_type == frontend.FE_FILE):
                    self.db.save_file_param(ts_key, self.cur_tp)

        # save actual services
        self.db.reset_temp_services()

        # in PAT
        ts_key = self.db.get_ts_key(si_collector.actual_tsid,
                                    si_collector.actual_onid,
                                    si_collector.actual_nid,
                                    src_key)
        for pat in pats:
            for program in pat.programs:
                svid = program.program_number
                if (svid != 0):
                    self.db.insert_temp_service2(ts_key, svid)

        # in SDT
        for sdt in sdts:
            if (self.scan_sdt_other):
                ts_key = self.db.get_ts_key2(sdt.transport_stream_id,
                                             sdt.original_network_id,
                                             src_key)
            else:
                ts_key = self.db.get_ts_key(sdt.transport_stream_id,
                                            sdt.original_network_id,
                                            si_collector.actual_nid,
                                            src_key)
            for service in sdt.services:
                self.db.insert_temp_service(ts_key, service)

        scanned_services = self.db.get_temp_services()
        services_to_be_removed = self.db.get_services_to_be_removed()
        services_to_be_updated = self.db.get_services_to_be_updated()
        services_to_be_inserted = self.db.get_services_to_be_inserted()

        self.db.apply_temp_services()

        # save default authority for transports
        for nit in nits:
            self.save_transport_default_authorities(nit, src_key)

        # save default authority for services
        for sdt in sdts:
            ts_key = self.db.get_ts_key(sdt.transport_stream_id,
                                        sdt.original_network_id,
                                        si_collector.actual_nid,
                                        src_key)
            da_mux = self.db.read_transport_default_authority(ts_key)
            for service in sdt.services:
                da = self.search_default_authority(service.descriptors)
                if (da is None):
                    da = da_mux
                if (da is None):
                    continue
                svc_key = self.db.get_svc_key2(ts_key, service.service_id)
                self.db.save_default_authority(svc_key, da)

        # save LCN
        for nit in nits:
            for transport in nit.transports:
                tsid = transport.transport_stream_id
                onid = transport.original_network_id
                private_id = 0
                for raw_dsc in transport.descriptors:
                    data = raw_dsc.data
                    if (raw_dsc.tag == dvbsi.DTAG_PRIVATE_DATA_SPECIFIER):
                        dsc = dvbsi.PrivateDataSpecifierDescriptor(data)
                        private_id = dsc.private_data_specifier
                        continue

                    if (raw_dsc.tag == 0x83):
                        if (private_id == 0x233a):
                            self.save_ukdtt_lcn(data, tsid, onid, src_key)
                        elif (private_id == 0x29):  # NorDig
                            self.save_nordig_lcn(data, tsid, onid, src_key)
                        elif (private_id == 0x28):  # EACEM
                            self.save_eacem_lcn(data, tsid, onid, src_key)
                        elif (private_id == 0x36):  # CANAL+
                            self.save_eacem_lcn(data, tsid, onid, src_key)
                        else:
                            self.save_eacem_lcn(data, tsid, onid, src_key)

        self.db.commit()

        string = "current scan finished: "
        string += "%d services (" % len(scanned_services)
        string += "%d removed, " % len(services_to_be_removed)
        string += "%d updated, " % len(services_to_be_updated)
        string += "%d inserted)" % len(services_to_be_inserted)
        self.logger.info(string)

        num_changed = (len(services_to_be_removed) +
                       len(services_to_be_updated) +
                       len(services_to_be_inserted))
        return num_changed

    def save_ukdtt_lcn(self, raw, tsid, onid, src_key):
        dsc = dvbsi.UkDttLogicalChannelDescriptor(raw)
        for entry in dsc.entries:
            svid = entry.service_id
            svc_key = self.db.get_svc_key(tsid, onid, svid, src_key)
            if (svc_key):
                self.db.save_lcn(svc_key, 1, 1, entry.logical_channel_number)

    def save_nordig_lcn(self, raw, tsid, onid, src_key):
        dsc = dvbsi.NorDigLogicalChannelDescriptor(raw)
        for entry in dsc.entries:
            svid = entry.service_id
            svc_key = self.db.get_svc_key(tsid, onid, svid, src_key)
            if (svc_key):
                self.db.save_lcn(svc_key, entry.visible_service_flag,
                                 1, entry.logical_channel_number)

    def save_eacem_lcn(self, raw, tsid, onid, src_key):
        dsc = dvbsi.EacemLogicalChannelDescriptor(raw)
        for entry in dsc.entries:
            svid = entry.service_id
            svc_key = self.db.get_svc_key(tsid, onid, svid, src_key)
            if (svc_key):
                self.db.save_lcn(svc_key, entry.visible_service_flag,
                                 1, entry.logical_channel_number)

    def all_scan_timer(self):
        status = self.cur_fe.read_status()
        if (status & linuxdvb.FE_HAS_LOCK) == 0:
            string = "scan timed out - no signal"
            self.logger.info(string)
            self.go_next()

    def search_default_authority(self, descriptors):
        for raw_dsc in descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_DEFAULT_AUTHORITY):
                dsc = dvbsi.DefaultAuthorityDescriptor(raw_dsc.data)
                return dsc.name
        return None

    def save_transport_default_authorities(self, nit, src_key):
        # save default authority for transports
        da_loop_1 = self.search_default_authority(nit.descriptors)
        for transport in nit.transports:
            da = self.search_default_authority(transport.descriptors)
            if (da is None):
                da = da_loop_1
            if (da is None):
                continue
            ts_key = self.db.get_ts_key(transport.transport_stream_id,
                                        transport.original_network_id,
                                        nit.network_id, src_key)
            if (ts_key is None):
                continue
            self.db.save_transport_default_authority(ts_key, da)

if __name__ == "__main__":
    fe_list = install.FeList()
    configurer = install.ConfigFrontends()
    fe_list.config_frontends(configurer)
    scan_params = ScanParams(fe_list.get_frontends())
    for tp in scan_params:
        print(tp.src_key, tp.ts_key, tp)
