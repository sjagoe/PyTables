import sys
import unittest
import os
import tempfile

from tables import *

from common import verbose, cleanup
# To delete the internal attributes automagically
unittest.TestCase.tearDown = cleanup

# Test Record class
class Record(IsDescription):
    var1 = StringCol(length=4)    # 4-character String
    var2 = IntCol()               # integer
    var3 = IntCol(itemsize=2)     # short integer
    var4 = FloatCol()             # double (double-precision)
    var5 = FloatCol(itemsize=4)   # float  (single-precision)


class RangeTestCase(unittest.TestCase):
    file  = "test.h5"
    title = "This is the table title"
    expectedrows = 100
    maxshort = 2 ** 15
    maxint   = 2147483648   # (2 ** 31)
    compress = 0

    def setUp(self):
        # Create an instance of HDF5 Table
        self.fileh = openFile(self.file, mode = "w")
        self.rootgroup = self.fileh.root

        # Create a table
        self.table = self.fileh.createTable(self.rootgroup, 'table',
                                            Record, self.title)

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test00_range(self):
        """Testing the range check"""
        rec = self.table.row
        # Save a record
        i = self.maxshort
        rec['var1'] = '%04d' % (i)
        rec['var2'] = i
        rec['var3'] = i
        rec['var4'] = float(i)
        rec['var5'] = float(i)
        try:
            rec.append()
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
            pass
        else:
            if verbose:
                print "\nNow, the range overflow no longer issues a ValueError"

    def test01_type(self):
        """Testing the type check"""
        rec = self.table.row
        # Save a record
        i = self.maxshort
        rec['var1'] = '%04d' % (i)
        rec['var2'] = i
        rec['var3'] = i % self.maxshort
        rec['var5'] = float(i)
        try:
            rec['var4'] = "124"
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next TypeError was catched!"
                print value
            pass
        else:
            print rec
            self.fail("expected a TypeError")

#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()

    for i in range(1):
        theSuite.addTest(unittest.makeSuite(RangeTestCase))

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )