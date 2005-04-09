import unittest

from ast.relationalexpression import RelationalExpression

from nine import token
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

from tests import util

class RelationalTest(unittest.TestCase):
    def testInstance(self):
        r = RelationalExpression('1','2','<')
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testLessThan(self):
        tokens = lex('1 < 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testGreaterThan(self):
        tokens = lex('1 > 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testEqualTo(self):
        tokens = lex('1 == 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testGreaterThanEqualTo(self):
        tokens = lex('1 >= 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testLessThanEqualTo(self):
        tokens = lex('1 <= 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testNotEqualTo(self):
        tokens = lex('1 != 2')
        r = RelationalExpression.parse(tokens)
        self.failUnless(isinstance(r,RelationalExpression), r)

    def testCompileString(self):
        program = util.source('''
            print 'true/false pattern'
            print 1 < 9
            print 9 < 1
            print 9 > 1
            print 1 > 9
            print 9 == 9
            print 1 == 9
            print 1 != 9
            print 9 != 9
            print 'true/true/false pattern'
            print 1 <= 9
            print 9 <= 9
            print 10 <= 9
            print 10 >= 9
            print 9 >= 9
            print 1 >= 9
        ''')

        util.runProgram('relation_test', program)

if __name__ == '__main__':
    unittest.main()
