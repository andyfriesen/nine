import unittest

from ast.ifstatement import IfStatement

from nine.lexer import lex
from nine.scope import Scope
from nine import error

from tests import util

class IfTest(unittest.TestCase):
    def setUp(self):
        pass

    def testParse(self):
        program = 'if 1<2:\n    pass\nelse:\n   pass\n'
        tokens = lex(program)
        i = IfStatement.parse(tokens)
        self.failUnless(isinstance(i, IfStatement))

    def testBadParse(self):
        program = 'if 1<2\n    pass\n'
        tokens = lex(program)
        def ifParse():
            IfStatement.parse(tokens)

        self.failUnlessRaises(error.SyntaxError, ifParse)

    def testBadParse2(self):
        program = 'if 1<2:\n    pass\nelse\n    pass\n'
        tokens = lex(program)
        def ifParse():
            IfStatement.parse(tokens)
        self.failUnlessRaises(error.SyntaxError, ifParse)

    def testBadParse3(self):
        program = 'if 1<2:\n    pass\nelif:\n   pass\nelse:\n    pass\n'
        tokens = lex(program)
        def ifParse():
            IfStatement.parse(tokens)
        self.failUnlessRaises(error.SyntaxError, ifParse)

    def testSemantic(self):
        program = 'if 1<2:\n    pass\nelif 1<2:\n   pass\nelse:\n   pass\n'
        tokens = lex(program)
        iS = IfStatement.parse(tokens)
        sIS = iS.semantic(Scope(None))
        self.failUnless(isinstance(sIS,IfStatement), tokens)

    def testBadSemeantic(self):
        program = 'if 1<2:\n    pass\nelse:\n   pass\nelif 1<2:\n   pass\n'
        tokens = lex(program)
        iS = IfStatement.parse(tokens)
        sIS = iS.semantic(Scope(None))
        self.assertRaises(Exception, iS.semantic(Scope(None)))

    def testCompileString(self):
        program = util.source('''
            print 'Expect 9:'
            var count = 0
            if 1<9:
                count = count + 1
            else:
                count = count + 99

            if 1>9:
                pass
            else:
                count = count + 3

            if 1>9:
                pass
            elif 9>1:
                count = count + 4

            if 9<1:
                pass
            elif 9<1:
                pass
            else:
                count = count + 1

            print count

            if count == 9:
                print 'Looks like it passed.  Woohoo!'
            else:
                print 'Oh no it failed!!' ''')

        util.runProgram('if_test',program)

    def testABugAndyFound(self):
        from nine.lexer import lex
        from nine.parser import parse
        from nine.semantic import semantic

        result = semantic(parse(lex(util.source('''
            if true:
                print 'True!'
            print 'This caused a spurious syntax error because there is no END_OF_STATEMENT after the dedent!'
        '''))))

        # Pass if we get here

if __name__ == '__main__':
    unittest.main()
