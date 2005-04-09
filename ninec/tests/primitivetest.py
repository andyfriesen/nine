
import unittest

from tests import util

class PrimitiveTest(unittest.TestCase):
    def testPrimitiveMethods(self):
        program = util.source('''
            var y = "Hello Nine!"

            print y.Length
        ''')

        util.runProgram('primitive_method_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
