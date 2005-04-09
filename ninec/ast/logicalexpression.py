import vartypes
from ast.relationalexpression import RelationalExpression
from nine import error

class LogicalExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def parse(tokens):
        expr = RelationalExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            peek = tokens.peek()
            if peek == 'and' or peek == 'or':
                tokens.getNext()
                rhs = RelationalExpression.parse(tokens)
                if rhs is None:
                    raise error.SyntaxError, 'Expected expression, got %r' % tokens.peek()
                expr = LogicalExpression(expr, rhs, peek)
            return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '<%s %s, %s>' % (type(self).__name__, self.leftSide, self.rightSide)

    def getType(self):
        return vartypes.BooleanType

    def semantic(self, scope):
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        ltype = lhs.getType()
        rtype = rhs.getType()

        if ltype is not vartypes.BooleanType or rtype is not vartypes.BooleanType:
            raise error.TypeError, ('"%s" expression is only legal for boolean expressions, not %r and %r' %
                (self.operation, ltype, rtype)
            )

        return LogicalExpression(lhs, rhs, self.operation)

    def emitLoad(self, gen):
        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation == 'and':
            gen.ilGen.Emit(gen.opCodes.And)
        elif self.operation == 'or':
            gen.ilGen.Emit(gen.opCodes.Or)
        else:
            assert False, 'LogicalExpression operation %s undefined' % self.operation
