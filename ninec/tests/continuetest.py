import unittest
from nine import token
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

from nine.error import SyntaxError, TypeError
from ast.whilestatement import WhileStatement

from tests import util

class ContinueTest(unittest.TestCase):
    def testCompileString(self):
        program = '''
print "There Should be nothing other than this"
var x = 5

while x > 1:
    x=x-1
    continue
    print x
    

'''

        util.runProgram('continue_test', program)

    def testGoodSemantic(self):
        result = semantic(parse(lex("while true:\n    continue\n")))
        self.failUnlessEqual(len(result), 1)

        stmt = result[0]
        self.failUnless(isinstance(stmt, WhileStatement), stmt)

    def testBadSemantic(self):
        '''TODO: find a bad semantic
        self.failUnlessRaises(TypeError,
            lambda: semantic(parse(lex("while 's':\n    print 9\n")))
        )'''
        pass

if __name__ == '__main__':
    unittest.main()
