
from nine import error
from nine import util

class NewArrayExpression(object):
    def __init__(self, position, elementType, size):
        self.position = position
        self.elementType = elementType  # The type of an element in the array
        self.arrayType = None           # The type of the array itself.  Determined in the semantic phase (below)
        self.size = size

    def parse(tokens):
        from ast.vartypes import Type
        from ast.expression import Expression

        if tokens.peek() != 'array':
            return None

        position = tokens.peek().position
        tokens.expect('array')
        tokens.expect('(')

        arrayType = Type.parse(tokens)
        if arrayType is None:
            raise error.SyntaxError(position, 'Expected type after "(", got %r' % tokens.peek())

        tokens.expect(',')

        size = []

        while True:
            s = Expression.parse(tokens)
            if s is None:
                raise error.SyntaxError(position, 'Expected expression for array size, got %r' % tokens.peek())

            size.append(s)

            if tokens.peek() == ',':
                tokens.expect(',')
            else:
                break
        tokens.expect(')')

        return NewArrayExpression(position, arrayType, size)
    parse = staticmethod(parse)

    def getType(self):
        from ast.arraytype import ArrayType
        return ArrayType(0, self.elementType, len(self.size))

    def semantic(self, scope):
        from ast.arraytype import ArrayType
        from ast import vartypes

        self.elementType = self.elementType.semantic(scope)
        self.arrayType = ArrayType(0, self.elementType, len(self.size))

        size = []
        for s in self.size:
            s = s.semantic(scope)
            if s.getType() != vartypes.IntType:
                raise error.TypeError, 'Size of new array must be int, not %r' % s.getType()

            size.append(s)

        self.size = size
        return self

    def emitLoad(self, gen):
        for s in self.size:
            s.emitLoad(gen)

        if len(self.size) == 1:
            gen.ilGen.Emit(gen.opCodes.Newarr, self.elementType.builder)

        else:
            from CLR import System
            from ast import vartypes

            argTypes = (vartypes.IntType.builder,) * len(self.size)
            argTypes = util.toTypedArray(System.Type, argTypes)

            ctor = self.arrayType.builder.GetConstructor(argTypes)
            assert ctor is not None, (self.arrayType, self.arrayType.builder.FullName)

            gen.ilGen.Emit(gen.opCodes.Newobj, ctor)
