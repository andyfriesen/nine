
from CLR import System
import clr
from System.Reflection import Assembly

from ast.expression import Expression
from ast import vartypes

from nine import util

class PrintStatement(object):
    def __init__(self, arg):
        self.arg = arg

    def parse(tokens):
        if tokens.peek() != 'print':
            return None
        else:
            tokens.getNext()
            arg = Expression.parse(tokens)
            if arg is None:
                raise Exception("Expected value at " + repr(tokens.peek()))

            return PrintStatement(arg)
    parse = staticmethod(parse)

    def semantic(self, scope):
        arg = self.arg.semantic(scope)

        return PrintStatement(arg)

    def emitCode(self, gen):
        consoleArgs = System.Array.CreateInstance(System.Type, 1)

        argType = self.arg.getType()
        assert argType is not None, self.arg

        if argType.builder.BaseType == System.Enum:
            consoleArgs[0] = vartypes.IntType.builder

        else:
            for n, pt in vartypes.PrimitiveTypes.iteritems():
                if argType.isSubClass(pt):
                    consoleArgs[0] = pt.builder
                    break
            else:
                consoleArgs[0] = System.Object

        # This is silly.  Need to get a System.Type reference for the Console class.
        consoleType = clr.GetClrType(System.Console)

        mi = consoleType.GetMethod('WriteLine', consoleArgs)

        self.arg.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Call, mi)
