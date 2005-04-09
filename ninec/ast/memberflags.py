
AllFlags = (
    'static',
    'virtual', 'override', 'abstract', 'sealed',

    'public', 'private', 'protected', 'internal',

    'newslot', # Internal gayness.  TODO: try to eradicate.
)

class MemberFlags(object):
    def __init__(self, **kw):
        for flag in AllFlags:
            setattr(self, flag, kw.get(flag, False))

    def __eq__(self, rhs):
        for flag in AllFlags:
            if getattr(self, flag) != getattr(rhs, flag):
                return False
        else:
            return True

    def __neq__(self, rhs):
        return not self.__eq__(rhs)

    def __iter__(self):
        for flag in AllFlags:
            if getattr(self, flag):
                yield flag

    def __repr__(self):
        return '<flags %r>' % (tuple(self),)
