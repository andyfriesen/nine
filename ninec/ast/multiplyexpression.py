from ast import vartypes

from nine import lexer
from nine import error

class MultiplyExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def parse(tokens):
        from ast.exponentexpression import ExponentExpression
        pos = tokens.getPosition()
        operation = None

        expr = ExponentExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            peek = tokens.peek()
            if peek in lexer.MultiplyOperators:
                tokens.getNext()
                rhs = ExponentExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()

                expr = MultiplyExpression(expr, rhs, peek)
            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '(%r %s %r)' % (self.leftSide, self.operation, self.rightSide)

    def getType(self):
        lt = self.leftSide.getType()
        rt = self.rightSide.getType()

        assert lt == rt, 'Internal error: %r is not %r, and should not be multiplyable' % (lt, rt)

        return lt

    def semantic(self, scope):
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        lt = lhs.getType()
        rt = rhs.getType()
        if lt != rt:
            raise error.TypeError, 'Cannot multiply %s and %s' % (lt, rt)

        return MultiplyExpression(lhs, rhs, self.operation)

    def emitLoad(self, gen):
        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation == '*':
            gen.ilGen.Emit(gen.opCodes.Mul)
        elif self.operation == '/':
            gen.ilGen.Emit(gen.opCodes.Div)
        elif self.operation == '%':
            gen.ilGen.Emit(gen.opCodes.Rem)
        else:
            assert False, 'AddExpression operation %s undefined' % self.operation
