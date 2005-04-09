
import unittest

from nine import error

from tests import util

class CtorCallTest(unittest.TestCase):
    def testSemantic(self):
        program = util.source('''
            var x = System.Object()
        ''')

        result = util.semanticProgram(program, ['mscorlib'])

    def testOverloadMatchFail(self):
        program = util.source('''
            var x = System.String("There is no overload for System.String that recieves a string.")
        ''')

        self.assertRaises(
            error.TypeError,
            lambda: util.semanticProgram(program, ['mscorlib'])
        )

    def testCodeGen(self):
        program = util.source('''
            var x = System.Object()
        ''')

        result = util.buildProgram('ctorcall_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
