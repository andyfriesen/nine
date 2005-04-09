import unittest
from tests import util
from nine import error

class RaiseTest(unittest.TestCase):
    def testCompile(self):
        program = util.source('''
            try:
                raise System.StackOverflowException()
                print 'Failed to raise! @_@'
            except System.StackOverflowException:
                print "Caught an exception"
        '''
        )

        util.runProgram('raise_test', program, ['mscorlib'])

    def testraiseinstance(self):
        program = util.source('''
            class UserException(System.Exception):
                pass

            var a = UserException()

            try:
                raise a
            except UserException:
                print "raising exception instances work!"'''
        )

        util.runProgram('raise_instance_test', program, ['mscorlib'])


if __name__=='__main__':
    unittest.main()
