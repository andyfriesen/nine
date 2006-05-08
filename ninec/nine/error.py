
class CodeError(Exception):
    def __init__(self, pos, msg=None):
        if msg is None:
            Exception.__init__(self, pos)
            self.line, self.file = (None, '<Unknown File>')

        else:
            Exception.__init__(self, msg)
            self.line, self.file = pos

    def __str__(self):
        if self.line is not None:
            return 'Error on line %s of %s: %s' % (self.line, self.file, Exception.__str__(self))
        else:
            return Exception.__str__(self)

class InternalError(CodeError):
    "Errors that arise from a shoddy compiler."

class LexError(CodeError):
    "An error encountered by the lexer.  Tends to be synonymous with a particularly nasty syntax error."

class SyntaxError(CodeError):
    "Errors that can't be classified more precisely, basically."
    pass

class TypeError(CodeError):
    'Errors that arise from type mismatch or misuse.'
    pass

class NameError(CodeError):
    'Errors about naming collisions.'
    pass

class OverrideError(CodeError):
    'Errors that pertain to definitions of polymorphic classes.'
    pass

class CircularInheritanceError(CodeError):
    'Errors concerning classes that mutually inherit each other.'
    pass
