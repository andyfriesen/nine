
from ast.declaration import Declaration
from scope import Scope

def makeGlobalScope(globalSymbols={}):
    globalScope = Scope(parent=None)

    for name, sym in globalSymbols.iteritems():
        globalScope[name] = sym

    return globalScope

def collectNames(decls, globalScope):
    for decl in decls:
        globalScope[decl.name] = decl

def resolveNames(decls, globalScope):
    for decl in decls:
        decl.resolveNames(globalScope)

def semantic(ast, globalScope=None):
    if globalScope is None:
        globalScope = Scope(parent=None)

    # Handle type declarations, other (non-type) declarations, and statements, in that order
    from ast.vartypes import Type
    decls = [n for n in ast if isinstance(n, Declaration)]
    stmts = [n for n in ast if n not in decls]

    collectNames(decls, globalScope)
    resolveNames(decls, globalScope)

    result = list()

    for decl in decls:
        result.append(decl.semantic(globalScope))

    for stmt in stmts:
        result.append(stmt.semantic(globalScope))

    # Pass 2.  Some nodes have a semantic2 method.  If it's there, call it.  If not, do nothing.
    result2 = list()
    for stmt in result:
        if hasattr(stmt, 'semantic2'):
            result2.append(stmt.semantic2(globalScope))
        else:
            result2.append(stmt)

    return result2
