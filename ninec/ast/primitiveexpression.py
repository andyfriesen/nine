
from ast import literalexpression
from ast import selfexpression
from ast import identifier
from ast import parenthexpression
from ast import newarrayexpression

class PrimitiveExpression(object):
    def parse(tokens):
        return (
            identifier.Identifier.parse(tokens) or
            newarrayexpression.NewArrayExpression.parse(tokens) or
            literalexpression.LiteralExpression.parse(tokens) or
            selfexpression.SelfExpression.parse(tokens) or
            parenthexpression.ParenthExpression.parse(tokens) or
            None
        )
    parse = staticmethod(parse)
