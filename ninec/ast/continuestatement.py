
from nine import error

class ContinueStatement(object):
    def __init__(self, position):
        self.position = position

    def parse(tokens):
        token = tokens.peek()
        if token == 'continue':
            tokens.getNext()
            return ContinueStatement(token.position)
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        if scope.innerLoop is None:
            raise error.SyntaxError(self.position, 'Continue statement is only legal inside a while or for loop')

        return self

    def emitCode(self, gen):
        assert gen.continueLabel is not None

        gen.ilGen.Emit(gen.opCodes.Br, gen.continueLabel)
