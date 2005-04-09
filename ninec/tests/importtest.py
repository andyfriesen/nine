import unittest
from tests import util

from ast.importstatement import ImportStatement

class ImportTest(unittest.TestCase):
    def testParse(self):
        program = 'import System.IO'
        ast = util.parseProgram(program)
        assert isinstance(ast[0], ImportStatement), ast

    def testBadParse(self):
        program = 'import (42*3+9)'
        def parse():
            util.parseProgram(program)
        self.assertRaises(Exception, parse)

    def testSemantic(self):
        program = 'import System.IO'
        sast = util.semanticProgram(program, ['mscorlib'])
        assert isinstance(sast[0], ImportStatement), sast

    def testEmitCode(self):
        '''Until we have our own namespace creation to test this,
        I would like to avoid messing with CLR libs
        '''

if __name__ == '__main__':
    unittest.main()
