import unittest

from nine import error
from tests import util

from ast.enumdecl import EnumDecl

class EnumTest(unittest.TestCase):
    def testParseDecl(self):
        program = util.source('''
            enum Enumberator:
                pass
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], EnumDecl)
        return result[0]
    
    def testParseBody(self):
        program = util.source('''
            enum Enumberator:
                x = 1
                y
                z = 2
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], EnumDecl)
        return result[0]    
    
    def testBuild(self):
        program = util.source('''
            enum Enumberator:
                x = 1
                y
                z = 3
                a
            print 'Expect one two three four'
            print Enumberator.x
            print Enumberator.y
            print Enumberator.z
            print Enumberator.a
        ''')

        util.runProgram('enumerator_test', program)


if __name__ == '__main__':
    unittest.main()