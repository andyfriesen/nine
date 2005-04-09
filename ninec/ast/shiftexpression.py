import vartypes

from nine import lexer
from nine import error

class ShiftExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def getType(self):
        lht = self.leftSide.getType()
        rht = self.rightSide.getType()
        if lht != rht:
            raise error.TypeError, "You cannot shift values of different types"
        return lht

    def parse(tokens):
        from ast.addexpression import AddExpression
        pos = tokens.getPosition()
        operation = None

        expr = AddExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            peek = tokens.peek()
            if peek in lexer.ShiftOperators:
                tokens.getNext()
                rhs = AddExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()

                expr = ShiftExpression(expr, rhs, peek)
            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '<%s %s, %s>' % (type(self).__name__, self.leftSide, self.rightSide)

    def semantic(self, scope):
        from ast.vartypes import IntType
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        if lhs.getType() != IntType or rhs.getType() != IntType:
            raise error.TypeError, "%s operator may only be used with integers" % self.operation
        else:
            return ShiftExpression(lhs, rhs, self.operation)

    def emitLoad(self, gen):
        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation == '<<':
            gen.ilGen.Emit(gen.opCodes.Shl)
        elif self.operation == '>>':
            gen.ilGen.Emit(gen.opCodes.Shr)
        elif self.operation == '>>>':
            gen.ilGen.Emit(gen.opCodes.Shr_Un)
        else:
            assert False, 'ShiftExpression operation %s undefined' % self.operation
