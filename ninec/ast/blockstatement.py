
from nine.token import BEGIN_BLOCK, END_BLOCK, END_OF_FILE

from nine.scope import Scope

class BlockStatement(object):
    def __init__(self, children=None):
        self.children = children or []

    def parse(tokens):
        from ast.statement import Statement
        if tokens.peek() is not BEGIN_BLOCK:
            return None
        tokens.getNext()

        children = list()

        while tokens.peek() is not END_BLOCK:
            stmt = Statement.parse(tokens)
            if stmt is None:
                break
            children.append(stmt)
        tokens.expect(END_BLOCK)

        return BlockStatement(children)

    parse = staticmethod(parse)

    def semantic(self, scope):
        localScope = Scope(parent=scope)

        newBody = []
        for child in self.children:
            newBody.append(child.semantic(localScope))

        return BlockStatement(newBody)

    def emitCode(self, gen):
        for child in self.children:
            child.emitCode(gen)
