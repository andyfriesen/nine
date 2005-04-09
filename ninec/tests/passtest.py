import os
import unittest

from ast.passstatement import PassStatement

from nine import token
from nine.driver import Driver
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic
from nine import error

from tests import util


class PassTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def testGoodParse(self):
        s = lex("pass\n")
        result = PassStatement.parse(s)
        self.failUnless(isinstance(result, PassStatement))

    def testBadParse(self):
        s = lex('pass "x"\n')
        self.assertRaises(error.SyntaxError, lambda: parse(s))

    def testCompileString(self):
        program = util.source('''
            pass
        ''')

        util.runProgram('pass_test', program)

if __name__ == '__main__':
    unittest.main()
