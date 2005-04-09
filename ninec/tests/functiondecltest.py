
import unittest

from ast.functiondecl import FunctionDecl

from nine.lexer import lex
from nine.parser import parse
from nine.scope import Scope
from nine.token import Token
from nine import error

from tests import util

class FunctionDeclTest(unittest.TestCase):
    def testNew(self):
        decl = FunctionDecl('identifier', (0, '<test>'), 'void', [], [])

    def testGoodParse(self):
        program = util.source('''
            def foo():
                pass
        ''')

        result = FunctionDecl.parse(lex(program))
        assert isinstance(result, FunctionDecl), result

    def testParseArgs(self):
        tokens = lex(util.source('''
            def foo(x as string, y as int, z as boolean):
                print x
                print y
                print z
        '''))

        result = FunctionDecl.parse(tokens)
        assert isinstance(result, FunctionDecl), tokens.peek()

    def testBadParse(self):
        program = util.source('''
            def foo():
        ''')

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: FunctionDecl.parse(lex(program))
        )

    def testGoodSemantic(self):
        program = util.source('''
            def foo():
                var x = 2
                var y = 9
                print x + y
        ''')

        tokens = lex(program)
        decl = FunctionDecl.parse(tokens)

        assert isinstance(decl, FunctionDecl), tokens

        scope = Scope(parent=None)
        result = decl.semantic(scope)

        assert result is not None

    def testDuplicateIdentifier(self):
        program = util.source('''
            def foo():
                print 9

            var foo = 9
        ''')

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: util.buildProgram('functiondecl_duplicate_test', program)
        )

    def testDuplicateIdentifier2(self):
        program = util.source('''
            def foo():
                print 9

            def foo():
                print 81
        ''')

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: util.buildProgram('functiondecl_duplicate_test', program)
        )

    def testReturnType(self):
        program = util.source('''
            def multiply(x as int, y as int) as int:
                pass
        ''')

        util.buildProgram('functiondecl_returntype_test', program)

    def testCodeGen(self):
        program = util.source('''
            def foo(x as int, y as int):
                print x * y
        ''')

        util.buildProgram('functiondecl_codegen_test', program)

    def testModifiers1(self):
        program = util.source('''
            static override def bork():
                pass
        ''')

        util.parseProgram(program)

    def testModifiers1(self):
        program = util.source('''
            static def bork():
                pass
        ''')

        util.parseProgram(program)

    def testModifiers2(self):
        program = util.source('''
            class C:
                sealed virtual def bork():
                    pass
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testModifiers3(self):
        program = util.source('''
            sealed override def bork():
                pass
        ''')

        util.parseProgram(program)

if __name__ == '__main__':
    unittest.main()
