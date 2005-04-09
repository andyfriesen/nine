from ast.expression import Expression
from nine.token import END_OF_STATEMENT
from ast.blockstatement import BlockStatement
import vartypes
from nine.error import SyntaxError, TypeError

class WhileStatement(object):
    def __init__(self, arg, block):
        self.arg = arg
        self.block = block

    def parse(tokens):
        if tokens.peek() != 'while':
            return None
        tokens.getNext()
        arg = Expression.parse(tokens)
        if arg is None:
            raise SyntaxError(tokens.peek().position, "Expected value at " + repr(tokens.peek()))

        tokens.expect(':')
        tokens.getNext()

        block = BlockStatement.parse(tokens)
        return WhileStatement(arg, block)
    parse = staticmethod(parse)

    def semantic(self, scope):
        arg = self.arg.semantic(scope)
        t = arg.getType()

        if t is not vartypes.BooleanType:
            raise TypeError, "While condition must be of type boolean, not %r" % t

        block = self.block.semantic(scope)

        return WhileStatement(arg, block)

    def emitCode(self, gen):
        from ast.breakstatement import BreakStatement
        from ast.continuestatement import ContinueStatement

        start = gen.ilGen.DefineLabel()
        loop = gen.ilGen.DefineLabel()
        end = gen.ilGen.DefineLabel()
        breakFlag = False

        gen.ilGen.Emit(gen.opCodes.Br, start)
        gen.ilGen.MarkLabel(loop)
        #FIXME: This is a bad way of doing things
        #   but I cannot think of another way for continue and break statements
        #   to have access to label references
        for child in self.block.children:
            if isinstance(child, BreakStatement):
                breakFlag = True
                gen.ilGen.Emit(gen.opCodes.Br, end)
            elif isinstance(child, ContinueStatement):
                gen.ilGen.Emit(gen.opCodes.Br, start)
            else:
                child.emitCode(gen)

        #self.block.emitCode(gen)
        gen.ilGen.MarkLabel(start)
        self.arg.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Brtrue, loop)
        if breakFlag:
            gen.ilGen.MarkLabel(end)
