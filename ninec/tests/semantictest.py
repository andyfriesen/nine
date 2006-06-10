
import unittest

from nine.lexer import lex
from nine.parser import parse
from nine import semantic
from nine.scope import Scope

from tests import util

class SemanticTest(unittest.TestCase):
    def testGoodProgram(self):
        source = lex(
            "print 'Hello World!'"
        )

        ast = parse(source)

        result = semantic.semantic(ast)

    def testCollectNames(self):
        program = util.source('''
            class A(B):
                pass

            class B(A):
                pass
        ''')

        ast = parse(lex(program))
        globalScope = Scope()

        semantic.collectNames(ast, globalScope)

        self.assertTrue('A' in globalScope.symbols)
        self.assertTrue('B' in globalScope.symbols)

    def testNameResolution(self):
        program = util.source('''
            class A(B):
                pass

            class B(A):
                pass
        ''')

        ast = parse(lex(program))
        globalScope = Scope()

        semantic.collectNames(ast, globalScope)
        semantic.resolveNames(ast, globalScope)

if __name__ == '__main__':
    unittest.main()
