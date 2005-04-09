import os
import unittest

from ast.addexpression import AddExpression
from ast.literalexpression import StringLiteral
from ast.printstatement import PrintStatement

from nine import token
from nine.driver import Driver
from nine.lexer import lex

from tests import util

class PrintAddTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def testPrintAdd(self):
        s = lex("print 1 + 2")
        result = PrintStatement.parse(s)
        self.failUnless(isinstance(result, PrintStatement))

    def testCompileString(self):
        program = '''\
print 'ADD'
print 3 + 6
print 'SUB'
print 12 - 3
'''

        util.runProgram('printadd_test', program)
