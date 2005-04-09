from ast.qualifiedname import QualifiedName
from ast.identifier import Identifier
from ast.blockstatement import BlockStatement

from ast import vartypes, castexpression
from ast import vardecl

from CLR import System
from nine import util

from nine import token
from nine import error

class TryStatement(object):
    def __init__(self, position, tryBlock, exceptBlocks, finallyBlock):
        self.position = position

        self.tryBlock = tryBlock
        self.exceptBlocks = exceptBlocks
        self.finallyBlock = finallyBlock

    def parse(tokens):
        if tokens.peek() != 'try':
            return None

        def eatColon():
            tokens.expect(':')
            tokens.expect('\n')

        position = tokens.peek().position

        token = tokens.expect('try')
        eatColon()

        tryBlock = BlockStatement.parse(tokens)

        while tokens.peek() == '\n': tokens.expect('\n')

        exceptBlocks = []

        while tokens.peek() == 'except':
            tokens.expect('except')

            filter = None

            if tokens.peek() != ":":
                filter = _ExceptFilter.parse(tokens)

            eatColon()

            exceptBlock = BlockStatement.parse(tokens)
            exceptBlocks.append((filter, exceptBlock))

        while tokens.peek() == '\n': tokens.expect('\n')

        finallyBlock = None

        if tokens.peek() == 'finally':
            tokens.expect('finally')
            eatColon()

            finallyBlock = BlockStatement.parse(tokens)

        while tokens.peek() == '\n': tokens.expect('\n')

        if not exceptBlocks and finallyBlock is None:
            raise error.SyntaxError(position, 'Try statement requires except or finally block')

        return TryStatement(position, tryBlock, exceptBlocks, finallyBlock)

    parse = staticmethod(parse)

    def semantic(self, scope):
        tryBlock = self.tryBlock.semantic(scope)

        exceptBlocks = []
        for filter, block in self.exceptBlocks:
            if filter is not None:
                filter = filter.semantic(scope)

                # Throw the captured exception into a local variable that is injected into the BlockStatement
                if filter.variable is not None:
                    block.children.insert(0, filter.variable)

            block = block.semantic(scope)

            exceptBlocks.append((filter, block.semantic(scope)))

        finallyBlock = self.finallyBlock
        if finallyBlock:
            finallyBlock = finallyBlock.semantic(scope)

        return TryStatement(self.position, tryBlock, exceptBlocks, finallyBlock)

    def emitCode(self, gen):
        gen.ilGen.BeginExceptionBlock()

        self.tryBlock.emitCode(gen)

        for filter, block in self.exceptBlocks:
            if filter is None:
                filterType = util.getNineType(System.Exception)
            else:
                filterType = filter.type

            gen.ilGen.BeginCatchBlock(filterType.builder)

            if filter is None or filter.name is None:
                gen.ilGen.Emit(gen.opCodes.Pop)

            block.emitCode(gen)

        if self.finallyBlock is not None:
            gen.ilGen.BeginFinallyBlock()
            self.finallyBlock.emitCode(gen)

        gen.ilGen.EndExceptionBlock()

class _ExceptFilter(object):
    def __init__(self, position, name, type):
        self.position = position
        self.name = name
        self.type = type

        self.variable = None # Variable that recieves the exception

    def parse(tokens):
        position = tokens.peek().position

        name = None
        type = QualifiedName.parse(tokens)

        if isinstance(type, Identifier):
            if tokens.peek() == 'as':
                name = type.name
                tokens.expect('as')

                type = QualifiedName.parse(tokens)

        return _ExceptFilter(position, name, type)
    parse = staticmethod(parse)

    def semantic(self, scope):
        self.type = self.type.semantic(scope)

        if not util.getNineType(System.Exception).isParentClass(self.type):
            raise error.SyntaxError(self.position, "Except argument must be a subclass of System.Exception")

        if self.name is not None:
            if self.name in scope:
                raise error.NameError(self.position, "Identifier %s already declared at %r" % (self.name, scope[self.name].position))

            self.variable = vardecl.VarDecl(self.name, self.position, self.type, _ExceptionThingie(self.type))

        return self

    def emitCode(self, gen):
        if self.builder is None:
            self.variable.emitCode(gen)
            self.builder = self.variable.builder

class _ExceptionThingie(object):
    '''This is a bit weird, but I find myself rather fond of this solution.

    When an exception is caught, it is the topmost element of the evaluation
    stack.  So, capturing this value in a local is simply a matter of immediately
    storing.

    This object helps to achieve that.  The variable that recieves the exception
    is created as a hidden local variable, and its initializer is an instance of this
    class.

    The crux of the whole crooked setup is that nothing is done in the
    emitCode() method.  The local variable has an initializer, so it is processed
    as a normal assignment.  The end result is that the local recieves whatever
    junk just so happens to be sitting on the top of the stack. (which is
    precisely what we want)
    '''
    def __init__(self, type):
        self.type = type

    def semantic(self, scope):
        return self

    def getType(self):
        return self.type

    def emitLoad(self, gen):
        pass
