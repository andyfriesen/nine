
import unittest

from ast.returnstatement import ReturnStatement

from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic
from nine import token
from nine import error

from tests import util

class ReturnTest(unittest.TestCase):
    def testParse(self):
        tokens = lex(util.source('''
            return
            return 42 * 3 - 9
        '''))

        r1 = ReturnStatement.parse(tokens)
        self.failUnless(isinstance(r1, ReturnStatement), r1)
        self.assertEqual(r1.value, None)

        tokens.expect(token.END_OF_STATEMENT)

        r2 = ReturnStatement.parse(tokens)
        self.failUnless(isinstance(r2, ReturnStatement), r2)
        self.assertNotEqual(r2.value, None)

        tokens.expect(token.END_OF_STATEMENT)

    def testTypeMismatch1(self):
        program = util.source('''
            def foo(i as int) as int:
                return "This isn't an int!!"
        ''')

        ast = parse(lex(program))
        self.failUnlessRaises(
            error.TypeError,
            lambda: semantic(ast)
        )

    def testTypeMismatch2(self):
        program = util.source('''
            def foo(i as int) as void:
                return i
        ''')
        self.failUnlessRaises(
            error.TypeError,
            lambda: semantic(parse(lex(program)))
        )

    def testTypeMismatch3(self):
        program = util.source('''
            def foo(i as int) as int:
                return
        ''')

        self.failUnlessRaises(
            error.TypeError,
            lambda: semantic(parse(lex(program)))
        )

    def testCodeGen(self):
        program = util.source('''
            def foo(i as int) as int:
                return i * 3

            def bar() as void:
                print 'bar!'
                return

            print foo(3)
            bar()
        ''')

        util.runProgram('returntest', program)


if __name__ == '__main__':
    unittest.main()
