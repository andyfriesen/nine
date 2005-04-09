
import unittest

from ast.literalexpression import LiteralExpression
from ast import vartypes

from nine.lexer import lex
from nine import error

class TypeTest(unittest.TestCase):
    def testNewType(self):
        class MockNativeType(object):
            def __init__(self):
                self.Name = 'Blah'

        t = vartypes.Type('MockType', MockNativeType())

    def testIntLiteral(self):
        e = LiteralExpression.parse(lex('42'))
        self.failUnlessEqual(e.getType(), vartypes.IntType)

    def testStringLiteral(self):
        e = LiteralExpression.parse(lex('\'blah\''))
        self.failUnlessEqual(e.getType(), vartypes.StringType)

    def testParse(self):
        from ast.identifier import Identifier

        tokens = lex('int aoeuaoeu string 42')

        results = [vartypes.Type.parse(tokens) for i in range(3)]

        assert results[0] is vartypes.IntType
        assert isinstance(results[1], Identifier)
        assert results[2] is vartypes.StringType

        self.assertRaises(
            error.SyntaxError,
            lambda: vartypes.Type.parse(tokens)
        )

    def testAncestry(self):
        from ast.namespace import Namespace
        from nine.driver import Driver

        driver = Driver()
        ns = Namespace('')
        driver._scanAssembly(ns, 'mscorlib')

        string = ns.symbols['System'].symbols['String']
        object = ns.symbols['System'].symbols['Object']

        assert not string.isDescendant(object)
        assert object.isDescendant(string), string.bases

if __name__ == '__main__':
    unittest.main()
