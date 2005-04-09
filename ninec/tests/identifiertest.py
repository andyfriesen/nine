
import unittest

from ast.identifier import Identifier
from ast.vardecl import VarDecl
from ast import vartypes

from nine.lexer import lex
from nine.token import Token
from nine.scope import Scope
from nine import error

from tests import util

class IdentifierTest(unittest.TestCase):
    def testNew(self):
        expr = Identifier('testvar', (0, 'test.9'))
        # yay we win! (if no exception is thrown)

    def testGoodParse(self):
        tokens = lex('foo')

        result = Identifier.parse(tokens)
        self.failIf(result is None)

    def testFailedParse(self):
        tokens = lex('print') # print is a keyword, not an identifier

        result = Identifier.parse(tokens)
        self.failUnless(result is None)

    def testParseKeywords(self):
        from ast import vartypes
        tokens = lex('int string x y')

        result = [Identifier.parse(tokens) for i in range(4)]

        # If execution gets this far, we win.

    def testSemantic(self):
        '''Also tests variable declaration/expression things.
        The basic jist is that, once semantic testing has been done,
        an Identifier should no longer be an Identifier; it should be
        a VariableExpression.
        '''
        from ast.vardecl import VarDecl
        from ast.variableexpression import VariableExpression

        decl = VarDecl('testvar', (0, '<test>'), vartypes.IntType)

        scope = Scope(parent=None)
        scope['testvar'] = decl

        tokens = lex('testvar nonexist')
        expr1 = Identifier.parse(tokens)
        expr2 = Identifier.parse(tokens)

        result = expr1.semantic(scope)

        self.failUnlessEqual(type(result), VariableExpression)
        self.failUnlessEqual(result.variable, decl)

        self.failUnlessRaises(
            error.NameError,
            lambda: expr2.semantic(scope)
        )

if __name__ == '__main__':
    unittest.main()
