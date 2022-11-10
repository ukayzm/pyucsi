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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#

"""Container for sections defined by DVB"""


from .dvb_section import STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL
from .dvb_section import STAG_EVENT_INFORMATION_NOWNEXT_OTHER
from .dvb_section import STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL
from .dvb_section import STAG_EVENT_INFORMATION_SCHEDULE_OTHER


# test & save result
NOT_TESTED             = -1
ERROR_ON_SAVING        = -2
NOT_MONITORING_SECTION = -3
NOT_MONITORING_SERVICE = -4
NOT_MONITORING_TABLE   = -5
ERROR_ON_RECEIVING     = -6
RECEIVING_TIMED_OUT    = -7
ERROR_ON_PARSING       = -8

NEW_SECTION            = 0x0001
SECTION_REPLACED       = 0x0002
OBSOLETE_SECTIONS      = 0x0004

NEW_SUB_TABLE          = 0x0008
NEW_VERSION            = 0x0010
VERSION_CHANGED        = 0x0020
OBSOLETE_SUB_TABLES    = 0x0040
COMPLETE_SUB_TABLE     = 0x0080

NEW_SVC_TABLE          = 0x0100
COMPLETE_SVC_TABLE     = 0x0200

COMPLETE_TABLE         = 0x0400


class SectionContainer:
    '''an interface for container to collect a number of sections.

    All classes for collecting sections are derived from this class.'''

    def reset(self):
        'resets internal state and remove all saved sections'
        pass

    def test(self, section):
        '''tests section and returns the result.

        return value:
            negative integer if an error occurred.
            0 if the section is already received.
            positive integer if the section is new or the version is changed.
            it is a flag ORed with the following:
                NEW_SECTION
                VERSION_CHANGED
                NEW_SUB_TABLE
                NEW_SVC_TABLE'''
        return NEW_SECTION

    def save(self, section, test_result=-1):
        '''saves section and returns the result.

        return value:
            negative integer if an error occurred.
            0 if the section is already received.
            positive integer if the section is new or the version is changed.
            it is a flag ORed with the following:
                NEW_SECTION
                VERSION_CHANGED
                NEW_SUB_TABLE
                NEW_SVC_TABLE
                OBSOLETE_SECTIONS
                OBSOLETE_SUB_TABLES
                COMPLETE_SUB_TABLE
                COMPLETE_SVC_TABLE
                COMPLETE_TABLE'''
        return 0

    def get_progress(self):
        'returns tuple (no. of received, no. of complete sections)'
        return (0, 0)

    def is_complete(self):
        'returns True if the collector received all sections expected'
        return False

    def get_obsolete_sections(self):
        'returns a list of sections that are obsolete or replaced'
        return []

    def get_sections(self):
        'returns a list of collected sections sorted by section_number'
        return []


class SubTable(SectionContainer):
    """Container for keeping sections of sub_table"""

    def __init__(self, table_id, table_id_ext):
        self.reset()
        self.table_id = table_id
        self.table_id_ext = table_id_ext

    def reset(self):
        """Reset a sub_table state."""
        self.sections = {}
        self.version_number = 0xff
        self.last_section_number = 0
        self.complete = False
        self.obsolete_sections = []

    def _is_monitoring_section(self, section):
        # virtual
        if (self.table_id != section.table_id):
            return False
        if (self.table_id_ext != section.table_id_ext):
            return False
        return True

    def _process_num_section_changed(self, section):
        if (section.last_section_number < self.last_section_number):
            for sn in list(self.sections.keys()):
                if (sn > section.last_section_number):
                    self.obsolete_sections.append(self.sections.pop(sn))
        self.last_section_number = section.last_section_number

    def save(self, section, test_result=-1):
        if (test_result is NOT_TESTED):
            test_result = self.test(section)

        if (test_result is NOT_MONITORING_SECTION):
            return test_result

        self.obsolete_sections = []
        num_section_changed = self.is_num_section_changed(section)
        if ((self.version_number == 0xff) or num_section_changed):
            self._process_num_section_changed(section)

        if (test_result & (NEW_SECTION | VERSION_CHANGED | SECTION_REPLACED)):
            self.version_number = section.version_number
            obsolete_section = self.sections.pop(section.section_number, None)
            if (obsolete_section is not None):
                self.obsolete_sections.append(obsolete_section)
            self.sections[section.section_number] = section
            if (self._check_complete(section)):
                self.complete = True
                test_result |= COMPLETE_SUB_TABLE
            else:
                self.complete = False

        if (len(self.obsolete_sections)):
            test_result |= OBSOLETE_SECTIONS

        return test_result

    def is_num_section_changed(self, section):
        if (self.last_section_number != section.last_section_number):
            return True
        return False

    def test(self, section):
        if (self._is_monitoring_section(section) is False):
            return NOT_MONITORING_SECTION

        test_result = 0

        if (self.version_number == 0xff):
            test_result |= NEW_VERSION
        elif (self.version_number != section.version_number):
            test_result |= VERSION_CHANGED

        if (section.section_number in self.sections):
            saved = self.sections[section.section_number]
            if (saved.crc_32 != section.crc_32 or
                saved.version_number != section.version_number):
                test_result |= SECTION_REPLACED
        else:
            test_result |= NEW_SECTION

        return test_result

    def _check_complete(self, section):
        """Check if all sections are received"""
        if (len(self.sections) is not self.last_section_number + 1):
            return False
        for section in self.sections.values():
            if (section.version_number is not self.version_number):
                return False
            if (section.last_section_number is not self.last_section_number):
                return False
        return True

    def get_progress(self):
        return len(self.sections), self.last_section_number + 1

    def is_complete(self):
        return self.complete

    def get_obsolete_sections(self):
        return self.obsolete_sections

    def get_sections(self):
        sections = []
        if (len(self.sections) == 0):
            return sections

        section_numbers = sorted(self.sections.keys())
        for section_number in section_numbers:
            sections.append(self.sections[section_number])
        return sections

    def __str__(self):
        got, to_get = self.get_progress()
        string = " (ver %2d, %d/%d) - (%02x, %04x) " % (
            self.version_number, got, to_get,
            self.table_id, self.table_id_ext)
        if (self.complete):
            string += "complete"
        else:
            string += "incomplete"
        return self.__class__.__name__ + string


class SubTableSdt(SubTable):
    """Class for keeping SDT sections"""
    def __init__(self, table_id, table_id_ext, original_network_id):
        SubTable.__init__(self, table_id, table_id_ext)
        self.original_network_id = original_network_id

    def _is_monitoring_section(self, section):
        if (self.original_network_id != section.original_network_id):
            return False
        return SubTable._is_monitoring_section(self, section)

    def __str__(self):
        got, to_get = self.get_progress()
        string = " (ver %2d, %d/%d) - (%02x, %04x:%04x)" % (
            self.version_number, got, to_get,
            self.table_id, self.original_network_id, self.table_id_ext)
        if (self.complete):
            string += "complete"
        else:
            string += "incomplete"
        return self.__class__.__name__ + string


class SubTableEit(SubTable):
    """Class for keeping EIT sections"""
    def __init__(self, table_id, table_id_ext,
                 transport_stream_id, original_network_id):
        SubTable.__init__(self, table_id, table_id_ext)
        self.original_network_id = original_network_id
        self.transport_stream_id = transport_stream_id

    def _is_monitoring_section(self, section):
        if (self.original_network_id != section.original_network_id):
            return False
        if (self.transport_stream_id != section.transport_stream_id):
            return False
        return SubTable._is_monitoring_section(self, section)

    def test(self, section):
        if (self._is_monitoring_section(section) is False):
            return NOT_MONITORING_SECTION

        test_result = 0

        if (self.version_number == 0xff):
            test_result |= NEW_VERSION
        elif (self.version_number != section.version_number):
            test_result |= VERSION_CHANGED

        if (section.section_number in self.sections):
            saved = self.sections[section.section_number]
            if (saved.version_number != section.version_number):
                test_result |= SECTION_REPLACED
        else:
            test_result |= NEW_SECTION

        return test_result

    def __str__(self):
        got, to_get = self.get_progress()
        string = " (ver %2d, %d/%d) - (%02x, %04x:%04x:%04x)" % (
            self.version_number, got, to_get,
            self.table_id, self.original_network_id,
            self.transport_stream_id, self.table_id_ext)
        if (self.complete):
            string += "complete"
        else:
            string += "incomplete"
        return self.__class__.__name__ + string

    def reset(self):
        SubTable.reset(self)
        self.segment_map = []     # contains which section
                                  # with section_number is received
        self.segment_mask = []    # contains which section
                                  # with section_number should be received
        self.num_sec_in_seg = []  # contains the count of 1's in segment_mask
                                  # to get easily the total number of sections
                                  # to receive

    def _check_complete(self, section):
        # check segment map, not section map
        seg_index = section.section_number // 8
        seg_offset = section.section_number % 8
        self.segment_map[seg_index] |= 0x01 << seg_offset
        if (self.segment_mask != self.segment_map):
            return False
        for section in self.sections.values():
            if (section.version_number is not self.version_number):
                return False
            if (section.last_section_number is not self.last_section_number):
                return False
        return True

    def get_progress(self):
        return len(self.sections), sum(self.num_sec_in_seg)

    def is_num_section_changed(self, section):
        if (self.last_section_number != section.last_section_number):
            return True

        seg_index = section.section_number // 8
        segment_last_offset = section.segment_last_section_number % 8
        segment_mask = 0xff >> (7 - segment_last_offset)
        if (len(self.segment_mask) <= seg_index):
            return True
        if (self.segment_mask[seg_index] is not segment_mask):
            return True
        return False

    def _process_num_section_changed(self, section):
        last_seg_index = section.last_section_number // 8
        if (len(self.segment_mask) < last_seg_index + 1):
            # increase the size of segment info
            diff = last_seg_index + 1 - len(self.segment_mask)
            for i in range(diff):
                self.segment_mask.append(0xff)
                self.segment_map.append(0)
                self.num_sec_in_seg.append(8)
        elif (len(self.segment_mask) > last_seg_index + 1):
            # decrease the size of segment info
            diff = len(self.segment_mask) - last_seg_index - 1
            for i in range(diff):
                self.segment_mask.pop()
                self.segment_map.pop()
                self.num_sec_in_seg.pop()
            # pop obsolete_sections.
            for sn in list(self.sections.keys()):
                if (sn > section.last_section_number):
                    self.obsolete_sections.append(self.sections.pop(sn))
        self.last_section_number = section.last_section_number

        seg_index = section.section_number // 8
        if (seg_index != last_seg_index):
            num_sec_in_seg = section.last_section_number % 8 + 1
            self.segment_mask[last_seg_index] = 0xff >> (8 - num_sec_in_seg)
            if (self.num_sec_in_seg[last_seg_index] > num_sec_in_seg):
                # number of sections in this segment decrease.
                # pop obsolete_sections.
                for sn in range(num_sec_in_seg, self.num_sec_in_seg[last_seg_index]):
                    obsolete_section = self.sections.pop(sn + last_seg_index * 8, None)
                    if (obsolete_section is not None):
                        self.obsolete_sections.append(obsolete_section)
            self.num_sec_in_seg[last_seg_index] = num_sec_in_seg

        num_sec_in_seg = section.segment_last_section_number % 8 + 1
        self.segment_mask[seg_index] = 0xff >> (8 - num_sec_in_seg)
        if (self.num_sec_in_seg[seg_index] > num_sec_in_seg):
            # number of sections in this segment decrease.
            # pop obsolete_sections.
            for sn in range(num_sec_in_seg, self.num_sec_in_seg[seg_index]):
                obsolete_section = self.sections.pop(sn + seg_index * 8, None)
                if (obsolete_section is not None):
                    self.obsolete_sections.append(obsolete_section)

        self.num_sec_in_seg[seg_index] = num_sec_in_seg


class Table(SectionContainer):
    '''a container to collect a number of SubTables.

    SubTable is a collection of sections with the same value of table_id, the
    same table_id_extension and version_number. SubTable is identified by key
    which is a tuple of table_id and table_id_extension.

    Table_id shall be specified on creating Table.
    SubTable is automatically added by useful() method if the received section
    has no relevant SubTable. Or user may manually add SubTable by calling
    new_sub_table() method.

    test(section)   checks if the section is newly received.
                    New sub_table is added if the section has no relevant
                    SubTable. This method returns True if the section is newly
                    received. If the version or CRC of the section is different
                    with the saved one, the SubTable is reset and this method
                    returns True.

    save(section)

    is_complete()   returns True if all sections are received.

    is_complete(key)

    get_progress()  returns tuple of (int1, int2).
                    int1 is the count of sections received.
                    int2 is the total count of sections need to complete table.
                    if int1 is equal to int2, the table is complete.

    get_progress(key)  returns tuple of (int1, int2).
                    int1 is the count of sections received.
                    int2 is the total count of sections need to complete table.
                    if int1 is equal to int2, the table is complete.

    get_sections()  returns the list of all sections received.

    get_sections(key)  returns the list of all sections received.

    reset()         removes all SubTables.
    '''
    def __init__(self, table_id):
        self.table_id = table_id
        self.reset()

    def reset(self):
        self.sub_tables = {}

    def new_sub_table(self, key):
        table_id, table_id_ext = key
        if (table_id != self.table_id):
            return None
        sub_table = SubTable(table_id, table_id_ext)
        self.sub_tables[key] = sub_table
        return sub_table

    def get_key(self, section):
        'makes a key to identify collector out of section'
        return (section.table_id, section.table_id_ext)

    def _is_monitoring_table(self, section):
        return (section.table_id == self.table_id)

    def test(self, section):
        if (self._is_monitoring_table(section) is False):
            return NOT_MONITORING_TABLE
        key = self.get_key(section)
        sub_table = self.get_sub_table(key)
        if (sub_table is None):
            return NEW_SUB_TABLE | NEW_SECTION | NEW_VERSION
        return sub_table.test(section)

    def save(self, section, test_result=-1):
        if (self._is_monitoring_table(section) is False):
            return NOT_MONITORING_TABLE

        if (test_result is NOT_TESTED):
            test_result = self.test(section)

        key = self.get_key(section)
        if (test_result & NEW_SUB_TABLE):
            sub_table = self.new_sub_table(key)
        else:
            sub_table = self.get_sub_table(key)
        if (sub_table is None):
            return ERROR_ON_SAVING

        save_result = sub_table.save(section, test_result)
        if (save_result & COMPLETE_SUB_TABLE):
            if (self.is_complete() is True):
                save_result |= COMPLETE_TABLE
        return save_result | test_result

    def is_complete(self):
        if (len(self.sub_tables) is 0):
            return False
        for sub_table in self.sub_tables.values():
            if (sub_table.complete is False):
                return False
        return True

    def get_progress(self):
        total_got = 0
        total_to_get = 0

        for sub_table in self.sub_tables.values():
            get, to_get = sub_table.get_progress()
            total_got += get
            total_to_get += to_get

        return total_got, total_to_get

    def get_sections(self):
        sections = []
        if (len(self.sub_tables) == 0):
            return sections

        keys = sorted(self.sub_tables.keys())
        for key in keys:
            sub_table = self.sub_tables[key]
            section_numbers = sorted(sub_table.sections.keys())
            for section_number in section_numbers:
                sections.append(sub_table.sections[section_number])
        return sections

    def get_obsolete_sections(self):
        obsolete_sections = []
        if (len(self.sub_tables) == 0):
            return obsolete_sections

        for sub_table in self.sub_tables.values():
            obsolete_sections += sub_table.obsolete_sections
        return obsolete_sections

    def get_sub_table(self, key):
        return self.sub_tables.get(key, None)


class TableSdt(Table):
    '''a container to collect Service Description Table.

    Key is a tuple of table_id, table_id_extension (transport_stream_id) and
    original_network_id.

    new_sub_table(key) adds new SubTableSdt to receive.
    '''
    def new_sub_table(self, key):
        table_id, table_id_ext, original_network_id = key
        if (table_id != self.table_id):
            return None
        sub_table = SubTableSdt(table_id, table_id_ext, original_network_id)
        self.sub_tables[key] = sub_table
        return sub_table

    def get_key(self, section):
        return (section.table_id, section.table_id_ext,
                section.original_network_id)


class TableEitPrinciple(Table):
    '''a container to collect Event Information Table.

    Key is a tuple of table_id, table_id_extension (service_id),
    transport_stream_id and original_network_id.

    Sections with table_id matching with most significant 4 bits are collected.

    new_sub_table(key) adds new SubTableEit to receive.
    '''
    def new_sub_table(self, key):
        table_id, table_id_ext, transport_stream_id, original_network_id = key
        if (table_id != self.table_id):
            return None
        sub_table = SubTableEit(table_id, table_id_ext,
                                transport_stream_id, original_network_id)
        self.sub_tables[key] = sub_table
        return sub_table

    def get_key(self, section):
        return (section.table_id, section.table_id_ext,
                section.transport_stream_id, section.original_network_id)


class SvcTable(Table):
    'a collection of SubTables within the same service'
    def __init__(self, svc_key):
        self.reset()
        self.svc_key = svc_key

    def reset(self):
        Table.reset(self)
        self.num_eit_sch_sub_table = 0
        self.obsolete_sub_tables = []

    def is_pf_table(self, table_id):
        if (table_id == STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL or
            table_id == STAG_EVENT_INFORMATION_NOWNEXT_OTHER):
            return True
        return False

    def is_eit_sch_table(self, table_id):
        if (table_id >= STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL and
            table_id <= (STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 0xf)):
            return True
        return False

    def _is_monitoring_service(self, section):
        # XXX
        return True

    def _is_monitoring_table(self, section):
        if (section.table_id >= STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL and
            section.table_id <= STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 0xf):
            return True
        return False

    def new_sub_table(self, key):
        table_id, svc_key = key
        table_id_ext, transport_stream_id, original_network_id = svc_key
        sub_table = SubTableEit(table_id, table_id_ext,
                                transport_stream_id, original_network_id)
        self.sub_tables[key] = sub_table
        return sub_table

    def get_key(self, section):
        return (section.table_id, (section.table_id_ext,
                section.transport_stream_id, section.original_network_id))

    def test(self, section):
        if (self._is_monitoring_service(section) is False):
            return NOT_MONITORING_SERVICE
        if (self._is_monitoring_table(section) is False):
            return NOT_MONITORING_TABLE
        sub_key = self.get_key(section)
        sub_table = self.get_sub_table(sub_key)
        if (sub_table is None):
            return NEW_SUB_TABLE | NEW_SECTION | NEW_VERSION

        return sub_table.test(section)

    def save(self, section, test_result=-1):
        if (self._is_monitoring_service(section) is False):
            return NOT_MONITORING_SERVICE
        if (self._is_monitoring_table(section) is False):
            return NOT_MONITORING_TABLE

        if (test_result == NOT_TESTED):
            test_result = self.test(section)

        key = self.get_key(section)
        if (test_result & NEW_SUB_TABLE):
            sub_table = self.new_sub_table(key)
        else:
            sub_table = self.get_sub_table(key)
        if (sub_table is None):
            return ERROR_ON_SAVING

        self.obsolete_sub_tables = []
        save_result = sub_table.save(section, test_result)
        if (save_result & (NEW_SECTION | VERSION_CHANGED | SECTION_REPLACED)):
            if (self.is_eit_sch_table(section.table_id)):
                num_eit_sch_sub_table = (section.last_table_id & 0xf) + 1
                if (self.num_eit_sch_sub_table > num_eit_sch_sub_table):
                    save_result |= OBSOLETE_SUB_TABLES
                    self.make_obsolete_sub_tables(num_eit_sch_sub_table)
                elif (self.num_eit_sch_sub_table < num_eit_sch_sub_table):
                    self.make_new_eit_sch_sub_tables(num_eit_sch_sub_table,
                                                     save_result)
                self.num_eit_sch_sub_table = (section.last_table_id & 0xf) + 1
        if (save_result & COMPLETE_SUB_TABLE):
            if (self.is_complete() is True):
                save_result |= COMPLETE_SVC_TABLE
        return save_result | test_result

    def make_obsolete_sub_tables(self, new_num_eit_sch_sub_table):
        for i in range(new_num_eit_sch_sub_table, self.num_eit_sch_sub_table):
            table_id = i + STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL
            key = (table_id, self.svc_key)
            sub_table = self.sub_tables.pop(key, None)
            if (sub_table is not None):
                self.obsolete_sub_tables.append(sub_table)

    def make_new_eit_sch_sub_tables(self, new_num_eit_sch_sub_table, result):
        for i in range(0, new_num_eit_sch_sub_table):
            table_id = i + STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL
            key = (table_id, self.svc_key)
            sub_table = self.get_sub_table(key)
            if (sub_table is None):
                self.new_sub_table(key)
                result |= NEW_SUB_TABLE | NEW_VERSION

    def get_obsolete_sub_tables(self):
        return self.obsolete_sub_tables


class TableEit(SectionContainer):
    def __init__(self):
        self.reset()

    def reset(self):
        self.svc_tables = {}

    def new_svc_table(self, svc_key):
        svc_table = SvcTable(svc_key)
        self.svc_tables[svc_key] = svc_table
        return svc_table

    def new_sub_table(self, key):
        table_id, svc_key = key
        table_id = self.equivalent_table_id(table_id)
        if (table_id == -1):
            return None
        if (svc_key not in self.svc_tables):
            svc_table = self.new_svc_table(svc_key)
        else:
            svc_table = self.get_svc_table(svc_key)
        if (svc_table is None):
            return ERROR_ON_SAVING
        new_key = (table_id, svc_key)
        return svc_table.new_sub_table(new_key)

    def get_key(self, section):
        return (section.table_id, self.get_svc_table_key(section))

    def get_svc_table_key(self, section):
        return (section.table_id_ext, section.transport_stream_id,
                section.original_network_id)

    def is_complete(self):
        if (len(self.svc_tables) == 0):
            return False
        for svc_table in self.svc_tables.values():
            if (svc_table.is_complete() is False):
                return False
        else:
            return True

    def equivalent_table_id(self, table_id):
        if (table_id >= STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL and
            table_id <= STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 0xf):
            return (table_id & 0xf) | STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL
        if (table_id == STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL or
            table_id == STAG_EVENT_INFORMATION_NOWNEXT_OTHER):
            return STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL
        return -1

    def test(self, section):
        table_id = self.equivalent_table_id(section.table_id)
        if (table_id == -1):
            return NOT_MONITORING_TABLE
        section.table_id = table_id
        svc_key = (section.table_id_ext, section.transport_stream_id,
                   section.original_network_id)
        if (svc_key not in self.svc_tables):
            return NEW_SVC_TABLE | NEW_SUB_TABLE | NEW_SECTION | NEW_VERSION

        svc_table = self.svc_tables[svc_key]
        return svc_table.test(section)

    def save(self, section, test_result=-1):
        table_id = self.equivalent_table_id(section.table_id)
        if (table_id == -1):
            return NOT_MONITORING_TABLE
        section.table_id = table_id
        if (test_result is NOT_TESTED):
            test_result = self.test(section)

        svc_key = (section.table_id_ext, section.transport_stream_id,
                   section.original_network_id)
        if (test_result & NEW_SVC_TABLE):
            svc_table = self.new_svc_table(svc_key)
        else:
            svc_table = self.get_svc_table(svc_key)
        if (svc_table is None):
            return ERROR_ON_SAVING

        save_result = svc_table.save(section, test_result)
        if (save_result & COMPLETE_SVC_TABLE):
            if (self.is_complete()):
                save_result |= COMPLETE_TABLE
        return test_result | save_result

    def get_svc_table(self, key):
        return self.svc_tables.get(key, None)

    def get_progress(self):
        total_got = 0
        total_to_get = 0

        for svc_table in self.svc_tables.values():
            get, to_get = svc_table.get_progress()
            total_got += get
            total_to_get += to_get

        return total_got, total_to_get

    def get_sections(self):
        sections = []
        for svc_table in self.svc_tables.values():
            sections += svc_table.get_sections()
        return sections

    def get_sub_table(self, key):
        table_id, table_id_ext, transport_stream_id, original_network_id = key

        svc_key = (table_id_ext, transport_stream_id, original_network_id)
        if (svc_key not in self.svc_tables):
            return None
        svc_table = self.svc_tables[svc_key]

        if (key not in svc_table):
            return None

        return svc_table.get(key, None)

    def get_obsolete_sections(self):
        obsolete_sections = []
        for svc_table in self.svc_tables.values():
            for sub_table in svc_table.sub_tables.values():
                obsolete_sections += sub_table.obsolete_sections
        return obsolete_sections

    def get_obsolete_sub_tables(self):
        obsolete_sub_tables = []
        for svc_table in self.svc_tables.values():
            obsolete_sub_tables += svc_table.get_obsolete_sub_tables()
        return obsolete_sub_tables
