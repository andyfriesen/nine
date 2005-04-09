
import unittest

from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

class SemanticTest(unittest.TestCase):
    def testGoodProgram(self):
        source = lex(
            "print 'Hello World!'"
        )

        ast = parse(source)

        result = semantic(ast)

'''
    def testGoodProgram(self):
        source = TokenList(lex(
                "print +"
            )
        )

        ast = parse(source)

        self.failUnlessRaises(Exception, lambda: semantic(ast))
'''#need something semantically wrong but isn't a parse error
