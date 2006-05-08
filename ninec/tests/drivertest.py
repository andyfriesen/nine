
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

    def testLoadAssembly(self):
        a = self.driver._loadAssembly('bin/ClassLibrary1')
        self.failUnless(a is not None, a)

        self.failUnlessRaises(
            Exception,
            lambda: self.driver._loadAssembly('does_not_exist')
        )

if __name__ == '__main__':
    unittest.main()
