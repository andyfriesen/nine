
from nine.token import *

class BreakStatement(object):
    def parse(tokens):
        if tokens.peek() == 'break':
            tokens.getNext()
            return BreakStatement()
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        return self

    def emitCode(self, gen):
        assert gen.breakLabel is not None

        gen.ilGen.Emit(gen.opCodes.Br, gen.breakLabel)
