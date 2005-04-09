from logicalexpression import LogicalExpression

class Expression(object):
    '''Base class for all expression nodes.
    '''

    def parse(tokens):
        return (
            LogicalExpression.parse(tokens)
        )
    parse = staticmethod(parse)

    def semantic(self, scope):
        assert False, '%s.semantic() was not implemented!' % type(self).__name__

    def emitLoad(self, gen):
        assert False, '%s.emitLoad(generator) was not implemented!' % type(self).__name__
