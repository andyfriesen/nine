'''
Logging API

The general jist of it is as follows:

Every log message has two parts: a 'tag', and the actual message.  The tag is just a category, basically.

All log categories are suppressed except for those found in the 'flags' set.  To enable a category, just add it to the set.
'''

from nine.set import *

flags = set()

def write(flag, *args):
    if flag in flags:
        print ' '.join(map(str, args))

# Example: to get all kinds of information about how the code generation happens, uncomment this line:
#flags.add('emit')
