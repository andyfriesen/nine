
class ImportStatement(object):
    def __init__(self, namespace):
        self.namespace = namespace

    def parse(tokens):
        from ast.qualifiedname import QualifiedName

        if tokens.peek() != 'import':
            return None

        tokens.expect('import')

        namespace = QualifiedName.parse(tokens)

        if namespace is None:
            raise Exception, 'Expected namespace name, got %r' % tokens.peek()

        return ImportStatement(namespace)

    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast.namespace import Namespace

        namespace = self.namespace.semantic(scope)
        assert isinstance(namespace, Namespace), "%r is not a namespace" % namespace

        return ImportStatement(namespace)

    def emitCode(self, gen):
        gen.ilGen.UsingNamespace(self.namespace.name)
