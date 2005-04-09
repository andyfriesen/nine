import unittest

from ast.parenthexpression import ParenthExpression
from ast.multiplyexpression import MultiplyExpression
from ast.literalexpression import StringLiteral
from ast import vartypes

from nine import token
from nine.tokenlist import TokenList
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic
from nine import error

from tests import util

class ParenthTest(unittest.TestCase):
    def testNew(self):
        pe = ParenthExpression(None)
        self.failUnless(pe is not None)

    def testGoodParse(self):
        tokens = lex('(3*3)')
        pe = ParenthExpression.parse(tokens)
        self.failUnless(isinstance(pe, ParenthExpression), repr(pe))

    def testChild(self):
        pe = ParenthExpression.parse(lex('(3*3)'))
        self.failUnless(isinstance(pe.childExpression, MultiplyExpression), repr(pe))
        self.failUnless(pe.getType() == vartypes.IntType, repr(pe))

    def testBadParse(self):
        tokens = lex('()')

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: ParenthExpression.parse(tokens)
        )

    def testCodeGen(self):
        program = util.source('''
        var x = 9
        var y = 3
        var z = 27

        print 'Expect 9'
        print x
        print 'Expect 9'
        print 3 + y * (y-1)
        print 'Expect 3'
        print (x + 3) / (y + 1)
        ''')

        util.runProgram('parenth_test', program)



if __name__ == '__main__':
    unittest.main()
