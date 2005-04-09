
import unittest

from ast import vartypes
from ast.identifier import Identifier
from ast.vardecl import VarDecl
from ast.variableexpression import VariableExpression

from nine.lexer import lex
from nine.token import Token
from nine.scope import Scope

from tests import util

class VariableTest(unittest.TestCase):
    def testNew(self):
        decl = VarDecl('testvar', (0, '<test>'), vartypes.IntType)
        expr = VariableExpression(Token('testvar', 'identifier'), decl)
        # yay we win! (if no exception is thrown)

    def testSemantic(self):
        # Also tests Identifier and name resolution.
        decl = VarDecl('testvar', (0, '<test>'), vartypes.IntType)

        scope = Scope(parent=None)
        scope['testvar'] = decl

        tokens = lex('testvar')
        expr = Identifier.parse(tokens)

        result = expr.semantic(scope)
        self.failUnlessEqual(type(result), VariableExpression)
        self.failUnlessEqual(result.variable, decl)

    def testEmitCode(self):
        program = util.source('''\
            var x as int
            print x
        ''')

        util.runProgram('variable_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
