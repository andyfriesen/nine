import unittest

from ast.addexpression import AddExpression
from ast.literalexpression import StringLiteral

from nine import token
from nine.tokenlist import TokenList
from nine.lexer import lex

from tests import util

_fakepos = (0, '<test>')

class AddTest(unittest.TestCase):
    def testNew(self):
        s = AddExpression(StringLiteral(_fakepos, 'A'), StringLiteral(_fakepos, 'B'), '+')
        self.failUnless(s is not None)

    def testParseAdd(self):
        tokens = lex("3 + 6")
        result = AddExpression.parse(tokens)
        self.failUnless(isinstance(result, AddExpression), repr(result))

    def testParseSub(self):
        tokens = lex("12 - 3")
        result = AddExpression.parse(tokens)
        self.failUnless(isinstance(result, AddExpression), repr(result))

    def testSemantic(self):
        tokens = lex('"abcd"+3')
        expr = AddExpression.parse(tokens)

        from nine.scope import Scope
        scope = Scope(parent=None)

        from nine import error
        self.failUnlessRaises(error.TypeError,
            lambda: expr.semantic(scope)
        )

    def testStringConcat(self):
        program = util.source('''
            var x = "Hello "
            var y = "World"
            var z = "!"

            var a = x + y + z
            print a
        ''')

        util.runProgram('string_concat_test', program)

if __name__ == '__main__':
    unittest.main()
