'''
Set wrapper.

Use 2.4 set class in Python 2.4
In 2.3, do some name mangling so that types with the same name exist.
'''
import sys

major, minor = sys.version_info[:2]

assert major == 2, "ninec only works on Python 2.x (3.x isn't out yet, and 1.x is ancient)"

if minor < 4:
    from sets import Set as set, ImmutableSet as frozenset

