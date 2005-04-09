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
        from nine.scope import Scope

        arg = self.arg.semantic(scope)
        t = arg.getType()

        if t != vartypes.BooleanType:
            raise TypeError, "While condition must be of type boolean, not %r" % t

        childScope = Scope(parent=scope)
        childScope.innerLoop = self

        block = self.block.semantic(childScope)

        return WhileStatement(arg, block)

    def emitCode(self, gen):
        from nine.codegenerator import CodeGenerator

        from ast.breakstatement import BreakStatement
        from ast.continuestatement import ContinueStatement

        startLabel = gen.ilGen.DefineLabel()
        loopLabel = gen.ilGen.DefineLabel()
        endLabel = gen.ilGen.DefineLabel()

        gen.ilGen.Emit(gen.opCodes.Br, startLabel)
        gen.ilGen.MarkLabel(loopLabel)

        miniGen = CodeGenerator(gen)
        miniGen.breakLabel = endLabel
        miniGen.continueLabel = startLabel
        self.block.emitCode(miniGen)

        gen.ilGen.MarkLabel(startLabel)
        self.arg.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Brtrue, loopLabel)
        gen.ilGen.MarkLabel(endLabel)
