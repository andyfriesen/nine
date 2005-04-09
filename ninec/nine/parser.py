
from ast.declaration import Declaration
from ast.statement import Statement
from ast.nullstatement import NullStatement

from nine import token
from nine import error

def parse(tokens):
    '''Parses a token stream into an abstract syntax tree.
    '''
    statements = []
    while not tokens.eof():
        while tokens.peek() is token.END_OF_STATEMENT:
            tokens.expect(token.END_OF_STATEMENT)

        if tokens.peek() is token.END_OF_FILE:
            break

        decl = Declaration.parse(tokens)
        if decl is not None:
            statements.append(decl)
            continue

        stmt = Statement.parse(tokens)
        if stmt is not None:
            statements.append(stmt)
            continue

        raise error.SyntaxError(tokens.peek().position, 'Syntax error at %r' % tokens.peek())

    return statements
