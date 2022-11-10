#
# section and descriptor parser
#
# Copyright (c) 2008 by K. Uhm <kayzm0@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#

import datetime

def bcd_to_integer(bcdval):
    """Convert a string BCD value into a normal integer."""
    val = 0
    for i in range(28, -1, -4):
        val += ((bcdval >> i) & 0x0f)
        if (i != 0):
            val *= 10
    return val

def dvbduration_to_seconds(dvbduration):
    """Convert from a 3 byte DVB BCD duration to a number of seconds."""
    seconds = 0

    seconds += bcd_to_integer(dvbduration[0]) * 60 * 60
    seconds += bcd_to_integer(dvbduration[1]) * 60
    seconds += bcd_to_integer(dvbduration[2])

    return seconds

def mjd_to_ymdwd(mjd):
    """Convert mjd to (Y, M, D, WD) according to ETSI EN 300 468 Annex C.

       Y: Year from 1900 (e.g. for 2003, Y = 103)
       M: Month from January (= 1) to December (= 12)
       D: Day of month from 1 to 31
       WD: Day of week from Monday (= 1) to Sunday (= 7)"""
    year = (mjd * 100 - 1507820) // 36525
    mon = ((mjd * 10000 - 149561000) - (year * 36525 // 100) * 10000) // 306001
    day = mjd - 14956 - (year * 36525 // 100) - (mon * 306001 // 10000)
    if ((mon == 14) or (mon == 15)):
        k = 1
    else:
        k = 0
    year += k
    mon = mon - 1 - k * 12
    wday = (mjd + 2) % 7 + 1
    return (year, mon, day, wday)

def dvbdate_to_datetime(dvbdate):
    """Convert from a 5 byte DVB UTC date to datetime

    Note: this functions expects the DVB date in network byte order.
    """
    mjd = (dvbdate[0] << 8) | dvbdate[1]
    year, month, day, wday = mjd_to_ymdwd(mjd)
    year += 1900
    hour = bcd_to_integer(dvbdate[2])
    if (hour > 23):
        hour = 23
    minute = bcd_to_integer(dvbdate[3])
    if (minute > 59):
        minute = 59
    second = bcd_to_integer(dvbdate[4])
    if (second > 59):
        second = 59
    return datetime.datetime(year, month, day, hour, minute, second)

def dvbdate_to_unixtime(dvbdate):
    """Convert from a 5 byte DVB UTC date to unix time.

    Note: this functions expects the DVB date in network byte order.
    """
    mjd = (dvbdate[0] << 8) | dvbdate[1]
    hour = bcd_to_integer(dvbdate[2])
    minute = bcd_to_integer(dvbdate[3])
    second = bcd_to_integer(dvbdate[4])
    return ((mjd - 40587) * 86400 + hour * 3600 + minute * 60 + second)

CHARSET_CODE_MAP = {
    0x01: "ISO8859-5",
    0x02: "ISO8859-6",
    0x03: "ISO8859-7",
    0x04: "ISO8859-8",
    0x05: "ISO8859-9",
    0x06: "ISO8859-10",
    0x07: "ISO8859-11",
    0x09: "ISO8859-13",
    0x0a: "ISO8859-14",
    0x0b: "ISO8859-15",
    0x11: "UTF16",
    0x12: "EUC-KR",
    0x13: "GB2312",
    0x14: "GBK",
    0x15: "UTF8",
}

CHARSET_EXT_MAP = {
    0x0001: "ISO8859-1",
    0x0002: "ISO8859-2",
    0x0003: "ISO8859-3",
    0x0004: "ISO8859-4",
    0x0005: "ISO8859-5",
    0x0006: "ISO8859-6",
    0x0007: "ISO8859-7",
    0x0008: "ISO8859-8",
    0x0009: "ISO8859-9",
    0x000a: "ISO8859-10",
    0x000b: "ISO8859-11",
    0x000d: "ISO8859-13",
    0x000e: "ISO8859-14",
    0x000f: "ISO8859-15",
}

def dvb_charset(dvb_text, default_charset = "ISO8859-9"):
    """Determine the (string codec compatable) character set of a dvb string."""
    used = 0

    while True:
        if (len(dvb_text) == 0):
            break
        if (dvb_text[0] >= 0x20):
            break
        if (dvb_text[0] == 0x10):
            if (len(dvb_text) < 3):
                break
            ext = (dvb_text[1] << 8) | dvb_text[2]
            charset = CHARSET_EXT_MAP.get(ext, None)
            if (charset):
                used = 3
        elif (dvb_text[0] == 0x1f):
            encoding_type_id = dvb_text[1]
            charset = default_charset
            if (charset):
                used = 2
        else:
            code = dvb_text[0]
            charset = CHARSET_CODE_MAP.get(code, None)
            if (charset):
                used = 1
        break
    if (used == 0):
        charset = default_charset
    return charset, used

