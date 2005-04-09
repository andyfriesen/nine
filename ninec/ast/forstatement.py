
from nine import error
from nine import util
from ast import vardecl

from CLR import System

class ForStatement(object):
    def __init__(self, position, iterator, sequence, body):
        self.position = position
        self.iterator = iterator
        self.sequence = sequence
        self.body = body

    def parse(tokens):
        from ast.blockstatement import BlockStatement
        from ast.expression import Expression
        from ast.identifier import Identifier
        from ast.vardecl import VarDecl
        from ast.vartypes import Type

        if tokens.peek() != 'for':
            return None

        position = tokens.peek().position
        tokens.expect('for')

        ident = Identifier.parse(tokens)
        if ident is None:
            raise error.SyntaxError(position, 'Expected iterator name, got %r' % tokens.peek())

        type = None

        """if tokens.peek() == 'as':
            tokens.expect('as')
            type = Type.parse(tokens)
            if type is None:
                raise error.SyntaxError(tokens.peek().position, 'Expected type after "as", got %r' % tokens.peek())"""

        tokens.expect('in')

        sequence = Expression.parse(tokens)
        if sequence is None:
            raise error.SyntaxError(tokens.peek().position, 'Expected expression after "in", got %r' % tokens.peek())

        tokens.expect(':')
        tokens.expect('\n')

        body = BlockStatement.parse(tokens)
        if body is None:
            raise error.SyntaxError(tokens.peek().position, 'Expected loop body after ":", got %r' % tokens.peek())

        return ForStatement(position, VarDecl(ident.name, ident.position, type), sequence, body)
    parse = staticmethod(parse)

    def semantic(self, scope):
        self.iterator.type = util.getNineType(System.Object)
        iterator = self.iterator.semantic(scope)
        iterator = vardecl._LocalVar(iterator.name, iterator.position, iterator.type)
        scope.symbols[iterator.name] = iterator

        sequence = self.sequence.semantic(scope)
        body = self.body.semantic(scope)

        return ForStatement(self.position, iterator, sequence, body)

    def emitCode(self, gen):
        self.iterator.emitCode(gen)

        IEnumerator = util.getNineType(System.Collections.IEnumerator)
        Object = util.getNineType(System.Object)

        gem = self.sequence.getType().getMethod('GetEnumerator', (), IEnumerator)
        getEnumeratorMethod = getattr(gem, 'builder', None) or getattr(gem, 'methodInfo', None)

        assert getEnumeratorMethod is not None, self

        enumerator = gen.defineLocal(IEnumerator)

        self.sequence.emitLoad(gen)
        gen.ilGen.Emit(gen.opCodes.Callvirt, getEnumeratorMethod)
        gen.ilGen.Emit(gen.opCodes.Stloc, enumerator)

        startLabel = gen.ilGen.DefineLabel()
        endLabel = gen.ilGen.DefineLabel()

        gen.ilGen.MarkLabel(startLabel)

        # if not enumerator.GetNext(): goto end
        gnm = IEnumerator.getMethod('MoveNext', (), util.getNineType(System.Boolean))
        getNextMethod = getattr(gnm, 'builder', None) or getattr(gnm, 'methodInfo', None)
        gen.ilGen.Emit(gen.opCodes.Ldloc, enumerator)
        gen.ilGen.Emit(gen.opCodes.Callvirt, getNextMethod)
        gen.ilGen.Emit(gen.opCodes.Brfalse, endLabel)

        # iterator = enumerator.Current
        gcm = IEnumerator.getMethod('get_Current', (), Object)
        getCurrentMethod = getattr(gcm, 'builder', None) or getattr(gcm, 'methodInfo', None)
        gen.ilGen.Emit(gen.opCodes.Ldloc, enumerator)
        gen.ilGen.Emit(gen.opCodes.Callvirt, getCurrentMethod)
        gen.ilGen.Emit(gen.opCodes.Stloc, self.iterator.builder)

        from nine.codegenerator import CodeGenerator

        subGen = CodeGenerator(gen)
        subGen.breakLabel = endLabel
        subGen.continueLabel = startLabel

        self.body.emitCode(subGen)

        gen.ilGen.Emit(gen.opCodes.Br, startLabel)

        gen.ilGen.MarkLabel(endLabel)
