
import clr
import CLR
from CLR import System

CLRMeta = type(System.String)

def typeToType(t):
    '''Horrible hack around the fact that Python.NET gets confused between
    the distinction between System.Type instances and Python classes.

    The basic approach is thus: get the full name, then use System.Reflection
    to fetch the assembly which contains the type, and ask it for the type.
    As a fun aside, this can also be achieved in one line of C#:

    Type typeToType(Type t) { return t; }

    But I am not yet ready to add more non-Python dependancies to Nine.
    (especially since this one would be so small)
    '''
    assert t is not None
    return clr.GetClrType(t)

    moduleName = t.__module__
    #assert moduleName.startswith('CLR.')

    fullName = moduleName[4:] + '.' + t.__name__

    # HACK: PythonNet does some wizardry with System.Exception, and it breaks our code.
    if issubclass(t, System.Exception):
        assembly = System.Reflection.Assembly.GetAssembly(t._class)

    else:
        assembly = System.Reflection.Assembly.GetAssembly(t)

    return assembly.GetType(fullName)

def toTypedArray(type, elements):
    '''Copy an iterable sequence into a typed .NET array.
    '''
    arr = System.Array.CreateInstance(type, len(elements))

    for index, elem in enumerate(elements):
        arr[index] = elem

    return arr

def getNineType(theType):
    from ast.external import ExternalType
    from ast.vartypes import Type

    if isinstance(theType, Type):
        return theType
    elif isinstance(theType, type):
        return ExternalType.getNineType(clr.GetClrType(theType))
    elif isinstance(theType, basestring):
        return ExternalType.getNineType(System.Type.GetType(theType))

    return ExternalType.getNineType(theType)

def getNetType(theType):
    from ast.vartypes import Type, PrimitiveType
    from ast.external import ExternalType

    if isinstance(theType, PrimitiveType):
        return theType.semantic(None)

    if hasattr(theType, 'builder'):
        return theType.builder

    else:
        assert False, (theType, type(theType))
