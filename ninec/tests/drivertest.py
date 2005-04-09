
import os
import os.path
import unittest

from nine.driver import Driver

from tests import util

class DriverTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def testNewDriver(self):
        self.failUnless(self.driver is not None)

    def testCompileString(self):
        program = util.source('''
            print 'Hello, driver test!'
        ''')

        util.runProgram('driver_hello_test', program)

if __name__ == '__main__':
    unittest.main()
