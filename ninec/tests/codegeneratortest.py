
import os
import os.path
import unittest

from ast.printstatement import PrintStatement
from ast.literalexpression import LiteralExpression, StringLiteral

from nine.codegenerator import CodeGenerator

class CodeGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.gen = CodeGenerator()

    def testBuildEmptyProgram(self):
        name = os.path.join('bin', 'codegen_empty_test')

        program = [] # it is a complicated program
        self.gen.createProgram(name, program)

        result = os.system('%s >> stdout.txt' % name)
        self.failUnless(result == 0)

    def testBuildHelloWorld(self):
        program = [
            PrintStatement(StringLiteral((0, '<fakesource>'), '\'Hello, code generator test!\''))
        ]

        name = os.path.join('bin', 'codegen_hello_test')

        self.gen.createProgram(name, program)
        result = os.system('%s >> stdout.txt' % name)
        self.failUnless(result == 0)
