
from CLR import System

from ast.vardecl import VarDecl

from nine import error

class Parameter(VarDecl):
    '''Represents a named parameter in a function body.
    '''

    def __init__(self, position, name, type):
        super(Parameter, self).__init__(name, position, type)
        self.index = None # set by FunctionDecl.semantic()

    def parse(tokens):
        from ast.vartypes import Type

        tok = tokens.getNext()

        if tok.type != 'identifier':
            tokens.unget()
            return None

        position = tok.position
        name = tok.value
        type = None

        if tokens.peek() == 'as':
            tokens.expect('as')
            type = Type.parse(tokens)

            if type is None:
                raise error.SyntaxError(position, 'Expected type after "as", got %r' % tokens.peek())
        else:
            raise error.InternalError(position, 'Untyped parameters are not yet implemented')

        return Parameter(position, name, type)
    parse = staticmethod(parse)

    def semantic(self, scope):
        #return self
        type = self.type
        if hasattr(type, 'semantic'):
            type = type.semantic(scope)

        return Parameter(self.position, self.name, type)

    def getType(self):
        return self.type

    def emitLoad(self, gen):
        assert self.index is not None, self

        gen.ilGen.Emit(gen.opCodes.Ldarg_S, System.Int16(self.index))

    def emitAssign(self, rhs, gen):
        assert self.index is not None, self

        rhs.emitCode(gen)
        gen.ilGen.Emit(gen.opCodes.Starg_S, System.Int16(self.index))
