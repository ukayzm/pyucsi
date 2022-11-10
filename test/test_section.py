import unittest
import struct
import random
import sys

sys.path.append("../src")

import dvbsi


class SectionTest(unittest.TestCase):
    def test_010(self):
        "Section - checking length"
        sec = dvbsi.Section(b"aa")
        self.assertEqual(sec.table_id, -1)
        sec = dvbsi.Section(b"aaaa")
        self.assertEqual(sec.table_id, -1)

    def test_020(self):
        "Section - extracting table_id, length and data"
        buf = struct.pack("BBBBBBBB", 1, 0, 5, 0, 0, 0, 0, 0)
        sec = dvbsi.Section(buf)
        self.assertEqual(sec.table_id, 1)
        self.assertEqual(sec.length, 5)
        self.assertEqual(sec.data, buf)

    def test_030(self):
        "Section - checking debug-printing"
        buf = struct.pack("BBBBBBBB", 1, 0, 5, 0, 0, 0, 0, 0)
        sec = dvbsi.Section(buf)
        string = sec.__str__()
        self.assertNotEqual(len(string), 0)


class SectionExtTest(unittest.TestCase):
    def test_010(self):
        "SectionExt - checking too short SectionExt"
        buf = struct.pack("BBBBBBB", 1, 0x80, 5, 0, 0, 0, 0)
        sec = dvbsi.SectionExt(buf)
        self.assertEqual(sec.table_id, -1)

    def test_015(self):
        "SectionExt - checking syntax_indicator"
        buf = struct.pack("BBBBBBBBB", 2, 0x00, 6, 0, 0, 0, 0, 0, 0)
        sec = dvbsi.SectionExt(buf)
        self.assertEqual(sec.table_id, -1)

        buf = struct.pack("BBBBBBBBB", 2, 0x80, 6, 0, 0, 0, 0, 0, 0)
        sec = dvbsi.SectionExt(buf)
        self.assertNotEqual(sec.table_id, -1)

    def test_020(self):
        "SectionExt - extracting table id and length of SectionExt"
        buf = struct.pack("BBBBBBBBB", 2, 0x80, 6, 0, 0, 0, 0, 0, 0)
        sec = dvbsi.SectionExt(buf)
        self.assertEqual(sec.table_id, 2)
        self.assertEqual(sec.length, 6)

    def test_030(self):
        "SectionExt - extracting SectionExt fields"
        buf0 = struct.pack("BBBBBBBB", 2, 0, 5, 0xf1, 0x5a, 0x11, 0x5, 0x88)
        sec = dvbsi.SectionExt(buf0)
        self.assertEqual(sec.table_id, -1)

        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x5, 0x88)
        sec = dvbsi.SectionExt(buf)
        self.assertEqual(sec.table_id_ext, 0xf15a)
        self.assertEqual(sec.version_number, 0x08)
        self.assertEqual(sec.current_next_indicator, 0x1)
        self.assertEqual(sec.section_number, 0x5)
        self.assertEqual(sec.last_section_number, 0x88)
        self.assertEqual(sec.crc_32, 0x5a110588)    # crc_32 takes last 4 bytes.

    def test_040(self):
        "SectionExt - checking debug-printing"
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x5, 0x88)
        sec = dvbsi.SectionExt(buf)
        string = sec.__str__()
        self.assertNotEqual(len(string), 0)

    def test_050(self):
        "SectionExt - invalid section_number"
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x5, 0x4)
        sec = dvbsi.SectionExt(buf)
        self.assertEqual(sec.table_id, -1)

class PsiStateTest(unittest.TestCase):
    def test_010(self):
        "PsiState - single number of section"
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x0d, 0x0, 0x0)
        sec6_0 = dvbsi.SectionExt(buf)
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x0f, 0x0, 0x0)
        sec7_0 = dvbsi.SectionExt(buf)

        psi = dvbsi.PsiState()
        self.assertEqual(psi.complete(), False)

        self.assertEqual(psi.useful(sec6_0), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec6_0), False)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec7_0), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec7_0), False)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec6_0), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec6_0), False)
        self.assertEqual(psi.complete(), True)

    def test_020(self):
        "PsiState - multiple number of section"
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x0, 0x1)
        sec8_0 = dvbsi.SectionExt(buf)
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x1, 0x1)
        sec8_1 = dvbsi.SectionExt(buf)
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x0, 0x1)
        sec9_0 = dvbsi.SectionExt(buf)
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x1, 0x1)
        sec9_1 = dvbsi.SectionExt(buf)

        psi = dvbsi.PsiState()
        self.assertEqual(psi.complete(), False)

        self.assertEqual(psi.useful(sec8_1), False)
        self.assertEqual(psi.complete(), False)
        self.assertEqual(psi.useful(sec8_0), True)
        self.assertEqual(psi.complete(), False)
        self.assertEqual(psi.useful(sec8_1), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec8_0), False)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec8_1), False)
        self.assertEqual(psi.complete(), True)

        self.assertEqual(psi.useful(sec9_1), False)
        self.assertEqual(psi.complete(), False)
        self.assertEqual(psi.useful(sec9_0), True)
        self.assertEqual(psi.complete(), False)
        self.assertEqual(psi.useful(sec9_1), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec9_0), False)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec9_1), False)
        self.assertEqual(psi.complete(), True)

        self.assertEqual(psi.useful(sec8_0), True)
        self.assertEqual(psi.complete(), False)
        self.assertEqual(psi.useful(sec8_1), True)
        self.assertEqual(psi.complete(), True)
        self.assertEqual(psi.useful(sec8_0), False)
        self.assertEqual(psi.complete(), True)


if __name__ == "__main__":
    unittest.main(argv=('', '-v'))
