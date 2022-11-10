import unittest
import struct
import random
import sys

sys.path.append("..")

import dvbsi


class TableTest(unittest.TestCase):
    def test_010(self):
        "Table - single number of section"
        # section with version 6, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x0d, 0x0, 0x0)
        sec6_0 = dvbsi.SectionExt(buf)
        # section with version 7, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x0f, 0x0, 0x0)
        sec7_0 = dvbsi.SectionExt(buf)

        table = dvbsi.Table(sec6_0.table_id)

        # no section received: not is_complete
        self.assertEqual(table.is_complete(), False)

        # table should contains no section
        sections = table.get_sections()
        self.assertEqual(len(sections), 0)

        # the first packet
        test_result = table.test(sec6_0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))

        # the first packet was not saved: test_result is same with previous
        test_result = table.test(sec6_0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))

        # table should contains no section
        sections = table.get_sections()
        self.assertEqual(len(sections), 0)

        # the first packet is saved:
        # save result is ORed with COMPLETE_SUB_TABLE and COMPLETE_TABLE
        save_result = table.save(sec6_0, test_result)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        # table is is_complete
        self.assertEqual(table.is_complete(), True)

        # table should contains sec6_0
        sections = table.get_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], sec6_0)

        # sec6_0 is already saved: test_result is 0
        test_result = table.test(sec6_0)
        self.assertEqual(test_result, 0)

        self.assertEqual(table.test(sec6_0), 0)
        self.assertEqual(table.test(sec6_0), 0)
        self.assertEqual(table.save(sec6_0, 0), 0)
        self.assertEqual(table.save(sec6_0), 0)

        # table is still is_complete
        self.assertEqual(table.is_complete(), True)

        # section with new version is tested
        test_result = table.test(sec7_0)
        self.assertEqual(test_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED))

        test_result = table.test(sec7_0)
        self.assertEqual(test_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED))

        # sec7_0 was tested but not saved yet.
        # table should still have information about sec6_0.
        save_result = table.test(sec6_0)
        self.assertEqual(save_result, 0)

        # table should contains sec6_0
        sections = table.get_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], sec6_0)

        # save sec7_0
        test_result = table.save(sec7_0)
        self.assertEqual(test_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))

        # table is still is_complete
        self.assertEqual(table.is_complete(), True)

        # table should contains sec7_0
        sections = table.get_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], sec7_0)

        obsolete_sections = table.get_obsolete_sections()
        self.assertEqual(len(obsolete_sections), 1)
        self.assertEqual(obsolete_sections[0], sec6_0)

        table.reset()

        # table is reset: is_complete() returns False
        self.assertEqual(table.is_complete(), False)

        # table should contains no section
        sections = table.get_sections()
        self.assertEqual(len(sections), 0)

        # the first packet is saved:
        # save result is ORed with COMPLETE_SUB_TABLE
        save_result = table.save(sec6_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        # table is is_complete
        self.assertEqual(table.is_complete(), True)

        # table should contains sec6_0
        sections = table.get_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], sec6_0)


    def test_020(self):
        "Table - multiple number of section"
        # section with version 8, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x0, 0x1)
        sec8_0 = dvbsi.SectionExt(buf)
        # section with version 8, section_number 1
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x1, 0x1)
        sec8_1 = dvbsi.SectionExt(buf)
        # section with version 9, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x0, 0x1)
        sec9_0 = dvbsi.SectionExt(buf)
        # section with version 9, section_number 1
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x1, 0x1)
        sec9_1 = dvbsi.SectionExt(buf)

        table = dvbsi.Table(sec8_0.table_id)
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec8_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        save_result = table.save(sec8_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec8_1), (dvbsi.NEW_SECTION))
        save_result = table.save(sec8_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))

        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.test(sec8_1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.test(sec8_0), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.test(sec8_1), 0)
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.test(sec9_0), (dvbsi.VERSION_CHANGED |
                                              dvbsi.SECTION_REPLACED))
        self.assertEqual(table.is_complete(), True)

        save_result = table.save(sec9_0)
        self.assertEqual(save_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS))
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(sec9_1)
        self.assertEqual(save_result, (dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec9_0), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec9_1), 0)
        self.assertEqual(table.is_complete(), True)

        save_result = table.save(sec8_0)
        self.assertEqual(save_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS))
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec8_1)
        self.assertEqual(save_result, (dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        save_result = table.save(sec8_0)
        self.assertEqual(save_result, 0)
        self.assertEqual(table.is_complete(), True)

        table.reset()

        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec8_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec8_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        save_result = table.save(sec8_0)
        self.assertEqual(save_result, 0)
        self.assertEqual(table.is_complete(), True)

    def test_030(self):
        "Table - single and multiple number of section"
        # section with version 8, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x11, 0x0, 0x0)
        sec8_0 = dvbsi.SectionExt(buf)
        # section with version 9, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x0, 0x1)
        sec9_0 = dvbsi.SectionExt(buf)
        # section with version 9, section_number 1
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x13, 0x1, 0x1)
        sec9_1 = dvbsi.SectionExt(buf)

        table = dvbsi.Table(sec8_0.table_id)
        self.assertEqual(table.is_complete(), False)

        test_result = table.test(sec8_0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        save_result = table.save(sec8_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        test_result = table.test(sec9_0)
        self.assertEqual(test_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED))
        self.assertEqual(table.is_complete(), True)

        save_result = table.save(sec9_0)
        self.assertEqual(save_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS))
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(sec9_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec9_0), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec9_1), 0)
        self.assertEqual(table.is_complete(), True)

        save_result = table.save(sec8_0)
        self.assertEqual(save_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        obsolete_sections = table.get_obsolete_sections()
        self.assertEqual(len(obsolete_sections), 2)
        self.assertEqual(obsolete_sections[0], sec9_1)
        self.assertEqual(obsolete_sections[1], sec9_0)

        self.assertEqual(table.save(sec8_0), 0)
        self.assertEqual(table.is_complete(), True)


    def test_040(self):
        "Table - different CRC"
        # section with version 8, section_number 0, CRC 0xc1c2c3c4
        buf = struct.pack("BBBBBBBBBBBB",
                2, 0x80, 9, 0xf1, 0x5a, 0x11, 0x0, 0x1, 0xc1, 0xc2, 0xc3, 0xc4)
        sec8_0_0 = dvbsi.SectionExt(buf)
        # section with version 8, section_number 1, CRC 0xc1c2c3c5
        buf = struct.pack("BBBBBBBBBBBB",
                2, 0x80, 9, 0xf1, 0x5a, 0x11, 0x1, 0x1, 0xc1, 0xc2, 0xc3, 0xc5)
        sec8_1_0 = dvbsi.SectionExt(buf)
        # section with version 8, section_number 0, CRC 0xc1c2c3c6
        buf = struct.pack("BBBBBBBBBBBB",
                2, 0x80, 9, 0xf1, 0x5a, 0x11, 0x0, 0x1, 0xc1, 0xc2, 0xc3, 0xc6)
        sec8_0_1 = dvbsi.SectionExt(buf)
        # section with version 8, section_number 1, CRC 0xc1c2c3c7
        buf = struct.pack("BBBBBBBBBBBB",
                2, 0x80, 9, 0xf1, 0x5a, 0x11, 0x1, 0x1, 0xc1, 0xc2, 0xc3, 0xc7)
        sec8_1_1 = dvbsi.SectionExt(buf)

        table = dvbsi.Table(sec8_0_0.table_id)
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(sec8_0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_VERSION))
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec8_1_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec8_0_0), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec8_1_0), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec8_0_0), 0)
        self.assertEqual(table.is_complete(), True)

        test_result = table.test(sec8_0_1)
        self.assertEqual(test_result, (dvbsi.SECTION_REPLACED))
        save_result = table.save(sec8_0_1)
        self.assertEqual(save_result, (dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        test_result = table.test(sec8_1_1)
        self.assertEqual(test_result, (dvbsi.SECTION_REPLACED))
        save_result = table.save(sec8_1_1)
        self.assertEqual(save_result, (dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.save(sec8_0_1), 0)
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.save(sec8_1_1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec8_1_1), 0)
        self.assertEqual(table.is_complete(), True)

    def test_050(self):
        "Table - different table_id"
        # section with table_id 1, section_number 0
        buf = struct.pack("BBBBBBBB", 1, 0x80, 5, 0xf1, 0x5a, 0x0d, 0x0, 0x0)
        sec1 = dvbsi.SectionExt(buf)
        # section with table_id 2, section_number 0
        buf = struct.pack("BBBBBBBB", 2, 0x80, 5, 0xf1, 0x5a, 0x0d, 0x0, 0x0)
        sec2 = dvbsi.SectionExt(buf)

        table = dvbsi.Table(sec1.table_id)
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(sec1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)
        save_result = table.save(sec2)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), True)
        save_result = table.save(sec2)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)

        table.reset()

        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec2)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)


class TableSdtTest(unittest.TestCase):
    def test_010(self):
        """TableSdt - 2 sub-tables"""
        # section with table_id_ext 0xf15a and original_network_id 0x1234
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.SdtSection(buf)

        table = dvbsi.TableSdt(sec0.table_id)
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        table.reset()
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

    def test_020(self):
        """TableSdt - 2 sub-tables; pre-determined sub_table"""
        # section with table_id_ext 0xf15a and original_network_id 0x1234
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.SdtSection(buf)

        table = dvbsi.TableSdt(sec0.table_id)
        self.assertEqual(table.is_complete(), False)

        key0 = table.get_key(sec0)
        table.new_sub_table(key0)

        key1 = table.get_key(sec1)
        table.new_sub_table(key1)

        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        table.reset()
        self.assertEqual(table.is_complete(), False)

        key0 = table.get_key(sec0)
        table.new_sub_table(key0)

        key1 = table.get_key(sec1)
        table.new_sub_table(key1)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SUB_TABLE))

        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

    def test_030(self):
        """TableSdt - 2 sub-tables, multiple sections"""
        # section with table_id_ext 0xf15a and original_network_id 0x1234
        # section_number 0
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0_0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15a and original_network_id 0x1234
        # section_number 1
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x01, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0_1 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        # section_number 0
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x00, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1_0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        # section_number 1
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x01, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1_1 = dvbsi.SdtSection(buf)

        table = dvbsi.TableSdt(sec0_0.table_id)
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec0_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE |
                                              dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.test(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec1_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE |
                                              dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        table.reset()
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION |
                                              dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec0_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec1_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE |
                                              dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

    def test_040(self):
        "TableSdt - 2 sub-tables, multiple sections, pre-determined sub_table"

        # section with table_id_ext 0xf15a and original_network_id 0x1234
        # section_number 0
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0_0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15a and original_network_id 0x1234
        # section_number 1
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x01, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec0_1 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        # section_number 0
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x00, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1_0 = dvbsi.SdtSection(buf)

        # section with table_id_ext 0xf15b and original_network_id 0x1234
        # section_number 1
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5b, 0x11, 0x01, 0x01,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1_1 = dvbsi.SdtSection(buf)

        table = dvbsi.TableSdt(sec0_0.table_id)
        self.assertEqual(table.is_complete(), False)

        key0 = table.get_key(sec0_0)
        table.new_sub_table(key0)

        key1 = table.get_key(sec1_0)
        table.new_sub_table(key1)

        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec0_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec1_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE |
                                              dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        table.reset()
        self.assertEqual(table.is_complete(), False)

        key0 = table.get_key(sec0_0)
        table.new_sub_table(key0)

        key1 = table.get_key(sec1_0)
        table.new_sub_table(key1)

        self.assertEqual(table.test(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec0_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1_0), (dvbsi.NEW_SECTION |
                                              dvbsi.NEW_VERSION))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec0_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec1_1), (dvbsi.NEW_SECTION))
        self.assertEqual(table.save(sec1_1), (dvbsi.NEW_SECTION |
                                              dvbsi.COMPLETE_SUB_TABLE |
                                              dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

    def test_050(self):
        "TableSdt - different table_id"
        # section with table_id 0x42
        buf = struct.pack("16B",
                0x42, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.SdtSection(buf)

        # section with table_id 0x46
        buf = struct.pack("16B",
                0x46, 0x80, 0x0d, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.SdtSection(buf)


        table = dvbsi.Table(sec1.table_id)
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec2), dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec2), dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)

        table.reset()

        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec2), dvbsi.NOT_MONITORING_TABLE)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)


class TableEitTest(unittest.TestCase):
    def test_010(self):
        """TableEit - 1 segment, not sparse"""
        # section with section_number 0, last_section_number 0,
        # segment_last_section_number 0
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

        self.assertEqual(table.save(sec0), 0)
        self.assertEqual(table.is_complete(), True)

    def test_020(self):
        """TableEit - 8 segments, not sparse"""
        # section with last_section_number 7, segment_last_section_number 7
        secs = []
        for i in range(0, 8):
            # section with section_number i
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, i, 0x07,
                    0x12, 0x34, 0x56, 0x78, 0x07, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        test_result = table.test(secs[5])
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        save_result = table.save(secs[5])
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(secs[0]), dvbsi.NEW_SECTION)
        self.assertEqual(table.save(secs[0]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.save(secs[4]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[1]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[2]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[6]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[4]), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[3]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[5]), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[6]), 0)
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(secs[7])
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)

    def test_030(self):
        """TableEit - 9 segments, not sparse"""
        # section with last_section_number 7, segment_last_section_number 7
        secs = []
        for i in range(0, 8):
            # section with section_number i
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, i, 0x08,
                    0x12, 0x34, 0x56, 0x78, 0x07, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x08, 0x08,
                0x12, 0x34, 0x56, 0x78, 0x08, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec = dvbsi.EitSection(buf)
        secs.append(sec)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(secs[5])
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_SVC_TABLE))
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[0]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[4]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[8]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[1]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[2]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[6]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[3]), dvbsi.NEW_SECTION)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[4]), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[5]), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[6]), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(secs[8]), 0)
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(secs[7])
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(secs[7]), 0)
        self.assertEqual(table.is_complete(), True)

    def test_040(self):
        """TableEit - 2 segments, sparse"""
        # section with section_number 0, last_section_number 8,
        # segment_last_section_number 0
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x08,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_0 = dvbsi.EitSection(buf)
        # section with section_number 8, last_section_number 8,
        # segment_last_section_number 8
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x08, 0x08,
                0x12, 0x34, 0x56, 0x78, 0x08, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_1 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_SVC_TABLE))
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec0_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec0_1), 0)
        self.assertEqual(table.is_complete(), True)

        table.reset()

        save_result = table.save(sec0_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_SVC_TABLE))
        self.assertEqual(table.is_complete(), False)
        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec0_1), 0)
        self.assertEqual(table.is_complete(), True)

    def test_050(self):
        """TableEit - 3 segments, sparse"""
        # section with section_number 0, last_section_number 9,
        # segment_last_section_number 0
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x09,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        # section with section_number 8, last_section_number 9,
        # segment_last_section_number 9
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x08, 0x09,
                0x12, 0x34, 0x56, 0x78, 0x09, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)
        # section with section_number 9, last_section_number 9,
        # segment_last_section_number 9
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x09, 0x09,
                0x12, 0x34, 0x56, 0x78, 0x09, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE))
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION))
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec1), 0)
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec2), 0)
        self.assertEqual(table.is_complete(), True)

        table.reset()

        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE))
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION))
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec2), 0)
        self.assertEqual(table.is_complete(), False)
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.is_complete(), True)
        self.assertEqual(table.save(sec2), 0)
        self.assertEqual(table.is_complete(), True)

    def test_060(self):
        """TableEit - 64 segments, sparse, random"""
        secs = []
        for i in range(0, 32):
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, i * 8, 0xf9,
                    0x12, 0x34, 0x56, 0x78, i * 8 + 1, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, i * 8 + 1, 0xf9,
                    0x12, 0x34, 0x56, 0x78, i * 8 + 1, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)

        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        i = 0
        while (len(secs)):
            index = random.randint(0, len(secs) - 1)
            if (i == 0):
                save_result = (dvbsi.NEW_SECTION |
                               dvbsi.NEW_VERSION |
                               dvbsi.NEW_SUB_TABLE |
                               dvbsi.NEW_SVC_TABLE)
            elif (i == 63):
                save_result = (dvbsi.NEW_SECTION |
                               dvbsi.COMPLETE_SUB_TABLE |
                               dvbsi.COMPLETE_SVC_TABLE |
                               dvbsi.COMPLETE_TABLE)
            else:
                save_result = dvbsi.NEW_SECTION
            sec = secs.pop(index)
            self.assertEqual(table.save(sec), save_result)
            if (len(secs) == 0):
                self.assertEqual(table.is_complete(), True)
            else:
                self.assertEqual(table.is_complete(), False)
            i += 1

        secs = []
        for i in range(0, 32):
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x13, i * 8, 0xf9,
                    0x12, 0x34, 0x56, 0x78, i * 8 + 1, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)
            buf = struct.pack("18B",
                    0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x13, i * 8 + 1, 0xf9,
                    0x12, 0x34, 0x56, 0x78, i * 8 + 1, 0x60,
                    0xc1, 0xc2, 0xc3, 0xc4)
            sec = dvbsi.EitSection(buf)
            secs.append(sec)

        i = 0
        while (len(secs)):
            index = random.randint(0, len(secs) - 1)
            if (i == 0):
                save_result = (dvbsi.VERSION_CHANGED |
                               dvbsi.SECTION_REPLACED |
                               dvbsi.OBSOLETE_SECTIONS)
            elif (i == 63):
                save_result = (dvbsi.SECTION_REPLACED |
                               dvbsi.OBSOLETE_SECTIONS |
                               dvbsi.COMPLETE_SUB_TABLE |
                               dvbsi.COMPLETE_SVC_TABLE |
                               dvbsi.COMPLETE_TABLE)
            else:
                save_result = (dvbsi.SECTION_REPLACED |
                               dvbsi.OBSOLETE_SECTIONS)
            sec = secs.pop(index)
            self.assertEqual(table.save(sec), save_result)
            if (len(secs) == 0):
                self.assertEqual(table.is_complete(), True)
            else:
                self.assertEqual(table.is_complete(), False)
            i += 1

    def test_070(self):
        """TableEit - get_progress: 2 segments, sparse"""
        # section with section_number 0, last_section_number 8,
        # segment_last_section_number 0
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x08,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_0 = dvbsi.EitSection(buf)
        # section with section_number 8, last_section_number 8,
        # segment_last_section_number 8
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x08, 0x08,
                0x12, 0x34, 0x56, 0x78, 0x08, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_1 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()
        self.assertEqual(table.get_progress(), (0, 0))

        table.save(sec0_0)
        self.assertEqual(table.get_progress(), (1, 2))
        table.save(sec0_1)
        self.assertEqual(table.get_progress(), (2, 2))
        table.save(sec0_1)
        self.assertEqual(table.get_progress(), (2, 2))

        table.reset()
        self.assertEqual(table.get_progress(), (0, 0))

        table.save(sec0_1)
        self.assertEqual(table.get_progress(), (1, 9))
        table.save(sec0_0)
        self.assertEqual(table.get_progress(), (2, 2))
        table.save(sec0_1)
        self.assertEqual(table.get_progress(), (2, 2))

    def test_080(self):
        """TableEit - different service"""
        # service_id 0xf15a
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        key0 = (0x60, (0xf15a, 0x1234, 0x5678))
        # service_id 0xf15b
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)
        key1 = (0x60, (0xf15b, 0x1234, 0x5678))
        # service_id 0xf15c
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5c, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.EitSection(buf)
        key2 = (0x60, (0xf15c, 0x1234, 0x5678))

        table = dvbsi.TableEit()

        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))

        table.reset()

        table.new_sub_table(key0)
        table.new_sub_table(key1)
        table.new_sub_table(key2)

        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

    def test_090(self):
        """TableEit - different table_id"""
        # table_id 0x60
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        key0 = (0x60, (0xf15a, 0x1234, 0x5678))
        # table_id 0x70
        buf = struct.pack("18B",
                0x70, 0x80, 0x0f, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)
        key1 = (0x70, (0xf15b, 0x1234, 0x5678))
        # table_id 0x40
        buf = struct.pack("18B",
                0x40, 0x80, 0x0f, 0xf1, 0x5c, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.EitSection(buf)
        key2 = (0x40, (0xf15c, 0x1234, 0x5678))

        table = dvbsi.TableEit()

        test_result = table.test(sec0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_SUB_TABLE))
        save_result = table.save(sec0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        test_result = table.test(sec1)
        self.assertEqual(test_result, dvbsi.NOT_MONITORING_TABLE)
        save_result = table.save(sec1)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)
        test_result = table.test(sec2)
        self.assertEqual(test_result, dvbsi.NOT_MONITORING_TABLE)
        save_result = table.save(sec2)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)

        table.reset()

        self.assertNotEqual(table.new_sub_table(key0), None)
        self.assertEqual(table.new_sub_table(key1), None)
        self.assertEqual(table.new_sub_table(key2), None)

        test_result = table.test(sec0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION))
        save_result = table.save(sec0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        test_result = table.test(sec1)
        self.assertEqual(test_result, dvbsi.NOT_MONITORING_TABLE)
        save_result = table.save(sec1)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)
        test_result = table.test(sec2)
        self.assertEqual(test_result, dvbsi.NOT_MONITORING_TABLE)
        save_result = table.save(sec2)
        self.assertEqual(save_result, dvbsi.NOT_MONITORING_TABLE)


class TableEitSvcTest(unittest.TestCase):
    def test_010(self):
        """TableEit - different service"""
        # service_id 0xf15a
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        key0 = (0xf15a, 0x1234, 0x5678)
        # service_id 0xf15b
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)
        key1 = (0xf15b, 0x1234, 0x5678)
        # service_id 0xf15c
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5c, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.EitSection(buf)
        key2 = (0xf15c, 0x1234, 0x5678)


        table = dvbsi.TableEit()
        self.assertEqual(table.is_complete(), False)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))

        table.reset()

        self.assertNotEqual(table.new_svc_table(key0), None)
        self.assertNotEqual(table.new_svc_table(key1), None)
        self.assertNotEqual(table.new_svc_table(key2), None)

        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.save(sec2), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

    def test_020(self):
        """TableEit - last_table_id"""
        # table_id 0x60
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        # table_id 0x61
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_SVC_TABLE |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_TABLE))

        table.reset()

        key0 = table.get_svc_table_key(sec0)

        self.assertNotEqual(table.new_svc_table(key0), None)

        self.assertEqual(table.test(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE))
        self.assertEqual(table.save(sec0), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.NEW_SUB_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.test(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION))
        self.assertEqual(table.save(sec1), (dvbsi.NEW_SECTION |
                                            dvbsi.NEW_VERSION |
                                            dvbsi.COMPLETE_SVC_TABLE |
                                            dvbsi.COMPLETE_SUB_TABLE |
                                            dvbsi.COMPLETE_TABLE))

    def test_025(self):
        """TableEit - last_table_id, obsolete sections"""
        # table_id 0x60, last_table_id 0x61
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0 = dvbsi.EitSection(buf)
        # table_id 0x61, last_table_id 0x61
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1 = dvbsi.EitSection(buf)
        # table_id 0x60, last_table_id 0x60
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x13, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x60,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()

        test_result = table.test(sec0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        save_result = table.save(sec0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        test_result = table.test(sec1)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION))
        save_result = table.save(sec1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        test_result = table.test(sec2)
        self.assertEqual(test_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED))
        save_result = table.save(sec2)
        self.assertEqual(save_result, (dvbsi.VERSION_CHANGED |
                                       dvbsi.SECTION_REPLACED |
                                       dvbsi.OBSOLETE_SECTIONS |
                                       dvbsi.OBSOLETE_SUB_TABLES |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))

        obsolete_sections = table.get_obsolete_sections()
        self.assertEqual(len(obsolete_sections), 1)
        self.assertEqual(obsolete_sections[0], sec0)

        obsolete_sub_tables = table.get_obsolete_sub_tables()
        self.assertEqual(len(obsolete_sub_tables), 1)
        obsolete_sub_table = obsolete_sub_tables[0]
        obsolete_sections = obsolete_sub_table.get_sections()
        self.assertEqual(obsolete_sections[0], sec1)


    def test_030(self):
        """TableEit - different service, multiple table_id"""
        # service_id 0xf15a
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_0 = dvbsi.EitSection(buf)
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec0_1 = dvbsi.EitSection(buf)
        # service_id 0xf15b
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1_0 = dvbsi.EitSection(buf)
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5b, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1_1 = dvbsi.EitSection(buf)
        # service_id 0xf15c
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5c, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2_0 = dvbsi.EitSection(buf)
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5c, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec2_1 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()

        test_result = table.test(sec0_0)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE))
        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        test_result = table.test(sec0_1)
        self.assertEqual(test_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION))
        save_result = table.save(sec0_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))

        save_result = table.save(sec1_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        save_result = table.save(sec2_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        save_result = table.save(sec1_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE))
        save_result = table.save(sec2_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))

        table.reset()

        key0 = table.get_svc_table_key(sec0_0)
        key1 = table.get_svc_table_key(sec1_0)
        key2 = table.get_svc_table_key(sec2_0)

        self.assertNotEqual(table.new_svc_table(key0), None)
        self.assertNotEqual(table.new_svc_table(key1), None)
        self.assertNotEqual(table.new_svc_table(key2), None)

        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        save_result = table.save(sec0_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE))

        save_result = table.save(sec1_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        save_result = table.save(sec2_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        save_result = table.save(sec1_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE))
        save_result = table.save(sec2_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))

    def test_040(self):
        """TableEit - equivalent table_id"""
        # table_id 0x60
        buf = struct.pack("18B",
                0x60, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0x00)
        sec0_0 = dvbsi.EitSection(buf)
        # table_id 0x61
        buf = struct.pack("18B",
                0x61, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x61,
                0xc1, 0xc2, 0xc3, 0x00)
        sec0_1 = dvbsi.EitSection(buf)

        # table_id 0x50
        buf = struct.pack("18B",
                0x50, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x51,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1_0 = dvbsi.EitSection(buf)
        # table_id 0x51
        buf = struct.pack("18B",
                0x51, 0x80, 0x0f, 0xf1, 0x5a, 0x11, 0x00, 0x00,
                0x12, 0x34, 0x56, 0x78, 0x00, 0x51,
                0xc1, 0xc2, 0xc3, 0xc4)
        sec1_1 = dvbsi.EitSection(buf)

        table = dvbsi.TableEit()

        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.test(sec1_0), 0)
        self.assertEqual(table.save(sec1_0), 0)
        save_result = table.save(sec0_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.test(sec1_1), 0)
        self.assertEqual(table.save(sec1_1), 0)

        table.reset()

        save_result = table.save(sec0_0)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_SVC_TABLE |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.NEW_SUB_TABLE |
                                       dvbsi.COMPLETE_SUB_TABLE))
        self.assertEqual(table.test(sec1_0), 0)
        self.assertEqual(table.save(sec1_0), 0)
        save_result = table.save(sec1_1)
        self.assertEqual(save_result, (dvbsi.NEW_SECTION |
                                       dvbsi.NEW_VERSION |
                                       dvbsi.COMPLETE_SUB_TABLE |
                                       dvbsi.COMPLETE_SVC_TABLE |
                                       dvbsi.COMPLETE_TABLE))
        self.assertEqual(table.test(sec0_1), 0)
        self.assertEqual(table.save(sec0_1), 0)


if __name__ == "__main__":
    unittest.main(argv=('', '-v'))
