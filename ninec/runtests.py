'''
Main unit test thing.  When run, this script executes all unit
tests found in the current package.

'''

import sys
import os.path
from glob import glob

from unittest import TestSuite, TextTestRunner, makeSuite

def main():
    # Remove stdout.txt if it exists
    if os.access('stdout.txt', os.F_OK):
        os.unlink('stdout.txt')

    # find all the unit tests in the current directory, and run them.
    # (this is ridiculously complicated due to path fun)
    tests = []

    suite = TestSuite()

    gutter = {} # dump to place locals and globals because __import__ is WEIRD

    for name in glob(os.path.join('tests', 'test*.py')) + glob(os.path.join('tests', '*test.py')):
        moduleName = 'tests.' + os.path.split(name)[1][:-3] # grab filename, minus .py extension
        module = __import__(moduleName, gutter, gutter, '*')

        for name, cls in module.__dict__.iteritems():
            if name.startswith('Test') or name.endswith('Test'):
                print >> sys.stderr, "Testing " + name
                suite.addTest(makeSuite(cls))

    TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
