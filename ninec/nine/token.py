
class Token(object):
    def __init__(self, type, value=None, line=None, file=None):
        self.type = type
        self.value = value
        self.line = line
        self.file = file

    def __getPosition(self):
        return (self.line, self.file)

    position = property(__getPosition)

    def __repr__(self):
        s = '<token %r' % self.type
        if self.value is not None:
            s += ' %r' % self.value
        if self.line is not None:
            s += ' at line %i' % self.line
        if self.file is not None:
            s += ' of %s' % self.file
        s += '>'
        return s

    def __str__(self):
        return str(self.value)

    def __eq__(self, rhs):
        if isinstance(rhs, basestring):
            return self.value == rhs
        else:
            return self.value == rhs.value and self.type == rhs.type

    def __ne__(self, rhs):
        return not (self == rhs)

END_OF_STATEMENT = Token('End of statement', '\n')
BEGIN_BLOCK = Token('begin block')
END_BLOCK = Token('end block')
END_OF_FILE = Token('End of file')
