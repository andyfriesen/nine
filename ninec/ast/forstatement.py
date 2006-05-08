
from nine import error
from nine import util
from ast import vardecl
from nine import log

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
        '''
        Slightly nasty.  We do an AST replacement here, turning the for loop
        into an equivalent while loop using an IEnumerator instance.

        Long story short, this:

            for iterator as T in y:
                stmts

        becomes this:

            var _e = y.GetEnumerator()
            while _e.MoveNext():
                var iterator = _e.Current as T
                stmts
        '''

        from ast.blockstatement import BlockStatement
        from ast.whilestatement import WhileStatement
        from ast.assignstatement import AssignStatement
        from ast.castexpression import CastExpression
        from ast.arraytype import ArrayType
        from ast.vardecl import VarDecl
        from nine.scope import Scope

        IEnumerator = util.getNineType(System.Collections.IEnumerator)
        Object = util.getNineType(System.Object)
        Boolean = util.getNineType(System.Boolean)

        elementType = Object

        sequence = self.sequence.semantic(scope)
        seqType = sequence.getType()

        if isinstance(seqType, ArrayType):
            elementType = seqType.arrayType
        elif self.iterator.type is not None:
            elementType = self.iterator.type

        enumerator = VarDecl('$$$ secret enumerator 0x%08X $$$' % id(self), self.position, IEnumerator,
            initializer=seqType.getMember(sequence, 'GetEnumerator').apply(())
        )

        miniScope = Scope(parent=scope)

        enumerator = enumerator.semantic(miniScope)

        # var iterator = enumerator.get_Current() as ElementType
        assert self.iterator.initializer is None, self
        self.iterator.initializer = CastExpression(self.position, IEnumerator.getMember(enumerator, 'get_Current').apply(()), elementType)

        # Finally, create the new replacement AST, do the usual semantic
        # testing on it, and return it as a replacement for our ForStatement
        # expression.
        return BlockStatement((
            enumerator,
            WhileStatement(
                IEnumerator.getMember(enumerator, 'MoveNext').apply(()),

                BlockStatement((
                    self.iterator,
                    self.body,
                ))
            )
        )).semantic(miniScope)
