import unittest

from nine import error

from ast.continuestatement import ContinueStatement

from tests import util

class ContinueTest(unittest.TestCase):
    def testParse(self):
        result = util.parseProgram(util.source('''
            while true:
                continue
        '''))

        self.assertEqual(1, len(result))

        stmt = result[0]
        self.failUnless(isinstance(stmt.block.children[0], ContinueStatement))

    def testOuterContinue(self):
        self.failUnlessRaises(
            error.SyntaxError,
            lambda: util.semanticProgram('continue')
        )

    def testRun(self):
        program = util.source('''
            print "There should be nothing other than this"
            var x = 5

            while x > 1:
                x=x-1
                continue
                print x
        ''')

        util.runProgram('continue_test', program)

if __name__ == '__main__':
    unittest.main()
