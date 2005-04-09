
import sys
from nine import error
from sys import argv as args, exit
import os.path
import getopt

def syntax():
    name = os.path.split(sys.argv[0])[1]
    print '''
%(name)s - Nine compiler

Syntax:
    %(name)s [options ...] source_file.9

Options:
    -rAssembly\tRefer to an external assembly.
    -oName\tSpecify the name of the resulting executable.

Example:
    %(name)s -oMyProgram -rSystem.Net -rMicrosoft.DirectX MyProgram.9\
    ''' % locals()
    exit(1)

if len(args) < 2:
    syntax()

try:
    options, args = getopt.gnu_getopt(sys.argv[1:], 'r:o:')
except getopt.GetoptError, e:
    print e
    syntax()

from nine.driver import Driver

#sourceName = args[0] # FIXME
sources = args
outputName = 'ninec_output'
references = []

the_driver = Driver()

for option, operand in options:
    if option == '-r':
        the_driver.addReference(operand)

    if option == '-o':
        outputName = operand
try:
    the_driver.compile(sources, outputName)
except error.CodeError, e:
    print e
    sys.exit(1)
