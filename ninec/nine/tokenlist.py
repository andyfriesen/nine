
from nine import error

class TokenList(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.pos=0

    def peek(self):
        assert self.pos < len(self), 'Internal error: Attempt to read past end of file!'
        return self[self.pos]

    def getNext(self):
        tmp = self.peek()
        self.pos += 1
        return tmp

    def unget(self):
        assert self.pos > 0
        self.pos -= 1

    def getPosition(self):
        return self.pos

    def setPosition(self, index):
        self.pos = index

    def eof(self):
        return self.pos == len(self)

    def expect(self, value):
        next = self.peek()
        if next != value:
            raise error.SyntaxError, 'Expected %r.  Got %r' % (value, next)

        return self.getNext()
