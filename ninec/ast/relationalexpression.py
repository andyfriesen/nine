
import vartypes
from ast.bitwiseexpression import BitwiseExpression

from nine import lexer
from nine import error
from nine.token import Token

class RelationalExpression(object):
    def __init__(self, lhs, rhs, op):
        self.leftSide = lhs
        self.rightSide = rhs
        self.operation = op

    def getType(self):
        # TEMP HACK: overloaded operators may make this untrue
        return vartypes.BooleanType

        lht = self.leftSide.getType()
        rht = self.rightSide.getType()
        if lht != rht:
            raise error.TypeError, "You cannot relate values of different types"

        return lht

    def parse(tokens):
        expr = BitwiseExpression.parse(tokens)
        if expr is None:
            return None
        #pos = tokens.getPosition()
        while True:
            op = tokens.peek()
            if op in lexer.RelationalOperators:
                tokens.getNext()
                rhs = BitwiseExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()

                expr = RelationalExpression(expr, rhs, op)

            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '<%s %s, %s>' % (type(self).__name__, self.leftSide, self.rightSide)

    def semantic(self, scope):
        lhs = self.leftSide.semantic(scope)
        rhs = self.rightSide.semantic(scope)

        if lhs.getType() != rhs.getType():
            raise error.TypeError, "%s operator is not valid between %s and %s" % (self.operation, lhs.getType(), rhs.getType())
        else:
            return RelationalExpression(lhs, rhs, self.operation)

    def emitLoad(self, gen):
        from CLR import System
        operators = (
            ('>', gen.opCodes.Cgt),
            ('<', gen.opCodes.Clt),
            #('>=', gen.opCodes.cgte),
            #('<=', gen.opCodes.clte),
            ('==', gen.opCodes.Ceq),
            #('!=', gen.opCodes.cneq),
        )
        operators = dict(operators)

        self.leftSide.emitLoad(gen)
        self.rightSide.emitLoad(gen)

        if self.operation in ('<','>','=='):
            gen.ilGen.Emit(operators[self.operation.value])

        elif self.operation == '!=':
            # Compile to "not (a == b)"
            gen.ilGen.Emit(operators['=='])
            gen.ilGen.Emit(gen.opCodes.Ldc_I4_0)
            gen.ilGen.Emit(gen.opCodes.Ceq)

        elif self.operation in ('<=','>='):
            # Compile to "not (a > b)" or "not (a < b)"

            if self.operation == '<=':
                gen.ilGen.Emit(gen.opCodes.Cgt)
            elif self.operation == '>=':
                gen.ilGen.Emit(gen.opCodes.Clt)

            gen.ilGen.Emit(gen.opCodes.Ldc_I4_0)
            gen.ilGen.Emit(gen.opCodes.Ceq)

        else:
            assert False, 'RelationalExpression operation %s undefined' % self.operation
