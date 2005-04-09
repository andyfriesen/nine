
import unittest

from tests import util

class PostfixTest(unittest.TestCase):
    def testParse(self):
        program = util.source('''
            var s = "Hello"
            var o as System.Object

            o = s as System.Object

            var p = System.Object() as System.Object
            var q = o as System.String as System.Object as System.String
        ''')

        util.semanticProgram(program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
