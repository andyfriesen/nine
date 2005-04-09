
from nine import lexer
from nine import error

class UnaryExpression(object):

    def __init__(self, position, operator, operand):
        self.position = position
        self.operator = operator
        self.operand = operand

    def parse(tokens):
        from ast.postfixexpression import PostfixExpression

        peek = tokens.peek()
        position = peek.position
        operator = None

        if peek not in lexer.UnaryOperators:
            return PostfixExpression.parse(tokens)

        tokens.expect(peek)

        operator = peek.value
        operand = UnaryExpression.parse(tokens)

        if operand is None:
            raise error.SyntaxError, "Expected operand for unary operator '%s', got %r" % tokens.peek()

        return UnaryExpression(position, operator, operand)
    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast import literalexpression
        from ast import vartypes
        from ast.literalexpression import LiteralExpression
        from nine.token import Token

        operand = self.operand.semantic(scope)

        if self.operator == '+':
            if operand.getType() not in (vartypes.IntType, vartypes.FloatType):
                raise error.TypeError, 'Unary + is only legal for ints and floats, not %r' % (operand.getType())

            return operand

        elif self.operator == '-':
            return NegativeExpression(self.position, operand).semantic(scope)

        elif self.operator == 'not':
            return NotExpression(self.position, operand).semantic(scope)

        elif self.operator == '~':
            return BitwiseNotExpression(self.position, operand).semantic(scope)

        else:
            assert False, 'Internal error: Unrecognized unary operator %r' % self.operator

class NegativeExpression(UnaryExpression):
    def __init__(self, position, operand):
        super(NegativeExpression, self).__init__(position, '-', operand)

    def semantic(self, scope):
        from ast import literalexpression
        from ast import vartypes
        from ast.literalexpression import LiteralExpression
        from nine.token import Token
        operand = self.operand.semantic(scope)

        oType = operand.getType()
        if oType not in (vartypes.IntType, vartypes.FloatType):
            raise error.TypeError, 'Unary minus is only valid on ints and floats, not %r' % oType

        # if the operand is a constant, then fold the expression into a constant as well.
        if isinstance(operand, LiteralExpression):
            oType = operand.getType()

            newValue = '-' + str(operand.getValue())

            if oType is vartypes.IntType:
                return literalexpression.IntLiteral(self.position, newValue)
            elif oType is vartypes.FloatType:
                return literalexpression.FloatLiteral(self.position, newValue)

            assert False

        return NegativeExpression(self.position, operand)

    def getType(self):
        return self.operand.getType()

    def emitLoad(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldc_I4_0)
        self.operand.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Sub)


class NotExpression(UnaryExpression):
    def __init__(self, position, operand):
        super(NotExpression, self).__init__(position, 'not', operand)

    def semantic(self, scope):
        from ast import vartypes

        operand = self.operand.semantic(scope)
        oType = operand.getType()

        if oType is not vartypes.BooleanType:
            raise error.TypeError, 'Unary not operator is valid only for booleans, not %r' % oType

        return NotExpression(self.position, operand)

    def getType(self):
        return self.operand.getType()

    def emitLoad(self, gen):
        self.operand.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Ldc_I4_0)
        gen.ilGen.Emit(gen.opCodes.Ceq)

class BitwiseNotExpression(UnaryExpression):
    def __init__(self, position, operand):
        super(BitwiseNotExpression, self).__init__(position, '~', operand)

    def semantic(self, scope):
        from ast import vartypes

        operand = self.operand.semantic(scope)
        oType = operand.getType()

        if oType is not vartypes.IntType:
            raise error.TypeError, 'Unary bitwise not operator is valid only for integers, not %r' % oType

        return BitwiseNotExpression(self.position, operand)

    def getType(self):
        return self.operand.getType()

    def emitLoad(self, gen):
        self.operand.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Not)
