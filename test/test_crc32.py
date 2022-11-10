import unittest
import sys
import struct

sys.path.append("..")

import dvbsi

class Crc32Test(unittest.TestCase):
    def test_010(self):
        "checking crc32"
        buf1 = b"\x16\x75\xa8\xf0\x2e\x79\x9b\x47"
        crc = dvbsi.crc32(buf1)
        buf2 = struct.pack("8sBBBB", buf1,
                ((crc >> 24) & 0xff),
                ((crc >> 16) & 0xff),
                ((crc >> 8) & 0xff),
                ((crc >> 0) & 0xff))
        self.assertEqual(dvbsi.crc32(buf2), 0)


if __name__ == "__main__":
    unittest.main(argv=('', '-v'))
