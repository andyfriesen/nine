from ast import vartypes

from nine import lexer
from nine import error
from nine import util

class AddExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def getType(self):
        lht = self.leftSide.getType()
        rht = self.rightSide.getType()
        if lht != rht:
            raise error.TypeError, "You cannot add values of different types"
        return lht

    def parse(tokens):
        from ast.multiplyexpression import MultiplyExpression
        pos = tokens.getPosition()
        operation = None

        expr = MultiplyExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            peek = tokens.peek()
            if peek in lexer.AddOperators:
                tokens.getNext()
                rhs = MultiplyExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()

                expr = AddExpression(expr, rhs, peek)
            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '(%r %s %r)' % (self.leftSide, self.operation, self.rightSide)

    def semantic(self, scope):
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        ltype = lhs.getType()
        rtype = rhs.getType()

        if ltype in (vartypes.IntType, vartypes.FloatType) and rtype == ltype:
            return AddExpression(lhs, rhs, self.operation)

        elif ltype == vartypes.StringType and rtype == ltype and self.operation == '+':
            return _StringConcatExpression(lhs, rhs)

        # TODO: Check for overloaded operators

        else:
            raise error.TypeError, "%s operator is not valid between %s and %s" % (self.operation, ltype, rtype)

    def emitLoad(self, gen):
        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation == '+':
            gen.ilGen.Emit(gen.opCodes.Add)
        elif self.operation == '-':
            gen.ilGen.Emit(gen.opCodes.Sub)
        else:
            assert False, 'AddExpression operation %s undefined' % self.operation

class _StringConcatExpression(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

        assert self.lhs.getType() == self.rhs.getType() == vartypes.StringType, self

    def semantic(self, scope):
        lhs = self.lhs.semantic(scope)
        rhs = self.rhs.semantic(scope)

        assert self.lhs.getType() == self.rhs.getType() == vartypes.StringType, self

        return _StringConcatExpression(lhs, rhs)

    def getType(self):
        return vartypes.StringType

    def emitLoad(self, gen):
        from CLR import System

        argTypes = util.toTypedArray(System.Type, (System.String, System.String))
        concatMethod = vartypes.StringType.builder.GetMethod("Concat", argTypes)
        assert concatMethod is not None, self

        self.lhs.emitLoad(gen)
        self.rhs.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, concatMethod)
