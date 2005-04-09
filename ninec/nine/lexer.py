
from nine.token import *
from nine.tokenlist import TokenList

from nine import error

KEYWORDS = (
    'print',

    'as',

    # Flow Control
    'goto',
    'if',
    'else',
    'elif',
    'while',
    'for',
    'break',
    'continue',
    'try',
    'except',
    'finally',
    'raise',
    'return',

    # Definitions
    'def',
    'class',
    'interface',
    'delegate',
    'var',

    # Primitive type names
    'float',
    'int',
    'string',
    'boolean',
    'void',
    'array',

    # Declaration modifiers
    'static',
    'virtual',
    'override',
    'abstract',
    'sealed',

    # Unary operators
    'not',

    # Binary operators
    'and',
    'or',

    # Primitive constants
    'true',
    'false',
    'self',
    'null', # 'None'?
)

RelationalOperators = (
    '!=',
    '==',
    '>=',
    '<=',
    '>',
    '<',
)

ShiftOperators = (
    '<<',
    '>>',
    '>>>',
)

AddOperators = (
    '+',
    '-',
)

MultiplyOperators = (
    '**',
    '*',
    '/',
    '%',
)

UnaryOperators = (
    '+',
    '-',
    '~',
    'not',
)

BitwiseOperators = (
    '|',
    '&',
    '^',
)

AssignOperators = (
    '=',
    '<<=',
    '>>=',
    '>>>=',
    '+=',
    '-=',
    '*=',
    '/=',
    '%=',
    '&=',
    '|=',
    '^='
)

OPERATORS = list(
    RelationalOperators + ShiftOperators + AddOperators + MultiplyOperators +
    UnaryOperators + BitwiseOperators + AssignOperators
)

# Operators need to be sorted by length
OPERATORS.sort(lambda a, b: len(b) - len(a))

# Opening brackets and their closing counterparts
OPEN_BRACKETS = {
    '(' : ')',
    '{' : '}',
    '[' : ']',
}

# Inverse of OPEN_BRACKETS
CLOSE_BRACKETS = dict([(v, k) for k, v in OPEN_BRACKETS.iteritems()])

def _countIndent(line):
    'Returns the number of spaces of indentation that a line has.'
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        elif char == '\t':
            raise error.LexError('Do not use hard tabs to indent!  It is EVIL.')
        elif char == '\n':
            # This is a blank line.  Blank lines don't count.  Start counting all over.
            count = 0
        else:
            return count

    return 0

def _lexNumber(source, pos):
    '''Lexes a number.

    source - The entirety of the source text. (as a string)
    pos - Current position within the source text. (integer)

    Returns (token, pos) where token is the number that was lexed out,
    and pos is the position of the next non-number character.
    '''
    startpos = pos

    c = source[pos]
    assert c.isdigit(), "_lexNumber expected a digit, not %s" % repr(c)

    token = c
    pos += 1
    while pos < len(source):
        c = source[pos]
        if c.isdigit() or c == '.':
            token += c
            pos += 1
        else:
            break

    return Token('literal', token, startpos), pos

def _lexIdentifier(source, pos):
    '''Lexes an identifier. (this comment is extraneous)

    See _lexNumber.  It's practically the same in every respect imaginable.
    '''
    startpos = pos

    c = source[pos]
    assert c.isalpha() or c == '_', '_lexNumber expected an alphanumeric or underscore, not %s' % repr(c)
    token = c
    pos += 1
    while pos < len(source):
        c = source[pos]
        if c.isalpha() or c.isdigit() or c == '_':
            token += c
            pos += 1
        else:
            break

    if token in KEYWORDS:
        return Token('keyword', token, startpos), pos
    else:
        return Token('identifier', token, startpos), pos

def _lexStringLiteral(source, pos):
    'Works the same way as _lexIdentifier and _lexNumber'

    c = source[pos]
    assert c in '\'\"', '_lexStringLiteral expected "\'", not %r' % c
    openquote = c

    pos += 1
    token = c
    while pos < len(source):
        c = source[pos]

        if c == '\n':
            raise error.LexError("End of line reached before end of string literal")

        if c == openquote:
            token += c
            pos += 1
            break

        if c == '\\' and pos < len(source) - 1:
            pos += 1
            c = source[pos]

        token += c
        pos += 1
        if pos >= len(source):
            break

    return Token('literal', token), pos

def _lexComment(source, pos):
    'Works the same way as _lexIdentifier and _lexNumber'

    c = source[pos]
    pos += 1
    assert c == '#', '_lexComment expected a #, not %r' % c

    comment = c
    while c != '\n':
        c = source[pos]
        pos += 1
        comment += c

    return Token('comment', comment), pos - 1

def _findNewLines(source):
    # linear indeces of every newline in the program
    newLines = []
    pos = 0
    while True:
        pos = source.find('\n', pos)
        if pos == -1:
            break

        newLines.append(pos)
        # Increment pos so that the next source.find call finds the next newline AFTER the one we just reported.
        pos += 1

    return newLines or [0] # Make sure at least one element is returned.

def lex(source, fileName='<unknown>'):
    pos = 0
    tokens = []
    newLines = _findNewLines(source)
    curLine = 0

    pos = 0

    # when an open brace, bracket, or parenth is encountered, it is pushed onto the symbol stack
    # while the symbol stack is not empty, newlines are ignored.
    # When the corresponding closing brace/bracket/parenth is encountered, newlines are once
    # more converted to END_OF_STATEMENT tokens
    symbolStack = []

    def getChar():
        if pos < len(source):
            return source[pos]
        else:
            return None

    def eof():
        return pos >= len(source)

    indents = [0] # as code indents, we push the previous indentation level

    while not eof():

        # If the current position is after the next newline char, increment the current line counter.
        # (deal with going past the end of the newLines list the boring but servicable way)
        try:
            while pos > newLines[curLine]:
                curLine += 1
        except IndexError:
            pass

        c = source[pos]

        if c == '\n':
            pos += 1

            if not symbolStack:
                # If there are no open parenths anyplace, then a few 'special' tokens get injected into the token stream
                # these tokens correspond to changes in whitespace.
                # 1: END_OF_STATEMENT is injected when we see a newline character.
                # 2: if the indentation on the following line is greater than the previous line, insert BEGIN_BLOCK and
                #    remember how far we've indented. (we need it when we encounter a dedent)
                # 3: if indentation is less than the previous line, make sure it's a dedent to a previous indentation amount,
                #    and insert END_BLOCKS for each indented block that was ended.

                if tokens and tokens[-1] is not END_OF_STATEMENT:
                    # Don't throw these things in without any thought at all.
                    # Redundant eos tokens is irritating.

                    tokens.append(END_OF_STATEMENT)

                count = _countIndent(source[pos:])

                if count > indents[-1]:
                    indents.append(count)
                    tokens.append(BEGIN_BLOCK)

                elif count < indents[-1]:
                    while count < indents[-1]:
                        assert len(indents) > 1
                        tokens.append(END_BLOCK)
                        indents.pop()

                    if count != indents[-1]:
                        raise error.LexError((curLine, fileName), 'Indentation does not match any previous level')

            continue

        elif c.isspace():
            pos += 1
            continue

        elif c.isalpha():
            try:
                token, pos = _lexIdentifier(source, pos)
            except error.CodeError, e:
                e.line, e.file = (curLine, fileName)
                raise e

        elif c.isdigit():
            try:
                token, pos = _lexNumber(source, pos)
            except error.CodeError, e:
                e.line, e.file = (curLine, fileName)
                raise e

        elif c == '\'' or c == '"':
            # String literal
            try:
                token, pos = _lexStringLiteral(source, pos)
            except error.CodeError, e:
                e.line, e.file = (curLine, fileName)
                raise e

        elif c == '#':
            try:
                comment, pos = _lexComment(source, pos)
            except error.CodeError, e:
                e.line, e.file = (curLine, fileName)
                raise e
            continue

        else:

            if c in OPEN_BRACKETS:
                symbolStack.append(c)

            elif c in CLOSE_BRACKETS:
                if not symbolStack or symbolStack[-1] != CLOSE_BRACKETS[c]:
                    raise error.LexError((curLine, fileName), 'Close bracket %s encountered before corresponding open bracket' % c)

                symbolStack.pop()

            symbol = source[pos]
            endPos = pos + 1
            while True:
                if endPos >= len(source) or source[pos:endPos + 1] not in OPERATORS:
                    break
                endPos += 1

            symbol = source[pos:endPos]
            pos = endPos
            token = Token('symbol', symbol, curLine)

        token.line = curLine
        token.file = fileName
        tokens.append(token)

    if not tokens or tokens[-1] is not END_OF_STATEMENT:
        tokens.append(END_OF_STATEMENT)

    while indents[-1] > 0:
        tokens.append(END_BLOCK)
        indents.pop()

    if not tokens or tokens[-1] is not END_OF_STATEMENT:
        tokens.append(END_OF_STATEMENT)

    if symbolStack:
        raise error.LexError((curLine, fileName), 'End-of-file reached before closing %r' % OPEN_BRACKETS[symbolStack[-1]])

    tokens.append(END_OF_FILE)

    return TokenList(tokens)
