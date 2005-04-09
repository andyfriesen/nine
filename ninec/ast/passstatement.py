
from nine.token import *

class PassStatement(object):
    '''A "statement" which does not actually do anything.
    '''

    def parse(tokens):
        if tokens.peek() == 'pass':
            tokens.getNext()
            return PassStatement()
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        return self

    def emitCode(self, gen):
        gen.ilGen.Emit(gen.opCodes.Nop)
