
from nine import token

class NullStatement(object):
    '''A "statement" which does not actually do anything.
    '''

    def parse(tokens):
        if tokens.peek() == token.END_OF_STATEMENT:
            tokens.getNext()
            return NullStatement()
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        return self

    def emitCode(self, gen):
        pass
