
import re
from CLR import System

from ast import vartypes

from nine.token import Token

class LiteralExpression(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value
        assert not isinstance(value, Token)

    def getType(self):
        assert False, 'LiteralExpression.getType must be overridden in %s' % type(self).__name__

    def getValue(self):
        return self.value

    def parse(tokens):
        pos = tokens.getPosition()

        t = tokens.peek()

        if t == 'true' or t == 'false':
            tok = tokens.getNext()
            return BooleanLiteral(tok.position, tok.value)

        if t.type != 'literal':
            return None

        tok = tokens.getNext()
        value = tok.value
        pos = tok.position

        floatChk = re.findall('^[0-9]+\.[0-9]+$', value)
        if len(floatChk) == 1:
            return FloatLiteral(pos, value)

        if value.isdigit():
            return IntLiteral(pos, value)

        elif isinstance(value, basestring) and value[0] in "'\"" and value[0] == value[-1]:
            return StringLiteral(pos, value)

        else:
            tokens.setPosition(pos)
            return None

    parse = staticmethod(parse)

    def semantic(self, scope):
        return self
        # No semantic testing necessary

    def __repr__(self):
        return '%r' % self.getValue()

class FloatLiteral(LiteralExpression):
    def getType(self):
        return vartypes.FloatType

    def emitLoad(self, gen):
        value = System.Single(float(self.getValue()))
        gen.ilGen.Emit(gen.opCodes.Ldc_R4, value)

class IntLiteral(LiteralExpression):
    def getValue(self):
        return int(self.value)

    def getType(self):
        return vartypes.IntType

    def emitLoad(self, gen):
        value = System.Int32(self.getValue())
        gen.ilGen.Emit(gen.opCodes.Ldc_I4, value)

class StringLiteral(LiteralExpression):
    def __init__(self, position, value):
        super(StringLiteral, self).__init__(position, value)

        self.value = self.value[1:-1]

    def getValue(self):
        return self.value

    def getType(self):
        return vartypes.StringType

    def emitLoad(self, gen):
        s = System.String(self.value)
        gen.ilGen.Emit(gen.opCodes.Ldstr, s)

class BooleanLiteral(LiteralExpression):
    def __init__(self, position, value):
        super(BooleanLiteral, self).__init__(position, value)

        if value == 'true':
            self.value = True
        elif value == 'false':
            self.value = False
        else:
            assert False, 'Internal error: attempt to create a boolean literal with: %r' % token

    def getValue(self):
        return self.value

    def getType(self):
        return vartypes.BooleanType

    def emitLoad(self, gen):
        if self.value is True:
            gen.ilGen.Emit(gen.opCodes.Ldc_I4_1)
        elif self.value is False:
            gen.ilGen.Emit(gen.opCodes.Ldc_I4_0)
        else:
            assert False, "Internal error: BooleanLiteral.value somehow isn't a boolean: %r" % self.value
