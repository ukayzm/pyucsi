import unittest
import sys

sys.path.append("..")

import dvbsi


class DescriptorTest(unittest.TestCase):
    def test_010(self):
        "Descriptor - checking length"
        buf = b"aa"
        dsc = dvbsi.Descriptor(buf)
        self.assertEqual(dsc.tag, -1)
        dsc = dvbsi.Descriptor(buf, 1)
        self.assertEqual(dsc.tag, -1)
        buf = b"aaaa"
        dsc = dvbsi.Descriptor(buf, 0)
        self.assertEqual(dsc.tag, -1)
        dsc = dvbsi.Descriptor(buf, 3)
        self.assertEqual(dsc.tag, -1)
        buf = b"\x00\x01\x06\x05\x00\x00\x00\x00"
        dsc = dvbsi.Descriptor(buf, 1)
        self.assertEqual(dsc.tag, -1)

    def test_020(self):
        "Descriptor - extracting tag, len and data"
        buf = b"\x00\x01\x03\x05\x00\x00\x00\x00"
        dsc = dvbsi.Descriptor(buf, 1)
        self.assertEqual(dsc.tag, 1)
        self.assertEqual(dsc.length, 3)
        self.assertEqual(len(dsc.data), 5)
        self.assertEqual(dsc.data, buf[1:6])

    def test_030(self):
        "Descriptor - checking debug-printing"
        buf = b"\x01\x00\x05\x00\x00\x00\x00\x00"
        dsc = dvbsi.Descriptor(buf, 0)
        string = dsc.__str__()
        self.assertNotEqual(len(string), 0)

class DescriptorLoopTest(unittest.TestCase):
    def test_010(self):
        "DescriptorLoop - no data"
        descloop = dvbsi.DescriptorLoop(b"", 0, 0)
        num_dsc = 0
        for dsc in descloop:
            num_dsc += 1
        self.assertEqual(num_dsc, 0)

    def test_020(self):
        "DescriptorLoop - loop"
        buf = (b"\x00\x01\x03\x05\x00\x00\x02\x04" +
               b"\x01\x02\x03\x04\x03\x02\x05\x06")
        num_dsc = 0
        for dsc in dvbsi.DescriptorLoop(buf, 1, 15):
            num_dsc += 1
        self.assertEqual(num_dsc, 3)

    def test_030(self):
        "DescriptorLoop - exact data"
        buf = (b"\x00\x01\x03\x05\x00\x00\x02\x04" +
               b"\x01\x02\x03\x04\x03\x02\x05\x06")
        dscs = []
        for dsc in dvbsi.DescriptorLoop(buf, 1, 15):
            dscs.append(dsc)
        self.assertEqual(dscs[0].tag, 1)
        self.assertEqual(dscs[0].length, 3)
        self.assertEqual(dscs[0].data, buf[1:6])
        self.assertEqual(dscs[1].tag, 2)
        self.assertEqual(dscs[1].length, 4)
        self.assertEqual(dscs[1].data, buf[6:12])
        self.assertEqual(dscs[2].tag, 3)
        self.assertEqual(dscs[2].length, 2)
        self.assertEqual(dscs[2].data, buf[12:16])

    def test_040(self):
        "DescriptorLoop - unspecifed offset & length"
        buf = (b"\x01\x03\x05\x00\x00\x02\x04" +
               b"\x01\x02\x03\x04\x03\x02\x05\x06")
        num_dsc = 0
        for dsc in dvbsi.DescriptorLoop(buf):
            num_dsc += 1
        self.assertEqual(num_dsc, 3)


if __name__ == "__main__":
    unittest.main(argv=('', '-v'))
