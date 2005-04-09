import unittest

from ast.multiplyexpression import MultiplyExpression
from ast.literalexpression import StringLiteral

from nine import token
from nine.tokenlist import TokenList
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic
from nine import error

from tests import util

_fakepos = (0, '<unknown>')

class MultiplyTest(unittest.TestCase):
    def testNew(self):
        s = MultiplyExpression(StringLiteral(_fakepos, 'A'), StringLiteral(_fakepos, 'B'), '*')
        self.failUnless(s is not None)

    def testParseMul(self):
        tokens = lex("2 * 5")
        result = MultiplyExpression.parse(tokens)
        self.failUnless(isinstance(result, MultiplyExpression), repr(result))

    def testParseDiv(self):
        tokens = lex("9 / 3")
        result = MultiplyExpression.parse(tokens)
        self.failUnless(isinstance(result, MultiplyExpression), repr(result))

    def testMod(self):
        tokens = lex("5 % 4")
        result = MultiplyExpression.parse(tokens)
        self.failUnless(isinstance(result, MultiplyExpression), repr(result))

    def testGoodSemantic(self):
        program = 'print 5 * 42\n'
        result = semantic(parse(lex(program)))
        # if no exception is thrown, it passes

    def testBadSemantic(self):
        program = "var x = 5 * 'bork'\n"

        self.failUnlessRaises(
            error.TypeError,
            lambda: semantic(parse(lex(program)))
        )

    def testCodeGen(self):
        program = '''
var x = 9
var y = 3
var z = 27

print 'Expect 9'
print x
print 'Expect 9'
print y * y
print 'Expect 3'
print x / y
print 'Expect 9'
print z / y
print 'Expect 3'
print z / x
print 'Expect 1'
print 5 % 4
'''

        util.runProgram('multiply_test', program)

if __name__ == '__main__':
    unittest.main()
