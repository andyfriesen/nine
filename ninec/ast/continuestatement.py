
from nine.token import *

class ContinueStatement(object):
    def parse(tokens):
        if tokens.peek() == 'continue':
            tokens.getNext()
            return ContinueStatement()
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        return self

    def emitCode(self, gen):
        assert gen.continueLabel is not None

        gen.ilGen.Emit(gen.opCodes.Br, gen.continueLabel)
