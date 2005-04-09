
from nine import error
from CLR import System
from nine import util

class CastExpression(object):
    def __init__(self, position, arg, type):
        self.position = position
        self.arg = arg
        self.type = type

    def parse(tokens):
        from ast.functioncallexpression import FunctionCallExpression
        from ast.vartypes import Type

        arg = FunctionCallExpression.parse(tokens)
        if arg is None:
            return None

        if tokens.peek() != 'as':
            return arg

        type = CastExpression.parseCast(tokens)

        return CastExpression(arg.position, arg, type)
    parse = staticmethod(parse)

    def parseCast(tokens):
        from ast.vartypes import Type

        tokens.expect('as')

        type = Type.parse(tokens)
        if type is None:
            raise error.SyntaxError, "Expected type name after 'as', got %r" % tokens.peek()

        return type
    parseCast = staticmethod(parseCast)

    def semantic(self, scope):
        arg = self.arg.semantic(scope)
        type = self.type.semantic(scope)

        argType = arg.getType()

        # If the arg type and the cast type are the same, the cast is a no-op
        # Remove it from the code
        if argType == type:
            return arg

        # make sure that arg can be coerced into the type
        if not type.isDescendant(argType) and not argType.isDescendant(type) and not util.getNineType(System.ValueType).isDescendant(argType):
            raise error.TypeError(self.position, "Cannot cast expression %r from type %r to %r" % (arg, argType, type))

        return CastExpression(self.position, arg, type)

    def getType(self):
        return self.type

    def emitLoad(self, gen):

        object = util.getNineType(System.Object)
        value = util.getNineType(System.ValueType)

        ilType = self.type.builder
        assert ilType is not None, self.type

        self.arg.emitLoad(gen)

        if self.type == object and value.isDescendant(self.arg.getType()):      #box
            gen.ilGen.Emit(gen.opCodes.Box, self.arg.getType().builder)
        elif self.type.builder.IsValueType and self.arg.getType() == object:    #unbox
            gen.ilGen.Emit(gen.opCodes.Unbox, ilType)
            if self.type == util.getNineType(System.Int32):
                gen.ilGen.Emit(gen.opCodes.Ldind_I4)
            elif self.type == util.getNineType(System.Single):
                gen.ilGen.Emit(gen.opCodes.Ldind_R4)
            else:
                assert False, "oh shit! dinosaurs!. Actually we've got some not-primitive value types not getting unboxed."
        else:
            #cast to primitive types
            if self.type == util.getNineType(System.Int32):
                gen.ilGen.Emit(gen.opCodes.Conv_I4)
            elif self.type == util.getNineType(System.Single):
                gen.ilGen.Emit(gen.opCodes.Conv_R4)
            elif self.type == util.getNineType(System.Double):
                gen.ilGen.Emit(gen.opCodes.Conv_R8)
            else:
                #cast to a class
                gen.ilGen.Emit(gen.opCodes.Castclass, ilType)
