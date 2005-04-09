
import unittest

from ast.functioncallexpression import FunctionCallExpression
from ast.identifier import Identifier

from nine.token import Token
from nine.lexer import lex
from nine import error

from tests import util

class FunctionCallTest(unittest.TestCase):
    def testNew(self):
        expr = FunctionCallExpression(0, Identifier('foo', (0, 'test.9')), [])
        # yay!

    def testSemantic(self):
        from nine.parser import parse
        from nine.semantic import semantic

        tokens = lex(util.source('''
            def foo():
                print 'foo!'

            foo()
        '''))

        ast = parse(tokens)
        st = semantic(ast)

    def testCodeGen(self):
        program = util.source('''
            def foo(x as int, y as int, msg as string):
                print msg
                var result = x * y
                print result

            foo(3, 3, 'Following should be 9:')
        ''')

        util.runProgram('functioncall_test', program)

    def testTypeMismatch(self):
        program = util.source('''
            def foo(x as string):
                print x

            foo(9)
        ''')

        self.failUnlessRaises(
            error.TypeError,
            lambda: util.buildProgram('functioncall_typemismatch_test', program)
        )

    def testArgCountMismatch(self):
        program = util.source('''
            def foo(x as int, y as int):
                print x * y

            foo(3)
        ''')

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: util.buildProgram('functioncall_argcountmismatch_test', program)
        )

    def testCallMethod(self):
        program = util.source('''
            class A:
                def foo(a as int, b as int):
                    print a + b

            var a = A()
            a.foo(4, 5)
        ''')

        util.runProgram('functioncall_method_test', program)

if __name__ == '__main__':
    unittest.main()
