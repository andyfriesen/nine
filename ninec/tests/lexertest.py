import unittest

from nine.token import *
from nine.lexer import lex
from nine import error

from tests import util

class LexerTest(unittest.TestCase):
    def testOne(self):
        string = 'Hey hey hey32415 123abc ;\nlk=34545 hasf; jh'
        actual = lex(string)
        expected = ['Hey', 'hey', 'hey32415', '123', 'abc', ';', END_OF_STATEMENT, 'lk', '=', '34545', 'hasf', ';', 'jh', END_OF_STATEMENT, END_OF_FILE]

        self.failUnlessEqual(actual, expected)

    def testLexInt(self):
        result = lex('12345 67890')
        self.failUnlessEqual(len(result), 4, result)
        self.failUnlessEqual(result[0], '12345')
        self.failUnlessEqual(result[1], '67890')

    def testLexFloat(self):
        result = lex('123.456 3.1415926535897931')
        self.failUnlessEqual(result[0], '123.456')
        self.failUnlessEqual(result[1], '3.1415926535897931')

    def testLexIdentifier(self):
        result = lex('abcdef ghijkl mno123')
        self.failUnlessEqual(len(result), 5)
        self.failUnlessEqual(result[0], 'abcdef')
        self.failUnlessEqual(result[2], 'mno123')

    def testLexKeyword(self):
        result = lex('int print abc string char if 0')
        self.failUnlessEqual(result[0].type, 'keyword')
        self.failUnlessEqual(result[1].type, 'keyword')
        self.failUnlessEqual(result[2].type, 'identifier')
        self.failUnlessEqual(result[3].type, 'keyword')
        self.failUnlessEqual(result[4].type, 'keyword')
        self.failUnlessEqual(result[5].type, 'keyword')
        self.failUnlessEqual(result[6].type, 'literal')

    def testNewLine(self):
        result = lex('1234324 kljflkjsdfk \n234543 sdfl')
        self.failUnlessEqual(len(result), 7)
        self.failUnless(result[2] is END_OF_STATEMENT)

    def testEof(self):
        result = lex('1234324 kljflkjsdfk \n234543 sdfl')
        self.failUnlessEqual(len(result), 7)
        self.failUnless(result[-1] is END_OF_FILE)

    def testDoubleQuoteString(self):
        result = lex('123123 "asdf" \'asdf\' 234234')
        self.failUnlessEqual(len(result), 6, result)
        self.failUnlessEqual(result[1], '"asdf"')

    def testEscapedQuotes(self):
        result = lex(r"""'This isn\'t an error because the apostraphe is escaped'""")
        self.failUnless(result[0].value.startswith(r"'This isn't"), repr(result[0].value))

    def testEmptyString(self):
        result = lex('\'\' ""')
        self.failUnlessEqual(len(result), 4)
        self.failUnlessEqual(result, ["''", '""', END_OF_STATEMENT, END_OF_FILE])

    def testComments(self):
        result = lex(util.source('''
            this is tokens!
            # this is a comment
            this is not
        '''))

        assert '#' not in result

    def testIndentation(self):
        result = lex(util.source('''
            0
                4

                4
                    8

            0
              2
                  6'''))

        EOS = END_OF_STATEMENT
        BB = BEGIN_BLOCK
        EB = END_BLOCK
        EOF = END_OF_FILE

        expected = [
            '0', EOS,  BB, '4',  EOS, '4', EOS,
             BB, '8', EOS,  EB,   EB, EOS, '0', EOS,
             BB, '2', EOS,  BB,  '6', EOS,  EB,  EB, EOS, EOF
        ]

        self.failUnlessEqual(len(result), len(expected))
        self.failUnlessEqual(result, expected)

    def testBadIndentation(self):
        def doIt():
            result = lex(util.source('''
                    0
                        4

                        4
                      2
                ''')
            )
        self.failUnlessRaises(Exception, doIt)

    def testLineTracking(self):
        tokens = lex(util.source('''
            Line1

            Line3
            Line4

            Line6
        '''))

        # get the "Line6" token
        line6 = [tok for tok in tokens if tok == "Line6"][0]

        self.failUnlessEqual(line6.line, 6)

    def testDigraphOperators(self):
        tokens = lex('!@>>=>>>=!==^&=')

        expected = ['!', '@', '>>=', '>>>=', '!=', '=', '^', '&=', END_OF_STATEMENT, END_OF_FILE]
        assert tokens == expected, '\n' + repr(expected) + '\n' + repr([t.value for t in tokens])

    def testBrackets(self):
        tokens = lex(util.source('''
            hello
            bar (
                there
                should
                be no end_of_line
                tokens here
            )
            blah
        '''))

        # find the 'bar' token
        index = tokens.index('bar')
        self.assertEqual(tokens[index - 1], END_OF_STATEMENT)

        index = tokens.index('(')
        self.assertEqual(tokens[index + 1], 'there')

        index = tokens.index(')')
        self.assertEqual(tokens[index + 1], END_OF_STATEMENT)

    def testMissingCloseBrace(self):
        source = util.source('''
            hey look we forgot to close this (!
            oops!
        ''')

        self.assertRaises(
            error.LexError,
            lambda: lex(source)
        )

if __name__ == '__main__':
    unittest.main()
