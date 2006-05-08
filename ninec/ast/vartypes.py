
from CLR import System

from nine import error
from nine import config

class Type(object):
    def __init__(self, name, builder=None):
        self.name = name
        self.__builder = builder
        self.bases = []
        self.external = False

    def getBuilder(self):
        return self.__builder

    def setBuilder(self, value):
        assert self.__builder is None, 'Internal error: attempt to overwrite existing builder!!'
        self.__builder = value

    builder = property(getBuilder, setBuilder)

    def parse(tokens):
        peek = tokens.peek()
        if peek.type == 'keyword':
            name = tokens.getNext()

            if peek.value in PrimitiveTypes:
                return PrimitiveTypes[peek.value]

            elif peek.value == 'array':
                tokens.unget()
                from ast.arraytype import ArrayType
                return ArrayType.parse(tokens)

            else:
                raise error.SyntaxError, 'Expected type name, got %r' % name

        else:
            from ast.qualifiedname import QualifiedName

            type = QualifiedName.parse(tokens)
            if type is None:
                raise error.SyntaxError, 'Expected type name, got %r' % tokens.peek()

            return type
    parse = staticmethod(parse)

    def semantic(self, scope):
        # Types have already been resolved if they are Type instances.  Smile and nod to make the semantic analyzer happy.
        assert False, 'Class %s does not override Type.semantic (%r)' % (type(self).__name__, self)
        return self

    def getMember(self, this, name):
        assert False, 'Class %s does not override Type.getMember  (%r)' % (type(self).__name__, self)

    def getCtor(self, params):
        '''Returns a constructor that recieves the given set of parameters.

        params is a list that contains the types that the returned constructor
        recieves.

        (types, not Parameter instances!)
        '''
        assert False, 'Class %s does not override Type.getCtor' % type(self).__name__

    def getMethod(self, name, paramTypes, returnType):
        assert False, 'Class %s does not override Type.getMethod' % type(self).__name__

    def isDescendant(self, type):
        'Returs true if self is a child class of type'
        return self.isParentClass(type)
        assert hasattr(type, 'bases'), (type, dir(type))

        from CLR import System

        if self == type:
            return True

        for base in type.bases:
            if self.isDescendant(base):
                return True
        else:
            return False

    def isParentClass(self, type):
        '''Returns true if "self" inherits "type", either directly or indirectly.
        '''

        if self == type:
            return True

        # Typical breadth-first search
        i = 0
        bases = type.bases[:]
        while i < len(bases):
            base = bases[i]
            i += 1

            if self == base:
                return True

            # add all bases to our list of classes to search
            # (except the ones we've already checked)
            for b in base.bases:
                if b not in bases:
                    bases.append(b)

        return False

    def isSubClass(self, type):
        return type.isParentClass(self)

    def __repr__(self):
        return '<%s %s 0x%08X>' % (type(self).__name__, self.name, id(self))

    if not config.DEBUG:
        # Pretty-print type names in release mode
        def __str__(self):
            return str(self.name)

    def __eq__(self, rhs):
        if not hasattr(rhs, 'builder'): return False

        if self.builder is None: return self is rhs

        from CLR import System
        return System.Object.ReferenceEquals(self.builder, rhs.builder)

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

# I hate this stupid class.  It's needed, though, because they need to be known about before assemblies are scanned.
# Their semantic() phase replaces them with the proper type
class __WTF:
    def __init__(self, type):
        from nine import util
        self.type = util.getNetType(type)

    def __repr__(self):
        return '<WTF %s>' % self.type.FullName

    def semantic(self, *args):
        from nine import util
        return util.getNineType(self.type)

IntType = __WTF(System.Int32)
FloatType = __WTF(System.Single)
BooleanType = __WTF(System.Boolean)
StringType = __WTF(System.String)
VoidType = __WTF(System.Void)
ObjectType = __WTF(System.Object)

PrimitiveTypes = {
    'int' : IntType,
    'float' : FloatType,
    'boolean' : BooleanType,
    'string' : StringType,
    'void' : VoidType,
    'object' : ObjectType
}
