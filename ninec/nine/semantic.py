
from scope import Scope

def semantic(ast, globalSymbols={}):
    globalScope = Scope(parent=None)

    for name, sym in globalSymbols.iteritems():
        globalScope[name] = sym

    result = []

    # HACK: Handle all class declarations first
    from ast.vartypes import Type
    classes = [n for n in ast if isinstance(n, Type)]
    stmts = [n for n in ast if n not in classes]

    for decl in classes:
        if hasattr(decl, 'name'):
            globalScope[decl.name] = decl

    for decl in classes:
        result.append(decl.semantic(globalScope))

    for stmt in stmts:
        result.append(stmt.semantic(globalScope))

    # Pass 2.  Some nodes have a semantic2 method.  If it's there, call it.  If not, do nothing.
    result2 = []
    for stmt in result:
        if hasattr(stmt, 'semantic2'):
            result2.append(stmt.semantic2(globalScope))
        else:
            result2.append(stmt)

    return result2
