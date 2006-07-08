
import os
import os.path
import unittest

from ast.printstatement import PrintStatement
from ast.literalexpression import LiteralExpression, StringLiteral

from nine.codegenerator import CodeGenerator

from tests import util

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
        '''FIXME: this test no longer works if run in isolation.
        '''
        program = [
            PrintStatement(StringLiteral((0, '<fakesource>'), '\'Hello, code generator test!\''))
        ]

        name = os.path.join('bin', 'codegen_hello_test')

        self.gen.createProgram(name, program)
        result = os.system('%s >> stdout.txt' % name)
        self.failUnless(result == 0)

    def testBuildLibrary(self):
        program = util.source('''
            class LibraryClass:
                def SayHi():
                    print 'Hi!'
        ''')

        util.buildProgram('build_library_test.dll', program)

        self.assertTrue(os.path.exists('bin/build_library_test.dll'))

if __name__ == '__main__':
    unittest.main()
