import unittest

from ast.breakstatement import BreakStatement

from nine import token
from nine.driver import Driver

from nine import error

from tests import util

class BreakTest(unittest.TestCase):
    def testParse(self):
        result = util.parseProgram(util.source('''
            while true:
                break
        '''))

        self.assertEqual(1, len(result))

        stmt = result[0]
        self.failUnless(isinstance(stmt.block.children[0], BreakStatement), stmt.block.children[0])

    def testOuterBreak(self):
        program = util.source('''
            break
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testRun(self):
        program = util.source('''
            print "You should see one 9"
            var x = 5

            while x > 0:
                print 9
                x = x - 1
                break
        ''')

        util.runProgram('break_test', program)

if __name__ == '__main__':
    unittest.main()
