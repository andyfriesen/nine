
class Declaration(object):
    def parse(tokens):
        from ast import classdecl
        from ast import functiondecl
        from ast import interfacedecl
        from ast import vardecl
        from ast import enumdecl
        from ast import delegatedecl

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

    def resolveNames(self, scope):
        assert False, '%r (of type %r) does not implement resolveNames!' % (self, type(self))

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.name)
