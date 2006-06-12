
from ast import vartypes
from ast import external
from nine import error
from nine import util

class ArrayType(external.ExternalType):
    def __init__(self, position, arrayType, arity):
        self.position = position
        self.arrayType = arrayType
        self.arity = arity
        self.__builder = None

        from ast.external import ExternalType
        from CLR import System
        self.bases = [ExternalType.getNineType(System.Array)]

    def parse(tokens):
        from ast.expression import Expression
        from ast.literalexpression import IntLiteral
        from nine.token import Token

        if tokens.peek() != 'array':
            return None

        position = tokens.peek().position

        tokens.expect('array')

        tokens.expect('(')

        arrayType = vartypes.Type.parse(tokens)
        if arrayType is None:
            raise error.SyntaxError(position, 'Expected type, got %r' % tokens.peek())

        arity = IntLiteral(position, 1)

        if tokens.peek() == ',':
            tokens.expect(',')
            arity = Expression.parse(tokens)
            if arity is None:
                raise error.SyntaxError(position, 'Expected array arity after type, got %r' % tokens.peek())

        tokens.expect(')')

        return ArrayType(position, arrayType, arity)
    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast.literalexpression import IntLiteral

        self.arrayType = self.arrayType.semantic(scope)
        assert self.arrayType is not None

        self.arity = self.arity.semantic(scope)
        if not isinstance(self.arity, IntLiteral):
            raise error.SyntaxError(self.position, 'Array arity must be a positive integer, not %r' % self.arity)

        self.arity = int(self.arity.value)

        if self.arity < 1:
            raise error.SyntaxError(self.position, 'Array arity must be a positive integer, not %r' % self.arity)

        return self

    def __eq__(self, rhs):
        if not hasattr(rhs, 'arity') or not hasattr(rhs, 'arrayType'):
            return False

        return self.arity == rhs.arity and self.arrayType == rhs.arrayType

    def __neq__(self, rhs):
        return not self.__eq__(rhs)

    def __getBuilder(self):
        from ast.external import ExternalType
        from CLR import System

        if 0:
            # Only works with .NET 2.0
            # (which is, as of this writing, still in beta)
            self.__builder = self.arrayType.builder.MakeArrayType(self.arity)

        else:
            # Utterly idiotic.
            # Have to ask the builder's module to get the array type *by name*
            # This really is the only way to do it.  As far as I can tell, Mono's C#
            # compiler does the same thing.
            # --andy

            name = self.name # bracket suffixes and stuff

            if isinstance(self.arrayType, ExternalType):
                # System.Type can retrieve the array type of an external type.
                self.__builder = System.Type.GetType(name)

            else:
                if self.arrayType.builder is None:
                    # HACK
                    # Don't have a builder for the array type, so can't get a builder for an array of that type.
                    # Just return the base array type.  It'll serve well enough for method lookup and the like.
                    from CLR import System
                    return util.getNetType(System.Array)

                else:
                    # Ask the ModuleBuilder for arrays of user types.
                    self.__builder = self.arrayType.builder.Module.GetType(name)

        assert self.__builder is not None, self
        return self.__builder

    builder = property(__getBuilder)

    def __getName(self):
        arity = self.arity
        if hasattr(arity, 'getValue'):
            arity = arity.getValue()

        if self.arrayType.external:
            return self.arrayType.builder.FullName + '[' + (',' * (arity - 1)) + ']'
        else:
            return self.arrayType.name + '[' + (',' * (arity - 1)) + ']'
    name = property(__getName)
