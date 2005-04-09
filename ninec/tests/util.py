# Utility functions for making unit tests more straightforward

import os
import os.path

def source(program):
    '''Strips leading whitespace from nine.the lines of
    a multiline string.
    Just like Python would handle this exact docstring:
    The leading whitespace on the first non-blank line (except the first)
    is taken to be the amount of whitespace to be used throughout the
    source.  That amount of whitespace is removed from nine.the beginning of
    each line.  If a line has less than this amount of whitespace, all
    leading whitespace is stripped from nine.the line.
    '''

    lines = program.splitlines()
    leadingSpaces = 0

    if len(lines) > 1:
        index = 1
        while index < len(lines) and not bool(lines[index].lstrip()):
            index += 1

        line = lines[index]
        spaces = 0
        while spaces < len(line) and line[spaces] == ' ':
            spaces += 1

    result = [lines[0]]
    for line in lines[1:]:
        if line.startswith(' ' * spaces):
            result.append(line[spaces:])
        else:
            result.append(line.lstrip())

    return '\n'.join(result)

from nine.driver import Driver
from nine.lexer import lex
from nine.parser import parse
from nine.semantic import semantic

def lexProgram(program):
    return lex(program)

def parseProgram(program):
    return parse(lex(program))

def semanticProgram(program, assemblies=[]):
    from ast.namespace import Namespace
    from ast.vartypes import Type

    driver = Driver()
    globalNs = Namespace('')
    for asm in assemblies:
        driver._scanAssembly(globalNs, asm)

    driver.fixPrimitives()

    return semantic(parse(lex(program)), globalNs.symbols)

def buildProgram(name, program, assemblies=[]):
    exeName = name
    path, name = os.path.split(exeName)
    name, ext = os.path.splitext(name)
    path = path or 'bin'
    ext = ext or '.exe'

    exeName = os.path.join(path, name + '.exe')

    if os.access(exeName, os.F_OK):
        # Delete any pre-existing EXE
        os.unlink(exeName)

    driver = Driver()

    for asm in assemblies:
        driver.addReference(asm)

    driver.compileString(program, exeName)

    assert os.access(exeName, os.F_OK)

def runProgram(name, program, assemblies=[]):
    buildProgram(name, program, assemblies)

    exeName = os.path.join('bin', name)

    print >> file('stdout.txt', 'a'), '--- %s.exe ---' % name
    result = os.system('%s >> stdout.txt' % exeName)
    f = file('stdout.txt', 'a')
    print >> f, '--- end %s.exe ---' % name
    print >> f, ''
    assert result == 0
