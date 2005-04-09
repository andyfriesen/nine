import unittest

from ast.exponentexpression import ExponentExpression
from ast.literalexpression import StringLiteral

from nine import token
from nine.tokenlist import TokenList
from nine.lexer import lex
from tests import util

class ExponentTest(unittest.TestCase):
    def testNew(self):
        s = ExponentExpression(1, 1)
        self.failUnless(s is not None)

    def testParseExp(self):
        tokens = lex("2 ** 2")
        result = ExponentExpression.parse(tokens)
        self.failUnless(isinstance(result, ExponentExpression), repr(result))

    def testSemantic(self):
        tokens = lex('"abcd"**3')
        expr = ExponentExpression.parse(tokens)

        from nine.scope import Scope
        scope = Scope(parent=None)
        
        from nine import error
        self.failUnlessRaises(error.TypeError,
            lambda: expr.semantic(scope)
        )


    def testCodeGen(self):
        program = util.source('''
        var x = 2.0
        var y = 3.0
        var z as System.Int32
        z = 1
        
        print 'Expect 9: testing two singes returns a single'
        y = y**x
        print  y

        print 'Expect 2: testing int and single returns a single'
        y = x**z
        print  y
        ''')

        util.runProgram('exponent_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
