
import unittest

from ast.dotexpression import DotExpression
from ast.expression import Expression
from ast.identifier import Identifier

from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic
from nine.driver import Driver

from tests import util

class DotTest(unittest.TestCase):
    def testParse(self):
        result = DotExpression.parse(lex('a.b.c.d'))

        assert isinstance(result, DotExpression), result

    def testLeftAssociativity(self):
        result = Expression.parse(lex('a.b.c.d'))

        assert isinstance(result.lhs, DotExpression), result.lhs
        assert result.rhs.name == 'd'

    def testNameResolve(self):
        from ast.vartypes import Type

        program = 'System.Configuration.Assemblies.AssemblyHash'
        sast = util.semanticProgram(program, ['mscorlib'])
        assert isinstance(sast[0].expr, Type), `expr`

if __name__ == '__main__':
    unittest.main()
