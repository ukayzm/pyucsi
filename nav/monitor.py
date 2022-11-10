#! /usr/bin/env python3

import frontend
import collector
import db_center
import logging
import observer
import dvbsi
import install
import dvb


class StreamSaver:
    def __init__(self):
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.logger = logging.getLogger('MainLog')

    def guess_audio_info(self, stream):
        codec = dvb.AUDIO_CODEC_MPEG_STEREO
        num_channel = 2
        # TODO: num_channel info should be get from descriptor
        if (stream.stream_type == dvbsi.ISO13818_7_AUDIO_ADTS
         or stream.stream_type == dvbsi.ISO14496_3_AUDIO_LATM):
            codec = dvb.AUDIO_CODEC_AAC
        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_AC3):
                codec = dvb.AUDIO_CODEC_AC3
                break
            elif (raw_dsc.tag == dvbsi.DTAG_ENHANCED_AC3):
                codec = dvb.AUDIO_CODEC_E_AC3
                break
            elif (raw_dsc.tag == dvbsi.DTAG_DTS):
                codec = dvb.AUDIO_CODEC_DTS
                break
            elif (raw_dsc.tag == dvbsi.DTAG_AAC):
                codec = dvb.AUDIO_CODEC_AAC
                break
        return codec, num_channel

    def guess_stream_class(self, stream):
        if (stream.stream_type == dvbsi.ISO11172_2_VIDEO
         or stream.stream_type == dvbsi.ISO13818_2_VIDEO
         or stream.stream_type == dvbsi.ISO14496_2_VISUAL
         or stream.stream_type == dvbsi.ISO14496_10_H264):
            return dvb.STREAM_CLASS_VIDEO

        if (stream.stream_type == dvbsi.ISO11172_3_AUDIO
         or stream.stream_type == dvbsi.ISO13818_3_AUDIO
         or stream.stream_type == dvbsi.ISO13818_7_AUDIO_ADTS
         or stream.stream_type == dvbsi.ISO14496_3_AUDIO_LATM):
            return dvb.STREAM_CLASS_AUDIO

        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_SUBTITLING):
                return dvb.STREAM_CLASS_DVB_SUBTITLE
            elif (raw_dsc.tag == dvbsi.DTAG_TELETEXT):
                return dvb.STREAM_CLASS_TELETEXT
            elif (raw_dsc.tag == dvbsi.DTAG_AC3 or
                  raw_dsc.tag == dvbsi.DTAG_ENHANCED_AC3 or
                  raw_dsc.tag == dvbsi.DTAG_DTS or
                  raw_dsc.tag == dvbsi.DTAG_AAC):
                return dvb.STREAM_CLASS_AUDIO

        return dvb.STREAM_CLASS_UNCLASSIFIED

    def save_streams(self, service, table):
        svc_key = service.svc_key
        svid = service.svid

        # TODO: do not delete...
        self.db.delete_all_streams_of(svc_key)

        pmts = table.get_sections()
        for section in pmts:
            if (section.program_number != svid):
                continue
            for stream in section.streams:
                stream_class = self.guess_stream_class(stream)
                component_tag = self.find_component_tag(stream)
                strm_key = self.db.save_stream(svc_key, stream, component_tag,
                                               stream_class)

                if (stream_class == dvb.STREAM_CLASS_AUDIO):
                    self.save_audio_stream(strm_key, stream)
                elif (stream_class == dvb.STREAM_CLASS_DVB_SUBTITLE):
                    self.save_dvb_subtitle_stream(strm_key, stream)
                elif (stream_class == dvb.STREAM_CLASS_TELETEXT):
                    self.save_teletext_stream(strm_key, stream)
        self.db.commit()

    def find_component_tag(self, stream):
        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_STREAM_IDENTIFIER):
                dsc = dvbsi.StreamIdentifierDescriptor(raw_dsc.data)
                return dsc.component_tag
        return -1

    def save_audio_stream(self, strm_key, stream):
        codec, num_channel = self.guess_audio_info(stream)
        lang_codes = []
        mix_type = 0    # TODO
        editorial_classification = 0    # TODO
        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_ISO_639_LANGUAGE):
                dsc = dvbsi.Iso639LanguageDescriptor(raw_dsc.data)
                for entry in dsc.entries:
                    lang_codes.append(entry)

        if (len(lang_codes) == 0):
            # no ISO_639_language_descriptor
            self.db.save_audio_stream(strm_key, "", codec, 0, mix_type,
                                      editorial_classification, num_channel)
        elif (len(lang_codes) >= 2 and codec == dvb.AUDIO_CODEC_MPEG_STEREO):
            # dual-mono
            self.db.save_audio_stream(strm_key, lang_codes[0].language_code,
                                      dvb.AUDIO_CODEC_MPEG_MONO_LEFT,
                                      lang_codes[0].audio_type, mix_type,
                                      editorial_classification, 1)
            self.db.save_audio_stream(strm_key, lang_codes[1].language_code,
                                      dvb.AUDIO_CODEC_MPEG_MONO_RIGHT,
                                      lang_codes[1].audio_type, mix_type,
                                      editorial_classification, 1)
        else:
            self.db.save_audio_stream(strm_key, lang_codes[0].language_code,
                                      codec, lang_codes[0].audio_type, mix_type,
                                      editorial_classification, num_channel)

    def save_dvb_subtitle_stream(self, strm_key, stream):
        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_SUBTITLING):
                dsc = dvbsi.SubtitlingDescriptor(raw_dsc.data)
                for entry in dsc.entries:
                    self.db.save_dvb_subtitle_stream(strm_key,
                                                     entry.language_code,
                                                     entry.subtitling_type,
                                                     entry.composition_page_id,
                                                     entry.ancillary_page_id)

    def save_teletext_stream(self, strm_key, stream):
        for raw_dsc in stream.descriptors:
            if (raw_dsc.tag == dvbsi.DTAG_TELETEXT):
                dsc = dvbsi.TeletextDescriptor(raw_dsc.data)
                for entry in dsc.entries:
                    self.db.save_teletext_stream(strm_key,
                                                 entry.language_code,
                                                 entry.teletext_type,
                                                 entry.teletext_magazine_number,
                                                 entry.teletext_page_number)


class Monitor(observer.SiObserver, observer.EitObserver, observer.SvcObserver):
    def __init__(self, svc_list):
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.fe_list = install.FeList()
        self.logger = logging.getLogger('MainLog')
        self.si_collector = collector.SiCollector()
        self.si_collector.register_observer(self)
        self.eit_collector = collector.EitCollector()
        self.eit_collector.register_observer(self)
        self.svc_list = svc_list
        self.svc_list.register_observer(self)
        self.cur_service = None
        self.working = False

    def start(self):
        if (self.working):
            self.stop()
        self.logger.info("start monitor")
        fe = self.fe_list.get_focused_frontend()
        self.si_collector.reset()
        self.si_collector.set_demux_dev(fe.card, fe.dev)
        self.eit_collector.set_demux_dev(fe.card, fe.dev)
        self.si_collector.start_pat(0)
        self.working = True

    def stop(self):
        if (self.working is False):
            return
        self.logger.info("stop monitor")
        self.si_collector.stop()
        self.eit_collector.stop()
        self.working = False

    def tune(self, service):
        self.stop()
        fe = self.fe_list.select_frontend(service.src_key)
        if (fe is None):
            return

        ts_key = service.ts_key
        ts = self.db.read_transport(ts_key)
        self.logger.info(ts)
        fe.tune(ts)
        self.start()

    def update(self, svc_list, services, cur_service):
        if (self.cur_service != cur_service):
            self.cur_service = cur_service
            self.start_pmt()

    def start_pmt(self):
        if (self.cur_service is None):
            return
        fe = self.fe_list.get_focused_frontend()
        if (fe.feinfo.type != self.cur_service.delivery_system):
            return

        if (self.cur_service.delivery_system == frontend.FE_OFDM):
            cur_freq = fe.get_frontend().frequency
            row = self.db.get_ter_param(self.cur_service.ts_key)
            if (not row):
                return
            svc_freq = row['freq'] * 1000
            if (cur_freq != svc_freq):
                return
        elif (self.cur_service.delivery_system == frontend.FE_FILE):
            cur_pathname = fe.ts_file_name
            row = self.db.get_file_param(self.cur_service.ts_key)
            if (not row):
                return
            if (row['pathname'] != cur_pathname):
                return

        pats = self.si_collector.pat.get_sections()
        for section in pats:
            for program in section.programs:
                if (program.program_number == self.cur_service.svid):
                    self.si_collector.start_pmt(program.pid)
                    return

    def on_warning(self, si_collector, section, string):
        self.logger.warning(string)

    def get_service_name(self, svc_key):
        c = self.connection.cursor()
        query = '''select svc_name from services where svc_key=?'''
        c.execute(query, [svc_key])
        row = c.fetchone()
        if (not row):
            return ""
        return row['svc_name']

    def on_eit_section(self, eit_collector, result, section,
                       sub_table, svc_table, table):
        if (result == dvbsi.RECEIVING_TIMED_OUT):
            self.logger.debug("EIT timeout")
            return

        if (result & (dvbsi.NEW_SECTION | dvbsi.VERSION_CHANGED)):
            tsid = section.transport_stream_id
            onid = section.original_network_id
            svid = section.service_id
            src_key = self.cur_service.src_key

            svc_key = self.db.get_svc_key(tsid, onid, svid, src_key)
            if (svc_key is None):
                return

            if (result & dvbsi.NEW_VERSION):
                string = "TID %02x" % section.table_id
                string += ", ver %02x" % section.version_number
                string += " - new EITsch version for "
                string += self.get_service_name(svc_key)
                self.logger.debug(string)
            if (result & dvbsi.VERSION_CHANGED):
                string = "TID %02x" % section.table_id
                string += ", ver %02x" % section.version_number
                string += " - EITsch version changed for "
                string += self.get_service_name(svc_key)
                self.logger.debug(string)
            if (result & dvbsi.COMPLETE_SVC_TABLE):
                svc_name = self.get_service_name(svc_key)
                self.logger.debug("%s: EITsch complete svc_table" % svc_name)

            # update events
            for event in section.events:
                self.db.save_event(onid, tsid, svid, svc_key,
                                   section.version_number, event)

    def on_section(self, si_collector, result, section, sub_table, table):
        if (result == dvbsi.RECEIVING_TIMED_OUT):
            #string = "timeout pid 0x%04x, table 0x%02x" % (pid, table_id)
            string = "timeout"
            if (table):
                string += " (table %02x)" % table.table_id
            self.logger.debug(string)
            return

        if (result < 0):
            return

        if (result & dvbsi.NEW_SECTION):
            table_id = section.table_id
            if (table_id == dvbsi.STAG_TIME_OFFSET):
                ts_key = self.cur_service.ts_key
                time_offset_in_db = self.db.read_time_offset(ts_key)
                time_offset = 0
                for dsc in section.descriptors:
                    if dsc.tag == dvbsi.DTAG_LOCAL_TIME_OFFSET:
                        # TODO: check country code and region id
                        lto_dsc = dvbsi.LocalTimeOffsetDescriptor(dsc.data)
                        if (len(lto_dsc.entries) == 0):
                            break
                        lto = lto_dsc.entries[0]
                        hour = dvbsi.bcd_to_integer(lto.local_time_offset[0])
                        minute = dvbsi.bcd_to_integer(lto.local_time_offset[1])
                        time_offset = (hour * 60 + minute) * 60
                        if (lto.local_time_offset_polarity == 1):
                            time_offset = -time_offset
                        break
                if (time_offset != time_offset_in_db):
                    self.db.save_time_offset(ts_key, time_offset)

        if (result & dvbsi.COMPLETE_TABLE):
            table_id = table.table_id
            if (table_id == dvbsi.STAG_PROGRAM_ASSOCIATION):
                self.start_pmt()
                self.eit_collector.start_eit_sch()
                self.si_collector.start_nit_act(21000)
                self.si_collector.start_nit_oth(21000)
                self.si_collector.start_sdt_act(21000)
                self.si_collector.start_tdt()
                self.si_collector.start_tot()
                self.si_collector.start_bat()
            elif (table_id == dvbsi.STAG_PROGRAM_MAP):
                if (self.cur_service):
                    stream_saver = StreamSaver()
                    stream_saver.save_streams(self.cur_service, table)
                    self.svc_list.notify_observers()
            elif (table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL):
                self.si_collector.start_sdt_oth(21000)

