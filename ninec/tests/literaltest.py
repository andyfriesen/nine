import unittest

from ast.literalexpression import LiteralExpression, IntLiteral, StringLiteral

from nine.token import Token
from nine.lexer import lex
from nine import error

class LiteralTest(unittest.TestCase):
    def testNew(self):
        s = LiteralExpression((0, 'unknown'), '"blah"')

    def testGoodStringParse(self):
        tokens = lex("'print' \"print\"")

        result = LiteralExpression.parse(tokens)
        self.failUnless(isinstance(result, StringLiteral))

        result2 = LiteralExpression.parse(tokens)
        self.failUnless(isinstance(result, StringLiteral))

    def testGoodIntParse(self):
        tokens = lex('42')
        result = LiteralExpression.parse(tokens)
        self.failUnless(isinstance(result, IntLiteral), result)

    def testBadParse(self):
        tokens = lex('pint')
        result = LiteralExpression.parse(tokens)
        self.failUnless(result is None)

    def testBooleanLiteral(self):
        tokens = lex('true false 42')

        results = [LiteralExpression.parse(tokens) for i in range(3)]

    def testFloatLiteral(self):
        pass

    def testImplicitCast(self):
        #TODO:this isn't implemented yet... if it is you will need to fix this test
        from tests import util
        prog = util.source('''
            var x as char = 'c'
        ''')
        
        self.assertRaises(error.TypeError, lambda:util.semanticProgram(prog))

    def testRandomCharTests(self):
        #TODO:when this is all implemented this test should reflect that
        from tests import util
        
        program = util.source('''
            #var z as char='N' #char
            var y = '9' #string
            var x = "nine" #also string
            var z = y[0]
            
            #print "z = 'N':"
            #print z
            print "x = 'nine' starts with 'n':"
            print x
            print x[0]
            #print "see 'n' become 'N':"
            x[0]=z
            print x
            print "see three '9's:"
            print y
            print y[0]
            print y as char
        ''')

        self.assertRaises(error.TypeError, lambda:util.runProgram('test_random_char_tests', program))

    def testEmitCode(self):
        from tests import util

        program = util.source('''
            var w as float = 9.9
            var x = 42
            var y = 9
            var z = x == y
            print 'Expect 9.9! (we needed singles)'
            print w
            print 'Expect "false" then "true"'
            print z
            print x == y == z
        ''')

        util.runProgram('literal_emitcode_test', program)

if __name__ == '__main__':
    unittest.main()
