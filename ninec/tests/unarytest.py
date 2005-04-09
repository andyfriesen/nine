
import unittest

from ast.unaryexpression import UnaryExpression

from nine.lexer import lex

from tests import util

class UnaryTest(unittest.TestCase):
    def testParse(self):
        tokens = lex('-42')
        result = UnaryExpression.parse(tokens)

        assert isinstance(result, UnaryExpression), result

    def testCodeGen(self):
        program = util.source('''
            var a = -9
            var b = -3.1415926535897931
            var c = +9
            var d = -c
            var e = ~0
            var f = ~(~1)

            print a
            print b
            print c
            print d
            print e
            print f

            var t1 = true
            var f1 = false
            var f2 = not t1
            var t2 = not f2
            var t3 = not f1

            print ''
            print 'Expect True, False, False, True, True'
            print t1
            print f1
            print f2
            print t2
            print t3
        ''')

        util.runProgram('unary_codegen_test', program)

if __name__ == '__main__':
    unittest.main()
