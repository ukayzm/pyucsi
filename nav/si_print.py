#! /usr/bin/env python

import dvbsi


def hexdump(indent, prefix, src, length=16):
    N = 0
    result = ''
    space = "    " * indent
    empty_prefix = " " * len(prefix)
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02x" % (x) for x in s])
        result += space + prefix + "%02x: %-*s\n" % (N, length * 3, hexa)
        N += length
        prefix = empty_prefix
    return result


def print_descriptors(indent, descriptors):
    space = "    " * indent
    for raw_dsc in descriptors:
        dsc_parser = dvbsi.DESCRIPTOR_MAP.get(raw_dsc.tag)
        if (dsc_parser is None):
            print(space + raw_dsc.__str__())
        else:
            dsc = dsc_parser(raw_dsc.data)
            for line in dsc.__str__().splitlines():
                print(space + line)
        print(hexdump(indent, " ", raw_dsc.data))


def print_section(section):
    print()
    print(section)
    if (section.table_id == dvbsi.STAG_NETWORK_INFORMATION_ACTUAL or
        section.table_id == dvbsi.STAG_NETWORK_INFORMATION_OTHER or
        section.table_id == dvbsi.STAG_BOUQUET_ASSOCIATION):
        # print NIT/BAT
        # descriptor loop 1
        print_descriptors(2, section.descriptors)
        for transport in section.transports:
            print("  *", transport)
            # descriptor loop 2
            print_descriptors(2, transport.descriptors)
    elif (section.table_id == dvbsi.STAG_SERVICE_DESCRIPTION_ACTUAL or
          section.table_id == dvbsi.STAG_SERVICE_DESCRIPTION_OTHER):
        # print SDT
        for service in section.services:
            print("  *", service)
            # descriptor loop
            print_descriptors(2, service.descriptors)
    elif (section.table_id == dvbsi.STAG_PROGRAM_MAP):
        # print PMT
        # descriptor loop 1
        print_descriptors(2, section.descriptors)
        for stream in section.streams:
            print("  *", stream)
            # descriptor loop 2
            print_descriptors(2, stream.descriptors)
    elif (section.table_id >= dvbsi.STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL and
          section.table_id <= 0x6f):
        # print EIT
        for event in section.events:
            print("  *", event)
            # descriptor loop 2
            print_descriptors(2, event.descriptors)
    elif (section.table_id == dvbsi.STAG_TIME_OFFSET):
        # print TOT
        print_descriptors(2, section.descriptors)
