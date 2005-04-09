import unittest
from nine.parser import parse
from nine.lexer import lex

class ParserTest(unittest.TestCase):
    def testNewParser(self):
        program = lex(
            "print 'Hello World!'\n"
            "print 42"
        )

        ast = parse(program)

if __name__ == '__main__':
    unittest.main()
