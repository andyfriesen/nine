
from nine.token import *
from ast.expression import Expression

class RaiseStatement(object):
    def __init__(self, position, expr):
        self.position = position
        self.expr = expr

    def parse(tokens):
        if tokens.peek() != 'raise':
            return None

        position = tokens.peek().position
        tokens.expect('raise')
        expr = Expression.parse(tokens)
        if expr is None:
            raise error.SyntaxError(position, 'Expected expression, got %r' % tokens.peek())

        return RaiseStatement(position, expr)
    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast import vartypes
        from nine import error, util
        from CLR import System

        expr = self.expr.semantic(scope)

        if not util.getNineType(System.Exception).isParentClass(expr.getType()):
            raise error.SyntaxError(self.position, "You can only throw object instances which inherit System.Exception, not %r" % expr.getType())

        return RaiseStatement(self.position, expr)

    def emitCode(self, gen):
        from nine import util

        self.expr.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Throw)
