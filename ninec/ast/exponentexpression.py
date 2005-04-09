from ast import vartypes

from nine import lexer
from nine import error
from nine import util
from CLR import System


legalTypes = [util.getNineType(t) for t in [System.Int32, System.Single, System.Double]]

class ExponentExpression(object):
    def __init__(self, base, exp):
        self.base =base
        self.exp = exp

    def getType(self):
        ltype = self.base.getType()
        rtype = self.exp.getType()
        return legalTypes[max(legalTypes.index(ltype), legalTypes.index(rtype))]

    def parse(tokens):
        from ast.unaryexpression import UnaryExpression

        expr = UnaryExpression.parse(tokens)
        if expr is None:
            return None

        while True:
            pos = tokens.getPosition()
            if tokens.peek() == '**':
                tokens.expect('**')
                rhs = UnaryExpression.parse(tokens)
                if rhs is None:
                    raise SyntaxError, 'Expected expression, got %r' % tokens.peek()
                expr = ExponentExpression(expr, rhs)
            else:
                return expr

    parse = staticmethod(parse)

    def __repr__(self):
        return '<%s %s ** %s>' % (type(self).__name__, self.base, self.exp)

    def semantic(self, scope):
        lhs = self.base.semantic(scope)
        rhs = self.exp.semantic(scope)

        ltype = lhs.getType()
        rtype = rhs.getType()

        dbl = util.getNineType(System.Single)

        if ltype not in legalTypes or rtype not in legalTypes:
            raise error.TypeError, "exponentiation valid only between %s, not %s and %s" % (legalTypes, ltype, rtype)

        return ExponentExpression(lhs, rhs)

    def emitLoad(self, gen):

        self.base.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Conv_R8)

        self.exp.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Conv_R8)

        powerMethod = util.getNetType(System.Math).GetMethod('Pow')
        gen.ilGen.Emit(gen.opCodes.Call, powerMethod)
