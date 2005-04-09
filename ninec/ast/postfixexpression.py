from nine import error
class PostfixExpression(object):
    def parse(tokens):
        from ast.primitiveexpression import PrimitiveExpression
        from ast.dotexpression import DotExpression
        from ast.functioncallexpression import FunctionCallExpression
        from ast.indexexpression import IndexExpression
        from ast.castexpression import CastExpression

        position = tokens.peek().position

        lhs = PrimitiveExpression.parse(tokens)
        if lhs is None:
            return None

        while True:

            if tokens.peek() == '(':
                args = FunctionCallExpression.parseArgList(tokens)
                lhs = FunctionCallExpression(lhs.position, lhs, args)

            elif tokens.peek() == '[':
                indicies = IndexExpression.parseIndex(tokens)
                lhs = IndexExpression(lhs.position, lhs, indicies)

            elif tokens.peek() == 'as':
                type = CastExpression.parseCast(tokens)
                lhs = CastExpression(lhs.position, lhs, type)

            elif tokens.peek() == '.':
                from ast.identifier import Identifier

                tokens.expect('.')
                rhs = Identifier.parse(tokens)
                if rhs is None:
                    raise error.SyntaxError(tokens.peek().position, 'Expected identifier, got %r' % tokens.peek())

                lhs = DotExpression(lhs.position, lhs, rhs)

            else:
                return lhs

    parse = staticmethod(parse)
