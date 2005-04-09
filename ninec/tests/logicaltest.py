import unittest

from ast.logicalexpression import LogicalExpression
from ast.literalexpression import StringLiteral
from ast.expression import Expression

from nine import token
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

from tests import util

from nine import error

_fakepos = (0, '<unknown>')

class LogicalTest(unittest.TestCase):
    def testNew(self):
        le = LogicalExpression(StringLiteral(_fakepos, '1'), StringLiteral(_fakepos, '1'), 'and')
        self.failUnless(le is not None)

    def testParseAnd(self):
        le = LogicalExpression.parse(lex("1 and 1"))
        self.failUnless(isinstance(le, LogicalExpression))

    def testParseOr(self):
        le = LogicalExpression.parse(lex("1 or 1"))
        self.failUnless(isinstance(le, LogicalExpression))

    def testBadParse(self):
        tokens = lex("1 and ")
        self.failUnlessRaises(
            error.SyntaxError,
            lambda: LogicalExpression.parse(tokens)
        )

    def testTypeMismatch(self):
        program = util.source('''
            print 5 or 2
        ''')

        self.failUnlessRaises(
            error.TypeError,
            lambda: util.semanticProgram(program)
        )

    def testCodeGen(self):
        program = util.source('''
            var x = 9
            var y = 3
            var z = 27

            print 'Expect True'
            print x==y or x==y*3
            print 'Expect False'
            print x==y and x==z/3
        ''')

        util.runProgram('logical_test', program)

if __name__ == '__main__':
    unittest.main()
