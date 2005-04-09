import unittest
from nine import token
from nine.driver import Driver
from nine.lexer import lex
import os

from nine.parser import parse
from nine.semantic import semantic
from nine.error import SyntaxError, TypeError

from ast.blockstatement import BlockStatement
from ast.whilestatement import WhileStatement

from tests import util

class WhileTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def testGoodParse(self):
        s = lex("while 1:\n    print 9\n")
        result = WhileStatement.parse(s)
        self.failUnless(isinstance(result, WhileStatement))

    def testBadParse(self):
        s = lex('while 0\n')
        self.assertRaises(SyntaxError, lambda: WhileStatement.parse(s))

    def testCompileString(self):
        program = util.source('''
            while false:
                print 9

            var x = 5

            while x > 0:
                print 3+3+3
                x = x - 1
        ''')

        util.runProgram('while_test', program)

    def testGoodSemantic(self):
        result = semantic(parse(lex("while true:\n    print 9\n")))
        self.failUnlessEqual(len(result), 1)

        stmt = result[0]
        self.failUnless(isinstance(stmt, WhileStatement), stmt)

    def testBadSemantic(self):
        self.failUnlessRaises(TypeError,
            lambda: semantic(parse(lex("while 's':\n    print 9\n")))
        )

if __name__ == '__main__':
    unittest.main()
