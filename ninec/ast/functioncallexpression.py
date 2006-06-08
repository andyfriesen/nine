
from ast.identifier import Identifier
from ast.functiondecl import FunctionDecl
from ast.dotexpression import DotExpression

from nine import error

class FunctionCallExpression(object):
    def __init__(self, position, func, args):
        assert isinstance(func, (Identifier, FunctionDecl, DotExpression)), func

        self.position = position
        self.func = func
        self.args = args

    def parseArgList(tokens):
        from ast.expression import Expression
        tokens.expect('(')

        args = []

        # parse arguments
        while True:
            if tokens.peek() == ')':
                break

            arg = Expression.parse(tokens)
            if arg is None:
                raise error.SyntaxError, 'Expected expression, got %r' % tokens.peek()
            args.append(arg)

            peek = tokens.peek()
            if peek == ',':
                tokens.expect(',')
            elif peek == ')':
                break
            else:
                raise error.SyntaxError, 'Expected comma or end parenth, got %r' % peek

        tokens.expect(')')

        return args
    parseArgList = staticmethod(parseArgList)

    def getType(self):
        assert self.func is not None, "Internal error: Don't know the return type of an unresolved method!"

        return self.func.returnType

    def semantic(self, scope):
        from ast import vartypes

        func = self.func.semantic(scope)
        if func is None:
            raise error.NameError('Unable to resolve %r' % self.func)

        args = []
        for arg in self.args:
            a = arg.semantic(scope)
            args.append(a)

        self.args = args

        if hasattr(func, 'apply'):
            result = func.apply(self.args).semantic(scope)
            return result

        if len(self.args) != len(func.params):
            raise error.SyntaxError, 'Function %s requires %i arguments, only got %i' % (func.name, len(func.params), len(self.args))

        args = []
        for arg, param in zip(self.args, func.params):
            a = arg.semantic(scope)
            assert a is not None

            argType = a.getType()
            if argType != param.type:
                raise error.TypeError, 'Cannot convert argument from nine.type %r to %r in call to %s' % (param.type, argType, func.name)

            args.append(a)

        self.func = func
        self.args = args
        return self

    def emitLoad(self, gen):
        for arg in self.args:
            arg.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, self.func.builder)
