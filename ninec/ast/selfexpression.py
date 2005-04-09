
from nine import error

class SelfExpression(object):
    def __init__(self, position, klass=None):
        self.position = position
        self.klass = klass # figured out in semantic phase

    def parse(tokens):
        peek = tokens.peek()
        if peek == 'self':
            tokens.expect('self')
            return SelfExpression(peek.position)
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        if scope.klass is None or scope.func.flags.static:
            raise error.SyntaxError(self.position, 'No "self" available')

        # TODO: if scope.function.isStatic or whatever

        return SelfExpression(self.position, scope.klass)

    def getType(self):
        assert self.klass is not None, self
        return self.klass

    def emitLoad(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldarg_0)
