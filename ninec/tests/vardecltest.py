
import unittest

from nine import error
from nine.scope import Scope
from nine.token import Token

from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

from ast.vardecl import VarDecl

from tests import util

class VarDeclTest(unittest.TestCase):
    def testNew(self):
        decl = VarDecl('test', (0, '<test>'))
        # test passes if constructor finishes

    def testGoodParse(self):
        tokens = lex('var foo')

        result = VarDecl.parse(tokens)
        self.failUnless(isinstance(result, VarDecl), result)

    def testFailParse(self):
        tokens = lex('print 4')

        result = VarDecl.parse(tokens)
        self.failUnless(result is None, result)

    def testTypeDefinition(self):
        tokens = lex('var x as int')

        VarDecl.parse(tokens)

    def testInitializer(self):
        tokens = lex('var x = 291')

        result = VarDecl.parse(tokens)
        assert isinstance(result, VarDecl), result

    def testDuplicate(self):
        program = 'var x\nvar x'

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: util.buildProgram('vardecl_duplicate_test', program)
        )

    def testBadParse(self):
        tokens = lex('var 42')

        self.failUnlessRaises(error.SyntaxError,
            lambda: VarDecl.parse(tokens)
        )

    def testSemantic(self):
        tokens = lex('var x as int')
        scope = Scope(parent=None)

        decl = VarDecl.parse(tokens)
        result = decl.semantic(scope)
        self.failUnless(isinstance(result, VarDecl), result)
        self.failUnless('x' in scope)

        # x is already defined in the scope, this should fail, as it is a duplicate
        self.failUnlessRaises(Exception,
            lambda: tokens.semantic(scope)
        )

    def testSemantic2(self):
        from nine.parser import parse
        from nine.semantic import semantic

        program = util.source('''
            var x = 42
            var y = 'Hello!'
            print x
            print y
        ''')

        result = semantic(parse(lex(program)))
        assert result is not None

        # Test passes if execution reaches this point.

    def testTypeInfer(self):
        from ast import vartypes

        program = util.source('''
            var x = 19
            var z = 'Hello!'
        ''')

        ast = parse(lex(program))
        st = semantic(ast)

        assert st[0].type is vartypes.IntType, (st[0].type, vartypes.IntType)
        assert st[1].type is vartypes.StringType, (st[1].type, vartypes.StringType)

    def testTypeMismatch(self):
        ast = parse(lex('var x as string = 42'))

        assert ast is not None

        self.failUnlessRaises(
            error.TypeError,
            lambda: semantic(ast)
        )

    def testGenerateCode(self):
        program = util.source('''
            var x as int
            var y = x
            var z = 'hooooorj'
            print z
            print x
        ''')

        util.runProgram('vardecl_test', program)

    def testLocalGlobal(self):
        program = util.source('''
            var x = 81
            var y = 9

            def divide(n as int):
                print x / n

            print 'Expect 9'
            divide(y)
        ''')

        util.runProgram('vardecl_local_global_test', program)

    def testBlockScopeGlobal(self):
        # Make sure that globals can be declared inside block statements
        program = util.source('''
            var count = 10
            while count > 0:
                count -= 1
                
                var x = count
                print x
        ''')
        util.buildProgram('vardecl_block_scope_global_test', program)

if __name__ == '__main__':
    unittest.main()
