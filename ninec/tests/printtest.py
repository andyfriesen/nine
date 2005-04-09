import os
import unittest

from ast.printstatement import PrintStatement
from ast.literalexpression import StringLiteral
from nine.lexer import lex
from nine.driver import Driver
from nine.scope import Scope

from tests import util

_fakepos = (0, '<unknown>')

class PrintTest(unittest.TestCase):
    def setUp(self):
        # Empty scope to make semantic analyzer happy
        self.scope = Scope(parent=None)

    def testNewPrintStatement(self):
        s = PrintStatement('blah')

    def testGoodParse(self):
        list = lex("print 'blah'")
        result = PrintStatement.parse(list)
        self.failUnless(isinstance(result, PrintStatement))

    def testGoodParse2(self):
        list = lex("print 42")
        result = PrintStatement.parse(list)
        self.failUnless(isinstance(result, PrintStatement))

    def testFailedParse(self):
        list = lex("pint 'blah'")
        result = PrintStatement.parse(list)
        self.failUnless(result is None)

    def testBadParse(self):
        list = lex("print 'blah")

        self.failUnlessRaises(Exception, lambda: PrintStatement.parse(list))

    def testGoodSemantic(self):
        s = PrintStatement(StringLiteral(_fakepos, '"asdf"'))
        result = s.semantic(self.scope)
        self.failUnless(isinstance(result, PrintStatement), result)

    def testBadSemantic(self):
        s = PrintStatement(StringLiteral(_fakepos, '"asdf"'))
        result = s.semantic(self.scope)
        self.failUnless(isinstance(result, PrintStatement), result)

    def testCodeGen(self):
        program = util.source('''
            var x = 27
            var y = 3
            var z = 'The following line should be "9"'
            print z
            print x / y
        ''')

        util.runProgram('print_codegen_test', program)


if __name__ == '__main__':
    unittest.main()
