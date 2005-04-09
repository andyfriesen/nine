import vartypes

from nine import error
from nine import lexer

class BitwiseExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def getType(self):
        lht = self.leftSide.getType()
        rht = self.rightSide.getType()
        if lht != rht:
            raise error.TypeError, "The bitwise expression requires values of identical types"
        return lht

    def parse(tokens):
        from ast.shiftexpression import ShiftExpression
        pos = tokens.getPosition()
        operation = None

        expr = ShiftExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            peek = tokens.peek()
            if peek in lexer.BitwiseOperators:
                tokens.getNext()
                rhs = ShiftExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()

                expr = BitwiseExpression(expr, rhs, peek)
            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '<%s %s, %s>' % (type(self).__name__, self.leftSide, self.rightSide)

    def semantic(self, scope):
        from ast.vartypes import IntType
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        if lhs.getType() != rhs.getType():
            raise error.TypeError, "%s operator may only accept arguments of same type, got %s and %s" % (self.operation, lhs.getType(), rhs.getType())
        else:
            return BitwiseExpression(lhs, rhs, self.operation)

    def emitLoad(self, gen):
        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation == '|':
            gen.ilGen.Emit(gen.opCodes.Or)
        elif self.operation == '&':
            gen.ilGen.Emit(gen.opCodes.And)
        elif self.operation == '^':
            gen.ilGen.Emit(gen.opCodes.Xor)
        else:
            assert False, 'BitWiseExpression operation %s undefined' % self.operation
