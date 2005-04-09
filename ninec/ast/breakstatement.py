
from nine import error

class BreakStatement(object):
    def __init__(self, position):
        self.position = position

    def parse(tokens):
        token = tokens.peek()
        if token == 'break':
            tokens.getNext()
            return BreakStatement(token.position)
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        if scope.innerLoop is None:
            raise error.SyntaxError(self.position, 'Break statement not in an enclosing loop')
        return self

    def emitCode(self, gen):
        assert gen.breakLabel is not None

        gen.ilGen.Emit(gen.opCodes.Br, gen.breakLabel)
