from nine import error
from nine import util
from CLR import System

class IndexExpression(object):
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
        from ast.vartypes import StringType
        indicies = []

        for index in self.indicies:
            index = index.semantic(scope)
            indicies.append(index)
            if index.getType() != IntType:
                raise error.TypeError, "Index must be of type Int"

        identifier = self.identifier.semantic(scope)
        
        if identifier.getType() == StringType:
            #FIXME: consistancy?
            if len(indicies) > 1:
                raise error.CodeError("Strings only use one index")
            
            return _StringIndexExpression(self.position, identifier, indicies[0])
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
    
class _StringIndexExpression(IndexExpression):
    def __init__(self, position, identifier, index):
        super(_StringIndexExpression, self).__init__(position,identifier,index)
        self.position = position
        self.identifier = identifier
        self.index = index
        
    def getType(self):
        from ast.vartypes import CharType
        from ast.vartypes import StringType
        assert self.identifier.getType() == StringType, "StringIndexExpression trying to index non-string"
        #FIXME: This is silly, but the identifier needs to stay a string
        #  and the rest of world needs to see a character
        return CharType

    def emitLoad(self, gen):
        type = self.identifier.getType()

        getm = type.builder.GetMethod('get_Chars')

        self.identifier.emitLoad(gen)
        self.index.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, getm)

    def emitLoadAddress(self, gen):
        """Umm, dunno if this applies to strings
            will we ever want the address of a character in a string?
            FIXME: Making this work allows assigning specific character slots in a string to a variable... maybe this should be disallowed?
        """
        raise error.CodeError("Cannot variablize a character in a string")
        #TODO: Create an emulation of this method's purpose for string assignment
        # will probably just end up a call to emitAssign
        getArgs = [System.Int32] * len(self.indicies)
        getArgs = util.toTypedArray(System.Type, getArgs)

        getm = self.identifier.variable.type.builder.GetMethod('Address', getArgs)

        self.identifier.emitLoad(gen)
        for i, index in enumerate(self.indicies):
            index.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, getm)

    def emitAssign(self, rhs, gen):
        raise error.CodeError("Cannot assign to characters in a string... maybe one day though")
        #TODO:if the world was perfect 'set_Chars' method would exist
        # but apparently strings must be immutable
        type = self.identifier.getType()
        setm = type.builder.GetMethod('set_Chars')

        self.identifier.emitLoad(gen)
        self.index.emitLoad(gen)
        rhs.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Call, setm)

    def __repr__(self):
        return '%r [ %r ]' % (self.identifier, self.index)

