
import unittest

from ast.expression import Expression
from ast.addexpression import AddExpression
from ast.multiplyexpression import MultiplyExpression

from nine.lexer import lex

class ExpressionTest(unittest.TestCase):
    def testAddMulExpression(self):
        ast = Expression.parse(lex('a*a+b*b'))

        assert isinstance(ast, AddExpression)
        assert isinstance(ast.leftSide, MultiplyExpression)
        assert isinstance(ast.rightSide, MultiplyExpression)

if __name__ == '__main__':
    unittest.main()
