
from nine import error

class ReturnStatement(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

    def parse(tokens):
        from ast.expression import Expression
        from nine import token

        if tokens.peek() != 'return':
            return None

        position = tokens.peek().position

        tokens.expect('return')

        if tokens.peek() is not token.END_OF_STATEMENT:

            value = Expression.parse(tokens)
            if value is None:
                raise error.SyntaxError(position, 'Expected end of statement or expression, got %r' % tokens.peek())
        else:
            value = None

        return ReturnStatement(position, value)
    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast import vartypes

        if scope.func is None or scope.func.returnType == vartypes.VoidType:
            value = None

            if self.value is not None:
                raise error.TypeError, 'Function returns void.  Expression is not allowed here.'

        else:
            if self.value is None:
                raise error.TypeError, 'Function %s has return type %r.  Return statement must have a value.' % (scope.func.name, scope.func.returnType)

            value = self.value.semantic(scope)
            type = value.getType()

            if type != scope.func.returnType:
                raise error.TypeError, 'Function %s returns value of %r, not %r' % (scope.func.name, scope.func.returnType, type)

        return ReturnStatement(self.position, value)

    def emitCode(self, gen):
        if self.value is not None:
            self.value.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Ret)
