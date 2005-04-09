
import unittest
from tests import util

class CtorTest(unittest.TestCase):
    def testCompileString(self):
        program = util.source('''
            class Foo:
                def ctor(a as string):
                    print a
                    
            var b as Foo = Foo("Constructor works!")'''
        )
        util.runProgram("ctor_test", program, [])

if __name__ == '__main__':
    unittest.main()
