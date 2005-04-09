
from ast import assignstatement
from ast import continuestatement
from ast import breakstatement
from ast import expressionstatement
from ast import forstatement
from ast import ifstatement
from ast import importstatement
from ast import nullstatement
from ast import passstatement
from ast import printstatement
from ast import raisestatement
from ast import returnstatement
from ast import trystatement
from ast import vardecl
from ast import whilestatement

from nine.token import END_OF_STATEMENT, END_BLOCK, END_OF_FILE
from nine import error

class Statement(object):
    '''Base class for all statement objects
    '''

    def parse(tokens):
        '''Parses a statement from nine.the input stream and returns it.

        If a statement could not be parsed, None is returned.
        An exception is raised if the statement is an *error*.

        For example, a print statement is always started with the "print"
        keyword.  If this keyword is not found, PrintStatement.parse will
        return None, as the source may be legal, but it is certainly not a
        print statement.
        '''

        stmt = (
            # The 'or' operator short circuits, so each of these are tested in turn.
            # The first non-null result is returned
            importstatement.ImportStatement.parse(tokens) or
            vardecl.VarDecl.parse(tokens) or
            passstatement.PassStatement.parse(tokens) or
            continuestatement.ContinueStatement.parse(tokens) or
            breakstatement.BreakStatement.parse(tokens) or
            printstatement.PrintStatement.parse(tokens) or
            assignstatement.AssignStatement.parse(tokens) or
            expressionstatement.ExpressionStatement.parse(tokens) or
            returnstatement.ReturnStatement.parse(tokens) or
            ifstatement.IfStatement.parse(tokens) or
            forstatement.ForStatement.parse(tokens) or
            trystatement.TryStatement.parse(tokens) or
            raisestatement.RaiseStatement.parse(tokens) or
            whilestatement.WhileStatement.parse(tokens) or
            nullstatement.NullStatement.parse(tokens) or
            None
        )

        if stmt is None:
            return None

        # This is gross:
        # Unless the previous token was an END_BLOCK, demand an END_OF_STATEMENT after the statement

        if tokens[tokens.pos - 1] in (END_OF_STATEMENT, END_BLOCK):
            # HACK: skip the need for an END_OF_STATEMENT after an END_BLOCK
            return stmt

        tok = tokens.getNext()
        if tok not in (END_OF_STATEMENT, END_BLOCK, END_OF_FILE):
            tokens.unget()
            raise error.SyntaxError(tokens.peek().position, 'Expected end-of-statement.  Got %r' % tokens.peek())

        if tok is not END_OF_STATEMENT:
            tokens.unget()

        return stmt

    parse = staticmethod(parse)

    def semantic(self, scope):
        '''Performs semantic checking on the statement.

        Semantic analysis amounts to making sure the statement is sensical.
        This amounts to performing symbol resolution and type
        deduction/testing.
        '''
        assert False, '%s.semantic() is not implemented!' % type(self).__name__

    def emitCode(self, gen):
        '''Emits executable code for the statement.

        'gen' is a CodeGenerator object which recieves the actual MSIL
        instructions that are to be inserted into the resulting executable.
        '''
        assert False, '%s.emitCode(generator) is not implemented!' % type(self).__name__
