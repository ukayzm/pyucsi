import unittest
import struct
import sys

sys.path.append("..")

import dvbsi


class DvbTypesTest(unittest.TestCase):
    def test_010_bcd_to_integer(self):
        "bcd_to_integer"
        bcd_val = 0x34
        int_val = dvbsi.bcd_to_integer(bcd_val)
        self.assertEqual(int_val, 34)
        bcd_val = 0x1234
        int_val = dvbsi.bcd_to_integer(bcd_val)
        self.assertEqual(int_val, 1234)
        bcd_val = 0x12345678
        int_val = dvbsi.bcd_to_integer(bcd_val)
        self.assertEqual(int_val, 12345678)
        bcd_val = 0x98765432
        int_val = dvbsi.bcd_to_integer(bcd_val)
        self.assertEqual(int_val, 98765432)

    def test_020_dvbduration_to_seconds(self):
        "dvbduration_to_seconds"
        buf = struct.pack("BBB", 0x0, 0x1, 0x0)
        seconds = dvbsi.dvbduration_to_seconds(buf)
        self.assertEqual(seconds, 60)
        buf = struct.pack("BBB", 0x1, 0x0, 0x0)
        seconds = dvbsi.dvbduration_to_seconds(buf)
        self.assertEqual(seconds, 3600)
        buf = struct.pack("BBB", 0x24, 0x0, 0x0)
        seconds = dvbsi.dvbduration_to_seconds(buf)
        self.assertEqual(seconds, 86400)

    def test_030_mjd_to_ymdwd(self):
        "mjd_to_ymdwd"
        mjd = 45218
        year, month, day, wday = dvbsi.mjd_to_ymdwd(mjd)
        self.assertEqual(year, 82)
        self.assertEqual(month, 9)
        self.assertEqual(day, 6)
        self.assertEqual(wday, 1)

    def test_040_dvbdate_to_datetime(self):
        "dvbdate_to_datetime"
        mjd = 45218
        mjd_0 = (mjd >> 8) & 0xff
        mjd_1 = mjd & 0xff
        buf = struct.pack("BBBBB", mjd_0, mjd_1, 0x9, 0x45, 0x32)
        date_time = dvbsi.dvbdate_to_datetime(buf)
        self.assertEqual(date_time.year, 1982)
        self.assertEqual(date_time.month, 9)
        self.assertEqual(date_time.day, 6)
        self.assertEqual(date_time.hour, 9)
        self.assertEqual(date_time.minute, 45)
        self.assertEqual(date_time.second, 32)
        mjd = 54114
        mjd_0 = (mjd >> 8) & 0xff
        mjd_1 = mjd & 0xff
        buf = struct.pack("BBBBB", mjd_0, mjd_1, 0x13, 0x18, 0x59)
        date_time = dvbsi.dvbdate_to_datetime(buf)
        self.assertEqual(date_time.year, 2007)
        self.assertEqual(date_time.month, 1)
        self.assertEqual(date_time.day, 14)
        self.assertEqual(date_time.hour, 13)
        self.assertEqual(date_time.minute, 18)
        self.assertEqual(date_time.second, 59)
        mjd = 54653
        mjd_0 = (mjd >> 8) & 0xff
        mjd_1 = mjd & 0xff
        buf = struct.pack("BBBBB", mjd_0, mjd_1, 0x5, 0x59, 0x33)
        date_time = dvbsi.dvbdate_to_datetime(buf)
        self.assertEqual(date_time.year, 2008)
        self.assertEqual(date_time.month, 7)
        self.assertEqual(date_time.day, 6)
        self.assertEqual(date_time.hour, 5)
        self.assertEqual(date_time.minute, 59)
        self.assertEqual(date_time.second, 33)

    def test_050_dvbdate_to_unixtime(self):
        "dvbdate_to_unixtime"
        mjd = 54653
        mjd_0 = (mjd >> 8) & 0xff
        mjd_1 = mjd & 0xff
        buf = struct.pack("BBBBB", mjd_0, mjd_1, 0x5, 0x59, 0x33)
        unixtime = dvbsi.dvbdate_to_unixtime(buf)
        self.assertEqual(unixtime, 1215323973)
        mjd = 54693
        mjd_0 = (mjd >> 8) & 0xff
        mjd_1 = mjd & 0xff
        buf = struct.pack("BBBBB", mjd_0, mjd_1, 0x11, 0x45, 0x03)
        unixtime = dvbsi.dvbdate_to_unixtime(buf)
        self.assertEqual(unixtime, 1218800703)

    def test_060_dvb_charset(self):
        "dvb_charset"
        # default_charset = "ISO6937" # XXX
        default_charset = "ISO8859-9"

        charset, used = dvbsi.dvb_charset(b"")
        self.assertEqual(charset, default_charset)
        self.assertEqual(used, 0)

        charset, used = dvbsi.dvb_charset(b"asdf")
        self.assertEqual(charset, default_charset)
        self.assertEqual(used, 0)

        charset, used = dvbsi.dvb_charset(b"asdf", "ISO8859-5")
        self.assertEqual(charset, "ISO8859-5")
        self.assertEqual(used, 0)

        string = struct.pack("B4s", 0, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, default_charset)
        self.assertEqual(used, 0)

        string = struct.pack("B4s", 0x01, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, "ISO8859-5")
        self.assertEqual(used, 1)

        string = struct.pack("B4s", 0x02, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, "ISO8859-6")
        self.assertEqual(used, 1)

        string = struct.pack("B4s", 0x03, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, "ISO8859-7")
        self.assertEqual(used, 1)

        string = struct.pack("BBB4s", 0x10, 0x00, 0x01, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, "ISO8859-1")
        self.assertEqual(used, 3)

        string = struct.pack("BBB4s", 0x10, 0x00, 0x0f, b"asdf")
        charset, used = dvbsi.dvb_charset(string)
        self.assertEqual(charset, "ISO8859-15")
        self.assertEqual(used, 3)

if __name__ == "__main__":
    unittest.main(argv=('', '-v'))
