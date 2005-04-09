
from ast import classdecl
from ast import functiondecl
from ast import interfacedecl
from ast import vardecl
from ast import enumdecl
from ast import delegatedecl

class Declaration(object):
    def parse(tokens):
        return (
            classdecl.ClassDecl.parse(tokens) or
            interfacedecl.InterfaceDecl.parse(tokens) or
            enumdecl.EnumDecl.parse(tokens) or
            vardecl.VarDecl.parse(tokens) or
            functiondecl.FunctionDecl.parse(tokens) or
            delegatedecl.DelegateDecl.parse(tokens) or
            None
        )

    parse = staticmethod(parse)
