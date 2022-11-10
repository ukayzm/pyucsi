#! /usr/bin/env python3

import linuxdvb
import fcntl
import os
import ctypes
import poll_loop
import observer
import time
import dvb


fe_type = list([
    'FE_QPSK',
    'FE_QAM',
    'FE_OFDM',
    'FE_ATSC',
    'FE_TYPE_4',
    'FE_TYPE_5',
    'FE_TYPE_6',
    'FE_TYPE_7',
    'FE_FILE',
    'FE_UNKNOWN'
])
for i, name in enumerate(fe_type):
    exec(name + '=' + str(i))


FE_LOOPED = 0x80


class Frontend(observer.FeObservable):
    def __init__(self, card=0, dev=0, rw=1, blocking=0):
        self.card = card
        self.dev = dev
        self.rw = rw
        self.blocking = blocking
        self.feinfo = linuxdvb.dvb_frontend_info()
        self.feinfo.type = FE_UNKNOWN
        self.src_key = 0
        self.ts_key = 0
        self.fe_filename = "NO_FE"
        self.source = None
        self.sources = []
        self.type_str = fe_type[self.feinfo.type]
        observer.Observable.__init__(self)

    def is_retunable(self, param):
        for observer in self.observers:
            if (observer.vote_against_tuning(self, param)):
                return False
        return True

    def get_tps_to_scan(self):
        return self.source.tps_to_scan[:]

    def get_info(self):
        return self.feinfo

    def read_status(self):
        return 0

    def read_ber(self):
        return 0

    def read_snr(self):
        return 0

    def read_signal_strength(self):
        return 0

    def get_frontend(self):
        p = linuxdvb.dvb_frontend_parameters()
        return p

    def set_frontend(self, p):
        return False

    def select_source(self, src_key):
        for source in self.sources:
            if (source.src_key == src_key):
                self.source = source
                return source
        return None

    def __str__(self):
        cap_str = "  capability:"
        for bit, flag in linuxdvb.fe_caps.items():
            if (self.feinfo.caps & bit) > 0:
                cap_str = "\n".join([cap_str, "    " + flag])
        return "\n".join([
            "%s" % self.fe_filename,
            "  type: %s" % fe_type[self.feinfo.type],
            "  name: %s" % self.feinfo.name,
            "  frequency_min: %d" % self.feinfo.frequency_min,
            "  frequency_max: %d" % self.feinfo.frequency_max,
            "  frequency_stepsize: %d" % self.feinfo.frequency_stepsize,
            "  frequency_tolerance: %d" % self.feinfo.frequency_tolerance,
            "  symbol_rate_min: %d" % self.feinfo.symbol_rate_min,
            "  symbol_rate_max: %d" % self.feinfo.symbol_rate_max,
            "  symbol_rate_tolerance: %d" % self.feinfo.symbol_rate_tolerance,
            "  notifier_delay: %d" % self.feinfo.notifier_delay,
            cap_str])


class DvbFrontend(Frontend):
    def __init__(self, card=0, dev=0, rw=1, blocking=0):
        Frontend.__init__(self, card, dev, rw, blocking)
        self.fe_filename = "/dev/dvb/adapter" + str(card)
        self.fe_filename += "/frontend" + str(dev)
        flags = 0
        if rw:
            flags = flags | os.O_RDWR
        else:
            flags = flags | os.O_RDONLY
        if not blocking:
            flags = flags | os.O_NONBLOCK
        self.fd = os.open(self.fe_filename, flags)
        self.poller = poll_loop.PollLoop()
        self.poller.register(self.fd,
                             poll_loop.POLLERR | poll_loop.POLLIN,
                             self.fe_callback)
        fcntl.ioctl(self.fd, linuxdvb.FE_GET_INFO, self.feinfo)
        self.type_str = fe_type[self.feinfo.type]

    def __delete__(self):
        if (self.fd != 0):
            os.close(self.fd)

    def fe_callback(self, fd, mode):
        try:
            event = self.get_event()
        except:
            return
        self.notify_observers(event)

    def set_blocking(self, blocking):
        fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        if blocking:
            fcntl.fcntl(self.fd, fcntl.F_SETFL, fl & (~os.O_NONBLOCK))
        else:
            fcntl.fcntl(self.fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def set_frontend(self, p):
        if (p.frequency < self.feinfo.frequency_min):
            return False
        if (p.frequency > self.feinfo.frequency_max):
            return False
        if (self.is_retunable(p) is False):
            return False
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_SET_FRONTEND, p)
        except:
            return False
        event = linuxdvb.dvb_frontend_event()
        event.status = linuxdvb.FE_REINIT
        event.parameters = p
        self.notify_observers(event)
        return True

    def get_frontend(self):
        p = linuxdvb.dvb_frontend_parameters()
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_GET_FRONTEND, p)
        except:
            pass
        return p

    def read_status(self):
        p = ctypes.c_uint()
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_READ_STATUS, p)
        except:
            pass
        return p.value

    def read_ber(self):
        p = ctypes.c_uint32()
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_READ_BER, p)
        except:
            pass
        return p.value

    def read_snr(self):
        p = ctypes.c_uint16()
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_READ_SNR, p)
        except:
            pass
        return p.value

    def read_signal_strength(self):
        p = ctypes.c_uint16()
        try:
            fcntl.ioctl(self.fd, linuxdvb.FE_READ_SIGNAL_STRENGTH, p)
        except:
            pass
        return p.value

    def get_event(self):
        event = linuxdvb.dvb_frontend_event()
        fcntl.ioctl(self.fd, linuxdvb.FE_GET_EVENT, event)
        return event


class OfdmFrontend(DvbFrontend):
    # fe_transmit_mode in frontend.h:
    #  0: TRANSMISSION_MODE_2K
    #  1: TRANSMISSION_MODE_8K
    #  2: TRANSMISSION_MODE_AUTO
    #  3: TRANSMISSION_MODE_4K
    #  4: TRANSMISSION_MODE_1K
    #  5: TRANSMISSION_MODE_16K
    #  6: TRANSMISSION_MODE_32K
    #  7: TRANSMISSION_MODE_C1
    #  8: TRANSMISSION_MODE_C3780
    def get_tuning_param(self, ts_ter):
        code_rate_dvb_of_linux = [7, 0, 1, 2, 7, 3, 7, 4, 7, 7, 7, 7]
        constellation_dvb_of_linux = [0, 1, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3]
        transmission_mode_dvb_of_linux = [0, 1, 3, 2, 3, 3, 3, 3]

        fe_param = self.get_frontend()
        ts_ter.frequency = int(fe_param.frequency / 1000)
        ts_ter.bandwidth = fe_param.u.ofdm.bandwidth
        i = fe_param.u.ofdm.code_rate_HP
        ts_ter.code_rate_hp_stream = code_rate_dvb_of_linux[i]
        i = fe_param.u.ofdm.code_rate_LP
        ts_ter.code_rate_lp_stream = code_rate_dvb_of_linux[i]
        i = fe_param.u.ofdm.constellation
        ts_ter.constellation = constellation_dvb_of_linux[i]
        i = fe_param.u.ofdm.transmission_mode
        ts_ter.transmission_mode = transmission_mode_dvb_of_linux[i]
        ts_ter.guard_interval = fe_param.u.ofdm.guard_interval

    def get_tuned_param(self):
        ts_ter = dvb.TsTer(self.ts_key, self.src_key)
        code_rate_dvb_of_linux = [7, 0, 1, 2, 7, 3, 7, 4, 7, 7, 7, 7]
        constellation_dvb_of_linux = [0, 1, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3]
        transmission_mode_dvb_of_linux = [0, 1, 3, 2, 3, 3, 3, 3]

        fe_param = self.get_frontend()
        ts_ter.frequency = int(fe_param.frequency / 1000)
        ts_ter.bandwidth = fe_param.u.ofdm.bandwidth
        i = fe_param.u.ofdm.code_rate_HP
        ts_ter.code_rate_hp_stream = code_rate_dvb_of_linux[i]
        i = fe_param.u.ofdm.code_rate_LP
        ts_ter.code_rate_lp_stream = code_rate_dvb_of_linux[i]
        i = fe_param.u.ofdm.constellation
        ts_ter.constellation = constellation_dvb_of_linux[i]
        i = fe_param.u.ofdm.transmission_mode
        ts_ter.transmission_mode = transmission_mode_dvb_of_linux[i]
        ts_ter.guard_interval = fe_param.u.ofdm.guard_interval
        return ts_ter

    def tune(self, ts_ter):
        transmission_mode_linux_of_dvb = [
            linuxdvb.TRANSMISSION_MODE_2K,
            linuxdvb.TRANSMISSION_MODE_8K,
            linuxdvb.TRANSMISSION_MODE_4K,
            linuxdvb.TRANSMISSION_MODE_AUTO,
        ]
        constellation_linux_of_dvb = [
            linuxdvb.QPSK,
            linuxdvb.QAM_16,
            linuxdvb.QAM_64,
            linuxdvb.QAM_AUTO,
        ]
        code_rate_linux_of_dvb = [
            linuxdvb.FEC_1_2,
            linuxdvb.FEC_2_3,
            linuxdvb.FEC_3_4,
            linuxdvb.FEC_5_6,
            linuxdvb.FEC_7_8,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
        ]

        fe_param = linuxdvb.dvb_frontend_parameters()
        fe_param.frequency = ts_ter.frequency * 1000
        fe_param.inversion = linuxdvb.INVERSION_AUTO
        fe_param.u.ofdm.bandwidth = ts_ter.bandwidth
        i = ts_ter.code_rate_hp_stream
        fe_param.u.ofdm.code_rate_HP = code_rate_linux_of_dvb[i]
        i = ts_ter.code_rate_lp_stream
        fe_param.u.ofdm.code_rate_LP = code_rate_linux_of_dvb[i]
        i = ts_ter.constellation
        fe_param.u.ofdm.constellation = constellation_linux_of_dvb[i]
        i = ts_ter.transmission_mode
        fe_param.u.ofdm.transmission_mode = transmission_mode_linux_of_dvb[i]
        fe_param.u.ofdm.guard_interval = ts_ter.guard_interval
        fe_param.u.ofdm.hierarchy_information = linuxdvb.HIERARCHY_AUTO

        ret = self.set_frontend(fe_param)
        return ret


class QpskFrontend(DvbFrontend):
    def get_sat_frequency(self, fe_freq):
        if (self.source.lo_freq < 6000):
            return self.source.lo_freq - fe_freq
        else:
            return self.source.lo_freq + fe_freq

    def get_tuning_param(self, ts_sat):
        fec_inner_dvb_of_linux = [0, 1, 2, 3, 8, 4, 0, 5, 6, 0, 7, 9]

        fe_param = self.get_frontend()
        fe_freq = int(fe_param.frequency / 1000)
        ts_sat.frequency = self.get_sat_frequency(fe_freq)
        ts_sat.fec_inner = fec_inner_dvb_of_linux[fe_param.u.qpsk.fec_inner]
        ts_sat.symbol_rate = int((fe_param.u.qpsk.symbol_rate + 5) / 1000)

        # get more informations
        dtv_property = linuxdvb.dtv_property()
        properties = linuxdvb.dtv_properties()
        properties.num = 1
        properties.props = ctypes.pointer(dtv_property)

        # get voltage to determine polarization
        dtv_property.cmd = linuxdvb.DTV_VOLTAGE
        err = fcntl.ioctl(self.fd, linuxdvb.FE_GET_PROPERTY, properties)
        if (err == 0 and dtv_property.result == 0):
            if (dtv_property.u.data == linuxdvb.SEC_VOLTAGE_13):
                ts_sat.polarization = 1
            elif (dtv_property.u.data == linuxdvb.SEC_VOLTAGE_18):
                ts_sat.polarization = 0

        # get modulation system
        dtv_property.cmd = linuxdvb.DTV_DELIVERY_SYSTEM
        err = fcntl.ioctl(self.fd, linuxdvb.FE_GET_PROPERTY, properties)
        if (err == 0 and dtv_property.result == 0):
            if (dtv_property.u.data == 0):
                ts_sat.modulation_system = 0
            elif (dtv_property.u.data == linuxdvb.SYS_DVBS2):
                ts_sat.modulation_system = 1

    def get_tuned_param(self):
        fec_inner_dvb_of_linux = [0, 1, 2, 3, 8, 4, 0, 5, 6, 0, 7, 9]
        ts_sat = dvb.TsSat(self.ts_key, self.src_key)

        fe_param = self.get_frontend()
        fe_freq = int(fe_param.frequency / 1000)
        ts_sat.frequency = self.get_sat_frequency(fe_freq)
        ts_sat.fec_inner = fec_inner_dvb_of_linux[fe_param.u.qpsk.fec_inner]
        ts_sat.symbol_rate = int((fe_param.u.qpsk.symbol_rate + 5) / 1000)

        # get more informations
        dtv_property = linuxdvb.dtv_property()
        properties = linuxdvb.dtv_properties()
        properties.num = 1
        properties.props = ctypes.pointer(dtv_property)

        # get voltage to determine polarization
        dtv_property.cmd = linuxdvb.DTV_VOLTAGE
        err = fcntl.ioctl(self.fd, linuxdvb.FE_GET_PROPERTY, properties)
        if (err == 0 and dtv_property.result == 0):
            if (dtv_property.u.data == linuxdvb.SEC_VOLTAGE_13):
                ts_sat.polarization = 1
            elif (dtv_property.u.data == linuxdvb.SEC_VOLTAGE_18):
                ts_sat.polarization = 0

        # get modulation system
        dtv_property.cmd = linuxdvb.DTV_DELIVERY_SYSTEM
        err = fcntl.ioctl(self.fd, linuxdvb.FE_GET_PROPERTY, properties)
        if (err == 0 and dtv_property.result == 0):
            if (dtv_property.u.data == 0):
                ts_sat.modulation_system = 0
            elif (dtv_property.u.data == linuxdvb.SYS_DVBS2):
                ts_sat.modulation_system = 1
        return ts_sat

    def set_voltage(self, voltage):
        # this is old method
        #fcntl.ioctl(self.fd, linuxdvb.FE_SET_VOLTAGE, voltage)
        #return

        voltage_property = linuxdvb.dtv_property()
        voltage_property.cmd = linuxdvb.DTV_VOLTAGE
        voltage_property.u.data = voltage

        properties = linuxdvb.dtv_properties()
        properties.num = 1
        properties.props = ctypes.pointer(voltage_property)

        return fcntl.ioctl(self.fd, linuxdvb.FE_SET_PROPERTY, properties)

    def set_delivery_system(self, delivery):
        dtv_property = linuxdvb.dtv_property()
        dtv_property.cmd = linuxdvb.DTV_DELIVERY_SYSTEM
        dtv_property.u.data = delivery

        properties = linuxdvb.dtv_properties()
        properties.num = 1
        properties.props = ctypes.pointer(dtv_property)

        return fcntl.ioctl(self.fd, linuxdvb.FE_SET_PROPERTY, properties)

    def set_lnb(self, ts_sat):
        # set tone
        ret = self.set_tone(0)
        if (ret):
            print("FE_SET_TONE failed")
            #return False

        # set DiSEqC
        time.sleep(0.015)
        cmd = linuxdvb.dvb_diseqc_master_cmd()
        cmd.msg[0] = 0xe0
        cmd.msg[1] = 0x10
        cmd.msg[2] = 0x00
        cmd.msg_len = 3
        #print("DiSEqC len:", cmd.msg_len, ", cmd:", hex(cmd.msg[0]),
        #      hex(cmd.msg[1]), hex(cmd.msg[2]), hex(cmd.msg[3]),
        #      hex(cmd.msg[4]), hex(cmd.msg[5]))
        ret = fcntl.ioctl(self.fd, linuxdvb.FE_DISEQC_SEND_MASTER_CMD, cmd)
        if (ret):
            print("FE_DISEQC_SEND_MASTER_CMD failed")
            return False

        time.sleep(0.015)

        # set polarization
        ret = 0
        if (ts_sat.polarization is 1):    # vertical
            ret = self.set_voltage(linuxdvb.SEC_VOLTAGE_13)
        elif (ts_sat.polarization is 0):  # horizontal
            ret = self.set_voltage(linuxdvb.SEC_VOLTAGE_18)
        if (ret):
            print("set_voltage failed")
            return False

        # set modulation_system
        ret = 0
        if (ts_sat.modulation_system is 0):
            ret = self.set_delivery_system(linuxdvb.SYS_DVBS)
        else:
            ret = self.set_delivery_system(linuxdvb.SYS_DVBS2)
        if (ret):
            print("set_delivery_system failed")
            return False
        return True

    def set_tone(self, tone):
        if (tone):
            on_off = linuxdvb.SEC_TONE_ON
        else:
            on_off = linuxdvb.SEC_TONE_OFF
        ret = fcntl.ioctl(self.fd, linuxdvb.FE_SET_TONE, on_off)
        return ret

    def set_diseqc(self, ts_sat):
        # set tone
        ret = self.set_tone(0)
        if (ret):
            print("FE_SET_TONE failed")
            #return False

        # set polarization
        ret = 0
        if (ts_sat.polarization is 1):    # vertical
            ret = self.set_voltage(linuxdvb.SEC_VOLTAGE_13)
        elif (ts_sat.polarization is 0):  # horizontal
            ret = self.set_voltage(linuxdvb.SEC_VOLTAGE_18)
        if (ret):
            print("set_voltage failed")
            return False

        # set DiSEqC
        time.sleep(0.015)
        cmd = linuxdvb.dvb_diseqc_master_cmd()
        cmd.msg[0] = 0xe0
        cmd.msg[1] = 0x10
        cmd.msg[2] = 0x38
        cmd.msg[3] = 0xf0
        if (self.source.diseqc_version >= 20):
            cmd.msg[0] |= 0x02
        cmd.msg[3] |= ((self.source.link_type - 1) << 2)
        if (ts_sat.polarization is 0 or ts_sat.polarization is 2):
            cmd.msg[3] |= 0x2
        if (self.source.continuous_tone):
            cmd.msg[3] |= 0x1
        cmd.msg_len = 4
        #print("DiSEqC len:", cmd.msg_len, ", cmd:", hex(cmd.msg[0]),
        #      hex(cmd.msg[1]), hex(cmd.msg[2]), hex(cmd.msg[3]),
        #      hex(cmd.msg[4]), hex(cmd.msg[5]))
        ret = fcntl.ioctl(self.fd, linuxdvb.FE_DISEQC_SEND_MASTER_CMD, cmd)
        if (ret):
            print("FE_DISEQC_SEND_MASTER_CMD failed")
            return False

        time.sleep(0.015)

        # set burst
        if (self.source.link_type == 1 or self.source.link_type == 3):
            burst = linuxdvb.SEC_MINI_A
        else:
            burst = linuxdvb.SEC_MINI_B
        ret = fcntl.ioctl(self.fd, linuxdvb.FE_DISEQC_SEND_BURST, burst)

        time.sleep(0.015)

        # set tone
        ret = self.set_tone(self.source.continuous_tone)
        if (ret):
            print("FE_SET_TONE failed")
            return False
        return True

    def tune(self, ts_sat):
        fec_inner_linux_of_dvb = [
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_1_2,
            linuxdvb.FEC_2_3,
            linuxdvb.FEC_3_4,
            linuxdvb.FEC_5_6,
            linuxdvb.FEC_7_8,
            linuxdvb.FEC_8_9,
            linuxdvb.FEC_3_5,
            linuxdvb.FEC_4_5,
            linuxdvb.FEC_9_10,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
            linuxdvb.FEC_AUTO,
        ]

        if (self.source is None):
            return False
        if (self.source.link_type < 0 or self.source.link_type > 4):
            return False

        lo_freq = self.source.lo_freq
        #lo_freq2 = self.source.lo_freq2

        fe_param = linuxdvb.dvb_frontend_parameters()
        # TODO: lo_freq2
        fe_param.frequency = abs(ts_sat.frequency - lo_freq) * 1000
        fe_param.inversion = linuxdvb.INVERSION_AUTO
        fe_param.u.qpsk.symbol_rate = ts_sat.symbol_rate * 1000
        fe_param.u.qpsk.fec_inner = fec_inner_linux_of_dvb[ts_sat.fec_inner]

        if (fe_param.u.qpsk.symbol_rate < self.feinfo.symbol_rate_min):
            return False
        if (fe_param.u.qpsk.symbol_rate > self.feinfo.symbol_rate_max):
            return False

        if (1 <= self.source.link_type <= 4):
            ret = self.set_diseqc(ts_sat)
        else:
            ret = self.set_lnb(ts_sat)
        if (ret is False):
            return False

        ret = self.set_frontend(fe_param)
        if (ret is False):
            print("set_frontend failed")
        return ret

    def get_polarization(self):
        # get voltage to determine polarization
        dtv_property = linuxdvb.dtv_property()
        properties = linuxdvb.dtv_properties()
        properties.num = 1
        properties.props = ctypes.pointer(dtv_property)

        dtv_property.cmd = linuxdvb.DTV_VOLTAGE
        err = fcntl.ioctl(self.fd, linuxdvb.FE_GET_PROPERTY, properties)
        if (err == 0 and dtv_property.result == 0):
            if (dtv_property.u.data == linuxdvb.SEC_VOLTAGE_13):
                return 1
        return 0


class FileFrontend(Frontend):
    def __init__(self, card=0, dev=0, rw=0, blocking=0):
        Frontend.__init__(self, card, dev, rw, blocking)
        self.fe_filename = "/dev/dvb/adapter" + str(card) + "/dvr" + str(dev)
        flags = 0
        if rw:
            flags = flags | os.O_RDWR
        else:
            flags = flags | os.O_WRONLY
        if not blocking:
            flags = flags | os.O_NONBLOCK
        self.fd = os.open(self.fe_filename, flags)
        self.poller = poll_loop.PollLoop()
        self.tsfd = 0
        self.ts_file_name = ""
        self.num_to_read = 0
        self.poller.register_timer(self.feed_file, 100, 100)
        #self.feinfo.name = "FILE Frontend"
        self.feinfo.type = FE_FILE
        self.type_str = fe_type[self.feinfo.type]

    def feed_file(self):
        if (self.tsfd):
            read_bytes = os.read(self.tsfd, self.num_to_read)
            if (len(read_bytes) == 0):
                # loop
                os.close(self.tsfd)
                self.tsfd = os.open(self.ts_file_name, os.O_RDONLY)
                read_bytes = os.read(self.tsfd, self.num_to_read)
                event = linuxdvb.dvb_frontend_event()
                event.status = self.read_status() | FE_LOOPED
                self.notify_observers(event)
            os.write(self.fd, read_bytes)
            del read_bytes

    def read_status(self):
        if (self.tsfd):
            return linuxdvb.FE_HAS_SIGNAL | linuxdvb.FE_HAS_LOCK
        else:
            return 0

    def get_tuning_param(self, ts_file):
        ts_file.pathname = self.ts_file_name

    def get_tuned_param(self):
        ts_file = dvb.TsFile(self.ts_key, self.src_key)
        ts_file.pathname = self.ts_file_name
        return ts_file

    def tune(self, ts_file):
        return self.set_frontend(ts_file.pathname)

    def set_frontend(self, ts_file_name, kbps=20000):
        if (self.tsfd):
            os.close(self.tsfd)

        self.ts_file_name = ts_file_name
        event = linuxdvb.dvb_frontend_event()
        event.status = linuxdvb.FE_REINIT
        self.notify_observers(event)

        self.num_to_read = int(kbps * 100 / 8)
        try:
            self.tsfd = os.open(self.ts_file_name, os.O_RDONLY)
            event.status = (linuxdvb.FE_HAS_SIGNAL | linuxdvb.FE_HAS_LOCK)
            self.notify_observers(event)
            return True
        except:
            self.tsfd = 0
            event.status = 0
            self.notify_observers(event)
            return False


if __name__ == "__main__":
    import sys
    import argparse

    def get_fe_sat():
        fe = QpskFrontend(1, 0)
        ts = dvb.TsSat(0, 0)
        # # refer to services.sql, ts_params_sat table
        #param.set_tuning_param(12567, 1, 30000, 7, 1)
        #param.set_tuning_param(4000, 0, 28125, 0, 0)
        ts.set_tuning_param(12658, 1, 21096, 0, 0)
        ts.frequency = 12658
        fe.source = dvb.SatSource(0, 0, 0, "unknown source")
        fe.source.link_type = 1
        fe.source.continuous_tone = 0
        fe.source.lo_freq = 11300
        return fe, ts

    def get_fe_ter():
        fe = OfdmFrontend(0, 0)
        ts = dvb.TsTer(0, 0)
        #ts.set_tuning_param(177500, linuxdvb.BANDWIDTH_7_MHZ)
        ts.set_tuning_param(746000, linuxdvb.BANDWIDTH_8_MHZ)
        fe.source = dvb.Source(0, 2, "unknown source")
        return fe, ts

    prg_desc = "Test frontend. Tune to frequency and print status."
    parser = argparse.ArgumentParser(description=prg_desc)
    parser.add_argument('-a',
                        action='store',
                        type=int,
                        help="use DVB /dev/dvb/adapterA/")
    parser.add_argument('-d',
                        action='store',
                        type=int,
                        help="(DVB-S/S2) 0: use LNB, 1-4: use DiSEqC (1-4)")
    parser.add_argument('-l',
                        action='store',
                        type=int,
                        help="(DVB-S/S2) LNB frequency in MHz")
    parser.add_argument('-t',
                        action='store',
                        type=int,
                        help="(DVB-S/S2) 0: tone off, 1: tone on")
    parser.add_argument('-p',
                        action='store',
                        type=int,
                        help="(DVB-S/S2) 0: horizontal, 1: vertical")
    parser.add_argument('-s',
                        action='store',
                        type=int,
                        help="(DVB-S/S2) symbol rate")
    parser.add_argument('-b',
                        action='store',
                        type=int,
                        help="(DVB-T/T2) bandwidth; 0: 8MHz, 1: 7MHz, 2: 6MHz")
    parser.add_argument('freq',
                        action='store',
                        type=int,
                        nargs='?',
                        help="frequency in MHz")

    argv = sys.argv[:]
    argv.pop(0)
    args = parser.parse_args(argv)
    if (args.a is None):
        args.a = 0
    if (args.d is None):
        args.d = 0
    if (args.l is None):
        args.l = 11300
    if (args.t is None):
        args.t = 0
    if (args.p is None):
        args.p = 0
    if (args.s is None):
        args.s = 27500
    if (args.b is None):
        args.b = 0

    filename = "/dev/dvb/adapter" + str(args.a) + "/frontend0"
    print("open", filename)
    fd = os.open(filename, os.O_RDONLY)
    info = linuxdvb.dvb_frontend_info()
    fcntl.ioctl(fd, linuxdvb.FE_GET_INFO, info)
    os.close(fd)

    if (info.type == FE_OFDM):
        fe = OfdmFrontend(args.a, 0)
        fe.source = dvb.Source(0, FE_OFDM, "unknown source")
    elif (info.type == FE_QPSK):
        fe = QpskFrontend(args.a, 0)
        fe.source = dvb.SatSource(0, FE_QPSK, 0, "unknown source")
    else:
        # TODO: FE_QAM
        print("Not yet implemented for FE type: %d" % info.type)
        sys.exit()

    print()
    print(fe)
    print()

    if (args.freq is None):
        sys.exit()

    if (info.type == FE_OFDM):
        ts = dvb.TsTer(0, 0)
        ts.set_tuning_param(args.freq * 1000, args.b)
    elif (info.type == FE_QPSK):
        fe = QpskFrontend(args.a, 0)
        ts = dvb.TsSat(0, 0)
        # # refer to services.sql, ts_params_sat table
        #param.set_tuning_param(12567, 1, 30000, 7, 1)
        #param.set_tuning_param(4000, 0, 28125, 0, 0)
        ts.set_tuning_param(args.freq, args.p, args.s, 0, 0, 0)
        ts.frequency = 12658
        fe.source.link_type = args.d
        fe.source.continuous_tone = args.t
        fe.source.lo_freq = args.l

    print(fe.source)
    print("_______________________________________________")
    print("TUNING PARAM:")
    print(ts)
    print(ts.detail_param_str())
    ret = fe.tune(ts)
    print("tuning result:", ret)
    print(linuxdvb.fe_status)
    while(1):
        time.sleep(1)
        status = fe.read_status()
        status_strs = []
        for key in linuxdvb.fe_status:
            if (status & key):
                status_strs.append(linuxdvb.fe_status[key][3:])
        status_str = '(' + ', '.join(status_strs) + ')'
        tuned_ts = fe.get_tuned_param()
        #string = str(tuned_ts)
        string = tuned_ts.detail_param_str()
        string += ", SNR %04x" % fe.read_snr()
        string += ", BER %04x" % fe.read_ber()
        string += ", STR %04x" % fe.read_signal_strength()
        string += " --> "
        string += hex(status) + " " + status_str
        print(string)
