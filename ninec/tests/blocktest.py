import unittest

from ast.printstatement import PrintStatement
from ast.blockstatement import BlockStatement
from ast.literalexpression import StringLiteral

from nine.token import END_OF_STATEMENT, BEGIN_BLOCK
from nine.lexer import lex

from tests import util

class BlockTest(unittest.TestCase):
    def testNewBlock(self):
        block = BlockStatement([])
        # Test passes if no exception is raised

    def testGoodParse(self):
        tokens = lex(util.source('''
            print 'blah'
                print '1!'
                print '2!'
            un_indent_ahoy_and_something_fish'''
        ))

        preamble = PrintStatement.parse(tokens)
        assert isinstance(preamble, PrintStatement)
        assert tokens.getNext() is END_OF_STATEMENT

        assert tokens.peek() is BEGIN_BLOCK, tokens.peek()

        block = BlockStatement.parse(tokens)
        assert block is not None, tokens

    def testSemantic(self):
        program = util.source('''
            while 0:
                print '1!'
                print '2!'
            '''
        )

        from nine.lexer import lex
        from nine.parser import parse
        from nine.semantic import semantic
        from nine.scope import Scope
        tokens = lex(program)
        ast = parse(tokens)
        block = ast[0].block
        assert isinstance(block, BlockStatement)

        scope = Scope(parent=None)
        result = block.semantic(scope)
        assert isinstance(result, BlockStatement)

if __name__ == '__main__':
    unittest.main()
