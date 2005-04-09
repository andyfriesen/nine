import unittest

from ast.assignstatement import AssignStatement

from nine.lexer import lex
from nine.tokenlist import TokenList

from tests import util

class AssignTest(unittest.TestCase):
    def testNew(self):
        e = AssignStatement('a', 'b')
        self.failUnless(isinstance(e, AssignStatement), repr(e))

    def testBadParse(self):
        tokens = lex('a b')
        result = AssignStatement.parse(tokens)
        self.failUnless(result is None)

    def testGoodParse(self):
        tokens = lex('x = 2')
        result = AssignStatement.parse(tokens)
        self.failUnless(result is not None)

    def testMoreParse(self):
        tokens = lex('x /= 3')
        result = AssignStatement.parse(tokens)
        self.failUnless(result is not None)

    def testSemantic(self):
        program = util.source('''
            var x as int
            x = 5
        ''')

        from nine.lexer import lex
        from nine.parser import parse
        from nine.semantic import semantic

        tokens = lex(program)
        ast = parse(tokens)
        st = semantic(ast)

        # Two statements
        self.failUnlessEqual(len(st), 2)
        # The second of which is an assignment whose lhs is the previous statement
        self.failUnlessEqual(st[1].lhs.variable, st[0])
        # named x
        self.failUnlessEqual(st[1].lhs.variable.name, 'x')

    def testEmitCode(self):
        program = util.source('''
            var x as int
            var z = 4
            x = 5
            print 'Expect to see 9 here!'
            print x + z

            var y as int
            y = x - x
            print 'This should  be -9:'
            print y - x - z

            x = 5
            z = 20

            x <<= 2
            print x
            x >>= 2
            print x
            x = 2
            print x
            x += 2
            print x
            x -= 2
            print x
            x *= 2
            print x
            z %= x
            print z
            x /= 4
            print x
            x &= z
            print x
            z |= x
            print z
            z ^= 1
            print z
        ''')

        util.runProgram('assign_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
