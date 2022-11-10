import unittest

def suite():
    test_suites = ('test_crc32',
                   'test_dvb_types',
                   'test_section',
                   'test_table',
                   'test_descriptor',
                  )
    return unittest.defaultTestLoader.loadTestsFromNames(test_suites)

if __name__ == "__main__":
    unittest.main(argv=('', '-v', 'suite'))
