import unittest
from nine import token
from nine.driver import Driver
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

from nine.error import SyntaxError, TypeError
from ast.whilestatement import WhileStatement

from tests import util

class BreakTest(unittest.TestCase):
    def testCompileString(self):
        program = util.source('''
            print "You should see one 9"
            var x = 5

            while x > 0:
                print 9
                x = x - 1
                break
        ''')

        util.runProgram('break_test', program)

    def testGoodSemantic(self):
        result = semantic(parse(lex("while true:\n    break\n")))
        self.failUnlessEqual(len(result), 1)

        stmt = result[0]
        self.failUnless(isinstance(stmt, WhileStatement), stmt)

if __name__ == '__main__':
    unittest.main()
