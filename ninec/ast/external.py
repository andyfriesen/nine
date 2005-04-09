
from ast import vartypes
from ast.memberflags import MemberFlags

from nine import error
from nine import util

from CLR import System
from CLR.System.Reflection import BindingFlags, MemberTypes

class ExternalType(vartypes.Type):
    def __init__(self, name, builder):
        super(ExternalType, self).__init__(name, builder)

        self.flags = MemberFlags()

        self.flags.sealed = bool(builder.IsSealed)
        self.flags.abstract = bool(builder.IsAbstract)

        self.symbols = dict() # Stores nested types.

        self.__bases = None

        assert builder not in ExternalType._Types

    def __getBases(self):
        if self.__bases is None:
            bases = list(self.builder.GetInterfaces())
            if self.builder.BaseType is not None:
                bases.insert(0, self.builder.BaseType)

            self.__bases = [ExternalType.getNineType(type) for type in bases]
        return self.__bases

    def __setBases(self, value):
        pass

    bases = property(__getBases, __setBases)

    def getCtor(self, params):
        '''Returns a constructor that recieves the given set of parameters.

        params is a list that contains the types that the returned constructor
        recieves.

        (types, not Parameter instances!)
        '''
        paramTypes = util.toTypedArray(System.Type,
            [util.getNetType(param.getType()) for param in params]
        )

        ctorInfo = self.builder.GetConstructor(paramTypes)

        if ctorInfo is None:
            return None

        else:
            return ExternalConstructor(ctorInfo, self)

    def getMember(self, this, name):
        fieldInfo = self.builder.GetField(name)
        if fieldInfo is not None:
            if fieldInfo.IsStatic and not isinstance(this, vartypes.Type):
                this = this.getType()

            return ExternalField(this, name)

        methodInfo = self.builder.GetMember(name, MemberTypes.Method, BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static)
        if len(methodInfo) > 0:
            return UnresolvedMethod(this, name)

        propertyInfo = self.builder.GetMember(name, MemberTypes.Property, BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static)

        assert len(propertyInfo) in (0, 1), 'Not yet implemented: property %s.%s is overloaded. %r' % (self.builder.FullName, name, list(propertyInfo))

        if len(propertyInfo) > 0:
            return ExternalProperty(this, propertyInfo[0])

        if name in self.symbols:
            return self.symbols[name]

        raise error.NameError, 'External class %s has no member named %s' % (self.builder.FullName, name)

    def getMethod(self, name, paramList, returnType):
        if isinstance(returnType, vartypes.Type):
            returnType = returnType.builder

        if returnType is None:
            # Only user types will not have builders at this point.
            # External classes never return user types.
            # If they could, it would be some sort of circular inter-program dependancy.
            return None

        if not isinstance(returnType, System.Type):
            returnType = ExternalType.getNineType(returnType).builder

        args = util.toTypedArray(System.Type, [util.getNetType(t) for t in paramList])

        methodInfo = self.builder.GetMethod(name, args)
        if methodInfo is None: return None

        if System.Object.ReferenceEquals(methodInfo.ReturnType, returnType):
            return ExternalMethod(self, methodInfo)
        else:
            return None

    def apply(self, args):
        return ExternalConstructorCall(self, args)

    def semantic(self, scope):
        return self

    def emitType(self, gen):
        pass

    def emitDeclaration(self, gen):
        pass

    def emitCode(self, gen):
        pass

    def __repr__(self):
        return '<external type %s>' % self.builder.FullName

    _Types = {}

    def getNineType(type):
        assert type is not None
        if not isinstance(type, System.Type):
            type = util.typeToType(type)

        if type not in ExternalType._Types:
            type = ExternalType(type.FullName, builder=type)
            ExternalType._Types[type] = type
            return type
        else:
            return ExternalType._Types[type]
    getNineType = staticmethod(getNineType)

class ExternalField(object):
    def __init__(self, this, name):
        self.this = this
        self.name = name

        if isinstance(self.this, vartypes.Type):
            self.builder = this.builder
        else:
            self.builder = this.getType().builder

        self.fieldInfo = self.builder.GetField(name)
        self.type = ExternalType.getNineType(self.fieldInfo.FieldType)

    def getType(self):
        return self.type

    def semantic(self, scope):
        return self

    def emitLoad(self, gen):
        if not self.fieldInfo.IsStatic:
            self.this.emitLoad(gen)
            gen.ilGen.Emit(gen.opCodes.Ldfld, self.fieldInfo)
        else:
            gen.ilGen.Emit(gen.opCodes.Ldsfld, self.fieldInfo)

    def emitAssign(self, rhs, gen):
        if not self.fieldInfo.IsStatic:
            self.this.emitLoad(gen)

        rhs.emitLoad(gen)

        if not self.fieldInfo.IsStatic:
            gen.ilGen.Emit(gen.opCodes.Stfld, self.fieldInfo)
        else:
            gen.ilGen.Emit(gen.opCodes.Stsfld, self.fieldInfo)

class ExternalProperty(object):
    def __init__(self, this, propertyInfo):
        assert propertyInfo is not None, this

        self.this = this
        self.propertyInfo = propertyInfo
        self.name = propertyInfo.Name
        self.type = ExternalType.getNineType(propertyInfo.PropertyType)

    def getType(self):
        return self.type

    def semantic(self, scope):
        return self

    def emitLoad(self, gen):
        methodInfo = self.propertyInfo.GetGetMethod()
        assert methodInfo is not None, 'Property %s.%s cannot be read from.' % (self.propertyInfo.DeclaringType.FullName, self.propertyInfo.Name)

        if not methodInfo.IsStatic:
            self.this.emitLoad(gen)

        if methodInfo.IsVirtual:
            gen.ilGen.Emit(gen.opCodes.Callvirt, methodInfo)
        else:
            gen.ilGen.Emit(gen.opCodes.Call, methodInfo)

    def emitAssign(self, rhs, gen):
        methodInfo = self.propertyInfo.GetSetMethod()
        assert methodInfo is not None, 'Property %s.%s cannot be written to.' % (self.propertyInfo.DeclaringType.FullName, self.propertyInfo.Name)

        if not methodInfo.IsStatic:
            self.this.emitLoad(gen)

        rhs.emitLoad(gen)

        if methodInfo.IsVirtual:
            gen.ilGen.Emit(gen.opCodes.Callvirt, methodInfo)
        else:
            gen.ilGen.Emit(gen.opCodes.Call, methodInfo)

class UnresolvedMethod(object):
    '''A method of an external class which has not yet been resolved fully.
    Amounts to a type and a name.  The proper method is resolved and returned
    by the apply() method.
    '''

    def __init__(self, this, name):
        self.this = this
        self.name = name

        if isinstance(self.this, ExternalType):
            self.builder = self.this.builder
            self.this = None
        else:
            self.builder = self.this.getType().builder

        # Determined during semantic phase
        self.args = None
        self.method = None

    def apply(self, args):

        signature = System.Array.CreateInstance(System.Type, len(args))
        for index, arg in enumerate(args):
            signature[index] = arg.getType().builder

        methodInfo = self.builder.GetMethod(self.name, signature)

        if methodInfo is None:
            argTypeNames = ', '.join([arg.FullName for arg in signature])
            raise error.TypeError, 'Unable to find overload of %s.%s that recieves arguments (%s)' % (self.builder.FullName, self.name, argTypeNames)

        return ExternalMethodCall(self.this, methodInfo, args)

    def emitLoad(self, gen):
        assert False, 'Attempt to call unresolved external method %s.%s' % (self.builder.FullName, self.name)

class ExternalMethod(object):
    '''A method of an external class that has been resolved to a specific overload.
    Presently only for internal use: UnresolvedMethod transforms itself into
    an ExternalMethodCall directly.

    This class is primarily used to extract metadata from external methods
    for dealing with polymorphic methods in subclasses.
    '''
    def __init__(self, klass, methodInfo):
        self.klass = klass

        self.methodInfo = methodInfo
        mi = methodInfo
        self.flags = MemberFlags()

        if mi.IsStatic: self.flags.static = True
        if mi.IsVirtual: self.flags.virtual = True
        if mi.IsAbstract: self.flags.abstract = True
        if mi.IsFinal: self.flags.sealed = True

class ExternalConstructor(object):
    '''
    Returned by ExternalType.getConstructor.
    '''
    def __init__(self, builder, klass):
        self.builder = builder
        self.klass = klass

    def apply(self, args):
        return ExternalConstructorCall(self.klass, args)

class ExternalConstructorCall(object):
    def __init__(self, type, args):
        self.type = type
        self.args = args
        self.ctorInfo = None # set in semantic phase

    def semantic(self, scope):
        argTypes = System.Array.CreateInstance(System.Type, len(self.args))
        for index, arg in enumerate(self.args):
            t = arg.getType()
            argTypes[index] = t.builder
            assert argTypes[index] is not None, 'Argument %r has not been semantically tested!' % arg

        type = self.type.builder
        assert type is not None, self.type

        self.ctorInfo = type.GetConstructor(argTypes)

        if self.ctorInfo is None:
            argList = ', '.join([str(arg.getType().name) for arg in self.args])
            raise error.TypeError, 'No constructor for type %s recieving arguments (%s) exists.' % (self.type, argList)

        assert self.ctorInfo is not None, repr(self.args) + ', ' + repr(list(argTypes))

        return self

    def getType(self):
        return self.type

    def emitLoad(self, gen):
        assert self.ctorInfo is not None

        for arg in self.args:
            arg.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Newobj, self.ctorInfo)


class ExternalMethodCall(object):
    def __init__(self, this, methodInfo, args):
        self.this = this
        self.methodInfo = methodInfo
        self.args = args

        if self.methodInfo.IsStatic:
            self.this = None

    def semantic(self, scope):
        if not self.methodInfo.IsStatic and self.this is None:
                raise error.SyntaxError, 'External method %s.%s is nonstatic: it must have a subject' % (self.methodInfo.DeclaringType.FullName, self.methodInfo.Name)

        return self

    def getType(self):
        from ast import vartypes
        t = ExternalType.getNineType(self.methodInfo.ReturnType)
        return t

    def emitLoad(self, gen):
        if not self.methodInfo.IsStatic:
            thisType = self.this.getType()
            if thisType.builder.IsValueType or thisType.builder.IsPrimitive:
                self.this.emitLoadAddress(gen)
            else:
                self.this.emitLoad(gen)

        for arg in self.args:
            arg.emitLoad(gen)

        if not self.methodInfo.IsStatic:
            gen.ilGen.Emit(gen.opCodes.Callvirt, self.methodInfo)
        else:
            gen.ilGen.Emit(gen.opCodes.Call, self.methodInfo)
