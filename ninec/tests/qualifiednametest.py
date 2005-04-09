
import unittest

from ast.qualifiedname import QualifiedName

from nine.lexer import lex
from nine.parser import parse
from nine import error

class QualifiedNameTest(unittest.TestCase):
    def testParse(self):
        result = QualifiedName.parse(lex('Foo.Bar'))

        assert isinstance(result, QualifiedName), result

    def testFailParse(self):
        self.failUnlessRaises(
            error.SyntaxError,
            lambda: QualifiedName.parse(lex('42'))
        )

    def testFailParse2(self):
        self.failUnlessRaises(
            error.SyntaxError,
            lambda: QualifiedName.parse(lex('blah.39'))
        )

    def testLeftAssociativity(self):
        result = QualifiedName.parse(lex('Foo.Bar.Baz'))

        assert isinstance(result.lhs, QualifiedName)
        assert result.rhs.name == 'Baz'

if __name__ == '__main__':
    unittest.main()
