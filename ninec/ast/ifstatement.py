from ast.expression import Expression
from ast.blockstatement import BlockStatement
from nine import token
import vartypes
from nine import error

class IfStatement(object):
    def __init__(self, statementList):
        self.statementList = statementList

    def parse(tokens):
        statementList=[]

        keyword = tokens.peek()
        if keyword != 'if':
            return None

        tokens.getNext()
        if keyword == 'if':
            arg = Expression.parse(tokens)
            if arg is None:
                raise error.SyntaxError, 'Expected expression at %r' % tokens.peek()

        if tokens.peek() != ':':
            raise error.SyntaxError, "Expected ':' at end of line for '"+str(keyword)+" "+ repr(arg) + "'"

        tokens.expect(':')
        tokens.expect(token.END_OF_STATEMENT)

        block = BlockStatement.parse(tokens)

        statementList.append((keyword, arg, block))

        while True:
            keyword = tokens.peek()

            if keyword not in ('elif', 'else'):
                break

            tokens.expect(keyword)

            if keyword in ('elif',):
                arg = Expression.parse(tokens)
                if arg is None:
                    raise error.SyntaxError, "Expected value at " + repr(tokens.peek())
            else:
                arg = None

            if tokens.peek() != ':':
                raise error.SyntaxError, "Expected ':' at end of line for '"+str(keyword)+" "+ repr(arg) + "'"

            tokens.expect(':')
            tokens.expect(token.END_OF_STATEMENT)
            block = BlockStatement.parse(tokens)

            statementList.append((keyword, arg, block))

        return IfStatement(statementList)
    parse = staticmethod(parse)

    def semantic(self, scope):
        #t = isinstance(self.arg, (AddExpression, LiteralExpression, StringLiteral))
        if self.statementList[0][0] != 'if':
            raise Exception, "Users should NOT see this, we forked the big one. 'if' statement doesn't start with an IF!"

        semanticStatementList = []
        numElse = 0
        oldK = 'if'
        for k, condition, body in self.statementList:
            if k != 'if':
                if k == 'elif':
                    if oldK not in ('if','elif'):
                        raise SyntaxError, k+" cannot come after "+oldK
                if k == 'else':
                    numElse += 1
                    if oldK not in ('if','elif') or numElse > 1:
                        raise SyntaxError, "Only one else statement allowed"

            if condition is not None:
                condition = condition.semantic(scope)
                t = condition.getType()

            if t is not vartypes.BooleanType:
                raise TypeError, k+" condition must be of type boolean, not %r" % t

            body = body.semantic(scope)
            semanticStatementList.append((k, condition, body))

        return IfStatement(semanticStatementList)

    def emitCode(self, gen):
        elseFlag = 0
        end = gen.ilGen.DefineLabel()
        next = gen.ilGen.DefineLabel()

        for k, a, b in self.statementList:
            if k in ('if', 'elif'):
                a.emitLoad(gen)
                gen.ilGen.Emit(gen.opCodes.Brfalse, next)
                b.emitCode(gen)
                gen.ilGen.Emit(gen.opCodes.Br, end)
                gen.ilGen.MarkLabel(next)
                next = gen.ilGen.DefineLabel()
            if k == 'else':
                elseFlag = 1
                gen.ilGen.MarkLabel(next)
                b.emitCode(gen)

        gen.ilGen.MarkLabel(end)
