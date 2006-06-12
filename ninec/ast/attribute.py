
from ast.identifier import Identifier
from ast.qualifiedname import QualifiedName

class Attribute(object):
    def __init__(self, className, params=None):
        self.className = className
        self.params = params or []

    def parse(tokens):
        startPos = tokens.getPosition()

        if tokens.peek() != '[':
            return None

        tokens.expect('[')

        klass = QualifiedName.parse(tokens)
        if klass is None:
            tokens.setPosition(startPos)
            return None

        tokens.expect(']')

        return Attribute(klass)

    parse = staticmethod(parse)

    def renameIdentifier(ident):
        if isinstance(ident, Identifier):
            return Identifier(ident.name + 'Attribute', ident.position)

        else:
            return QualifiedName(ident.lhs, Attribute.renameIdentifier(ident.rhs))

    renameIdentifier = staticmethod(renameIdentifier)

    def semantic(self, scope):
        className = Attribute.renameIdentifier(self.className).semantic(scope)

        params = []
        for param in self.params:
            params.append(param.semantic(scope))

        attr = Attribute(className, params)

        scope.klass.attributes.append(attr)

        return Attribute(className, params)
