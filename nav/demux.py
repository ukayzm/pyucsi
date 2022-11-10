#! /usr/bin/env python3.1

import linuxdvb
import fcntl
import os

class Demux:
    def __init__(self, card = 0, dev = 0, blocking=1):
        filename = "/dev/dvb/adapter" + str(card) + "/demux" + str(dev)
        if not blocking:
            flags = os.O_NONBLOCK | os.O_RDWR
        else:
            flags = os.O_RDWR
        self.fd = os.open(filename, flags)

    def __del__(self):
        os.close(self.fd)

    def fileno(self):
        return self.fd

    def set_blocking(self, blocking):
        if blocking:
            fcntl.fcntl(self.fd, fcntl.F_SETFL, 0)
        else:
            fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)

    def start(self):
        """Start the filtering operation defined via calls to set_filter or
        set_pes_filter."""
        fcntl.ioctl(self.fd, linuxdvb.DMX_START)

    def stop(self):
        """Stop the filtering operation defined via calls to set_filter or
        set_pes_filter."""
        fcntl.ioctl(self.fd, linuxdvb.DMX_STOP)

    def set_filter(self, pid, _filter, mask, mode, timeout, flags):
        """Set up a filter according to the _filter and mask arguments."""
        self.param = linuxdvb.dmx_sct_filter_params()

        if len(_filter) != len(mask) or len(_filter) > linuxdvb.DMX_FILTER_SIZE:
            raise IOError()
        if mode is not None and len(mode) != len(_filter):
            raise IOError()

        self.param.pid = pid
        self.pid = pid
        self.param.timeout = timeout
        self.param.flags = flags
        for i in range(0, linuxdvb.DMX_FILTER_SIZE):
            if (i < len(_filter)):
                self.param.filter.filter[i] = _filter[i]
                self.param.filter.mask[i] = mask[i]
                if mode is not None:
                    self.param.filter.mode[i] = mode[i]
                else:
                    self.param.filter.mode[i] = 0
            else:
                self.param.filter.filter[i] = 0
                self.param.filter.mask[i] = 0
                self.param.filter.mode[i] = 0

        fcntl.ioctl(self.fd, linuxdvb.DMX_SET_FILTER, self.param)

    def set_pes_filter(self, pid, input, output, pes_type, flags):
        """Set up a PES filter according to the parameters provided."""
        p = linuxdvb.dmx_pes_filter_params()

        p.pid = pid
        p.input = input
        p.output = output
        p.pes_type = pes_type
        p.flags = flags

        fcntl.ioctl(self.fd, linuxdvb.DMX_SET_PES_FILTER, p)

    def set_buffer_size(self, size):
        """Set the size of the circular buffer used for filtered data."""
        fcntl.ioctl(self.fd, linuxdvb.DMX_SET_BUFFER_SIZE, size)

    def get_stc(self, num):
        stc = linuxdvb.dmx_stc()

        stc.num = num
        fcntl.ioctl(self.fd, linuxdvb.DMX_GET_STC, stc)
        return stc.base, stc.stc

    def read(self, length = 4096):
        return os.read(self.fd, length)

