
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

    moduleName = t.__module__
    assert moduleName.startswith('CLR.')

    fullName = moduleName[4:] + '.' + t.__name__

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

    if isinstance(theType, CLRMeta):
        theType = typeToType(theType)

    if isinstance(theType, System.Type):
        return ExternalType.getNineType(theType)
    elif isinstance(theType, basestring):
        return ExternalType.getNineType(System.Type.GetType(theType))
    elif isinstance(theType, Type):
        return theType
    else:
        assert False, (theType, type(theType))

def getNetType(theType):
    from ast.vartypes import Type

    if isinstance(theType, CLRMeta):
        theType = typeToType(theType)

    if isinstance(theType, Type):
        return theType.builder

    elif isinstance(theType, System.Type):
        return theType

    else:
        assert False, theType

