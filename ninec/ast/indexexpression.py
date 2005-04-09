from nine import error
from nine import util
from CLR import System

class IndexExpression(object):
    setValue = {
        'Int32':System.Int32,
        'Boolean':System.Boolean,
        'Single':System.Single,
    }
    def __init__(self, position, identifier, indicies):
        self.position = position
        self.identifier = identifier
        self.indicies = indicies

    def parseIndex(tokens):
        from ast.expression import Expression
        indicies = []

        tokens.expect('[')
        while True:
            indicies.append(Expression.parse(tokens))
            if tokens.peek() == ',':
                tokens.expect(',')
            else:
                tokens.expect(']')
                break
        return indicies
    parseIndex = staticmethod(parseIndex)

    def semantic(self, scope):
        from ast.vartypes import IntType
        indicies = []

        for index in self.indicies:
            index = index.semantic(scope)
            indicies.append(index)
            if index.getType() != IntType:
                raise error.TypeError, "Index must be of type Int"

        identifier = self.identifier.semantic(scope)
        return IndexExpression(self.position, identifier, indicies)

    def getType(self):
        eType = self.identifier.getType()
        assert hasattr(eType, 'arrayType'), self.identifier
        return eType.arrayType

    def emitLoad(self, gen):
        arrayType = self.identifier.getType()

        getArgs = [System.Int32] * len(self.indicies)
        getArgs = util.toTypedArray(System.Type, getArgs)

        getm = arrayType.builder.GetMethod('Get', getArgs)

        self.identifier.emitLoad(gen)
        for i, index in enumerate(self.indicies):
            index.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, getm)

    def emitLoadAddress(self, gen):
        getArgs = [System.Int32] * len(self.indicies)
        getArgs = util.toTypedArray(System.Type, getArgs)

        getm = self.identifier.variable.type.builder.GetMethod('Address', getArgs)

        self.identifier.emitLoad(gen)
        for i, index in enumerate(self.indicies):
            index.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, getm)

    def emitAssign(self, rhs, gen):
        arrayType = self.identifier.getType()

        setArgs = [System.Int32]*len(self.indicies)
        setArgs.append(arrayType.arrayType.builder)
        setArgs = util.toTypedArray(System.Type, setArgs)

        setm = arrayType.builder.GetMethod('Set', setArgs)

        self.identifier.emitLoad(gen)
        for index in self.indicies:
            index.emitLoad(gen)
        rhs.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, setm)

    def __repr__(self):
        return '%r [ %r ]' % (self.identifier, self.indicies)
