from lexer import *
from Errors import *
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]
    def advance(self):
        if self.current().tokentype != TokenType.EOF:
            current_token = self.current()
            self.position += 1
            return current_token
        else:
            return self.current()

    def expect(self, tokentype):
        if self.current().tokentype == tokentype:
            return self.advance()
        raise ParserError("Expected '%s'" % tokentype, self.current())
    def is_at_end(self):
        return self.current().tokentype == TokenType.EOF
    def factor(self):
        if self.current().tokentype == TokenType.INTEGER:
            value = self.current().value
            self.advance()
            result = NumberLiteral(value)
        elif self.current().tokentype == TokenType.BOOLEAN:
            boolean = self.current().value
            self.advance()
            boolean = boolean == "true"
            result = BooleanLiteral(boolean)

        elif self.current().tokentype == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            expression = self.expression()
            self.expect(TokenType.RPAREN)
            result = expression
        elif self.current().tokentype == TokenType.IDENTIFIER:
            identifier = self.current().value
            self.advance()

            result = Identifier(identifier)
        elif self.current().tokentype == TokenType.PLUS or self.current().tokentype == TokenType.MINUS:
            operator = self.current().tokentype
            self.advance()
            operand = self.factor()
            return UnaryExpression(operator, operand)
        elif self.current().tokentype == TokenType.STRING:
            string = self.current().value
            self.advance()
            result = StringLiteral(string)
        elif self.current().tokentype == TokenType.NULL:
            self.advance()
            result = NullLiteral()
        elif self.current().tokentype == TokenType.LBRACKET:
            items = []
            self.expect(TokenType.LBRACKET)
            if self.current().tokentype == TokenType.RBRACKET:
                self.expect(TokenType.RBRACKET)
                result = ListLiteral(items)
            else:
                while self.current().tokentype != TokenType.RBRACKET:
                    items.append(self.expression())

                    if self.current().tokentype == TokenType.COMMA:
                        self.advance()
                    elif self.current().tokentype != TokenType.RBRACKET:
                        raise ParserError("Expected ',' or ']'", self.current())
                self.expect(TokenType.RBRACKET)
                result = ListLiteral(items)
        else:
            raise ParserError(f"Unexpected token '{self.current().value}'", self.current())
        while True:
            if self.current().tokentype == TokenType.DOT:
                self.expect(TokenType.DOT)
                member = self.expect(TokenType.IDENTIFIER)
                result = MemberExpression(result, Identifier(member.value))
            elif self.current().tokentype == TokenType.LBRACKET:
                self.expect(TokenType.LBRACKET)
                index = self.expression()
                self.expect(TokenType.RBRACKET)
                result = IndexExpression(result, index)
            elif self.current().tokentype == TokenType.LPAREN:
                self.expect(TokenType.LPAREN)
                arguments = []

                if self.current().tokentype != TokenType.RPAREN:
                    while self.current().tokentype != TokenType.RPAREN:
                        arguments.append(self.expression())

                        if self.current().tokentype == TokenType.COMMA:
                            self.advance()
                            if self.current().tokentype == TokenType.RPAREN:
                                raise ParserError("Expected argument after ','", self.current())
                        elif self.current().tokentype != TokenType.RPAREN:
                            raise ParserError("Expected ',' or ')'", self.current())

                self.expect(TokenType.RPAREN)
                result = FunctionCall(result, arguments)
            else:
                break
        return result
    def term(self):
        left = self.factor()
        while self.current().tokentype == TokenType.MULTIPLY or self.current().tokentype == TokenType.DIVIDE or self.current().tokentype == TokenType.MODULO:
            operator = self.current().tokentype
            self.advance()
            right = self.factor()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left
    def expression(self):
        return self.logical_or()
    def arithmetic(self):
        left = self.term()
        while self.current().tokentype == TokenType.PLUS or self.current().tokentype == TokenType.MINUS:
            operator = self.current().tokentype
            self.advance()
            right = self.term()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left
    def comparison(self):
        left = self.arithmetic()
        while self.current().tokentype == TokenType.EQ or self.current().tokentype == TokenType.NE or self.current().tokentype == TokenType.GE or self.current().tokentype == TokenType.LE or self.current().tokentype == TokenType.LT or self.current().tokentype == TokenType.GT:
            operator = self.current().tokentype
            self.advance()
            right = self.arithmetic()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left
    def logical_not(self):
        if self.current().tokentype == TokenType.NOT:
            operator = self.current().tokentype
            self.advance()
            operand = self.logical_not()
            expression = UnaryExpression(operator, operand)
            return expression
        else:
            return self.comparison()
    def logical_and(self):
        left = self.logical_not()
        while self.current().tokentype == TokenType.AND:
            operator = self.current().tokentype
            self.advance()
            right = self.logical_not()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left
    def logical_or(self):
        left = self.logical_and()
        while self.current().tokentype == TokenType.OR:
            operator = self.current().tokentype
            self.advance()
            right = self.logical_and()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left

    def assignment(self):
        start = self.position

        try:
            target = self.assignment_target()
        except ParserError:
            self.position = start
            return self.expression()
        allowed = (Identifier, MemberExpression, IndexExpression)

        if isinstance(target, allowed) and self.current().tokentype == TokenType.ASSIGN:
            self.expect(TokenType.ASSIGN)
            value = self.assignment()
            return Assignment(target, value)
        else:
            self.position = start
            return self.expression()

    def assignment_target(self):
        return self.factor()

    def statement(self):
        if self.current().tokentype == TokenType.LBRACE:
            statements = []
            self.expect(TokenType.LBRACE)
            while self.current().tokentype != TokenType.RBRACE:
                statement = self.statement()
                statements.append(statement)
            self.expect(TokenType.RBRACE)
            return BlockStatement(statements)
        elif self.current().tokentype == TokenType.IF:
            self.expect(TokenType.IF)
            self.expect(TokenType.LPAREN)
            condition = self.assignment()
            self.expect(TokenType.RPAREN)
            body = self.statement()
            if self.current().tokentype == TokenType.ELSE:
                self.expect(TokenType.ELSE)
                else_branch = self.statement()
                return IfStatement(condition, body, else_branch)

            return IfStatement(condition, body)
        elif self.current().tokentype == TokenType.WHILE:
            self.expect(TokenType.WHILE)
            self.expect(TokenType.LPAREN)
            condition = self.assignment()
            self.expect(TokenType.RPAREN)
            body = self.statement()
            return WhileStatement(condition, body)
        elif self.current().tokentype == TokenType.FUNCTION:
            self.expect(TokenType.FUNCTION)
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            parameters = []
            if self.current().tokentype == TokenType.RPAREN:
                self.expect(TokenType.RPAREN)
            else:
                while self.current().tokentype != TokenType.RPAREN:
                    parameters.append(Identifier(self.expect(TokenType.IDENTIFIER).value))
                    if self.current().tokentype == TokenType.COMMA:
                        self.advance()
                        if self.current().tokentype != TokenType.IDENTIFIER:
                            raise ParserError("Expected parameter after ','", self.current())
                    elif self.current().tokentype != TokenType.RPAREN:
                        raise ParserError("Expected ',' or ')'", self.current())
                self.expect(TokenType.RPAREN)
            body = self.statement()

            return FunctionDeclaration(name,body,parameters)
        elif self.current().tokentype == TokenType.RETURN:
            self.expect(TokenType.RETURN)
            if self.current().tokentype == TokenType.SEMICOLON:
                self.expect(TokenType.SEMICOLON)
                return ReturnStatement()
            else:
                ass = self.assignment()
                self.expect(TokenType.SEMICOLON)
                return ReturnStatement(ass)
        elif self.current().tokentype == TokenType.FOR:
            self.expect(TokenType.FOR)
            self.expect(TokenType.LPAREN)
            if self.current().tokentype == TokenType.SEMICOLON:
                init = None
            else:
                init = self.assignment()
            self.expect(TokenType.SEMICOLON)

            if self.current().tokentype == TokenType.SEMICOLON:
                condition = None
            else:
                condition = self.expression()
            self.expect(TokenType.SEMICOLON)

            if self.current().tokentype == TokenType.RPAREN:
                increment = None
            else:
                increment = self.assignment()
            self.expect(TokenType.RPAREN)

            body = self.statement()

            return ForStatement(body, init, condition, increment)
        elif self.current().tokentype == TokenType.CLASS:
            self.expect(TokenType.CLASS)
            name = Identifier(self.expect(TokenType.IDENTIFIER).value)
            if self.current().tokentype == TokenType.EXTEND:
                self.expect(TokenType.EXTEND)
                superclass = Identifier(self.expect(TokenType.IDENTIFIER).value)
            else:
                superclass = None
            self.expect(TokenType.LBRACE)
            methods = []
            while self.current().tokentype != TokenType.RBRACE:
                if self.is_at_end():
                    raise ParserError("Expected '}'", self.current())
                if self.current().tokentype != TokenType.FUNCTION:
                    raise ParserError("Expected Function declaration inside class", self.current())

                methods.append(self.statement())

            self.expect(TokenType.RBRACE)
            return ClassDeclaration(name, methods, superclass)
        else:
            statement = self.assignment()
            self.expect(TokenType.SEMICOLON)

            return ExpressionStatement(statement)

    def parse(self):
        statements = []

        while not self.is_at_end():
            statement = self.statement()
            statements.append(statement)

        return Program(statements)

class ASTNode:
    pass
class NullLiteral(ASTNode):
    pass
    def __repr__(self):
        return (
            f"NULL"
        )
class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"NumberLiteral(value={self.value!r})"
class BooleanLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"BooleanLiteral(value={self.value!r})"
class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return (
            f"String(value={self.value!r})"
        )
class BlockStatement(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"BlockStatement(statements={self.statements!r})"
class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"IfStatement(condition={self.condition!r}, then_branch={self.then_branch!r}, else_branch={self.else_branch!r})"
class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"WhileStatement(condition={self.condition!r}, body={self.body!r})"
class ForStatement(ASTNode):
    def __init__(self, body, initializer=None, condition = None, increment=None ):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body
    def __repr__(self):
       return f"ForStatement(body={self.body!r}, condition={self.condition!r}, increment={self.increment!r})"
class FunctionDeclaration(ASTNode):
    def __init__(self, name, body, parameters=None):
        self.name = name
        self.parameters = [] if parameters is None else parameters
        self.body = body
    def __repr__(self):
       return f"FunctionDeclaration(name={self.name!r}, parameters= {self.parameters!r}, body={self.body!r})"
class FunctionCall(ASTNode):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
    def __repr__(self):
        return f"FunctionCall(callee={self.callee!r}, arguments={self.arguments})"
class ReturnStatement(ASTNode):
    def __init__(self, value=None):
        self.value = value
    def __repr__(self):
        return f"ReturnStatement(value={self.value!r})"
class ClassDeclaration(ASTNode):
    def __init__(self, name, body, superclass=None):
        self.name = name
        self.superclass = superclass
        self.body = body
    def __repr__(self):
        return f"ClassDeclaration(name={self.name!r}, superclass={self.superclass!r}, body={self.body!r})"
class MemberExpression(ASTNode):
    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop
    def __repr__(self):
        return f"MemberExpression(obj={self.obj!r}, prop={self.prop!r})"
class ListLiteral(ASTNode):
    def __init__(self, items=None):
        self.items = [] if items is None else items
    def __repr__(self):
        return (
            f"ListLiteral(items={self.items!r})"
        )
class IndexExpression(ASTNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index
    def __repr__(self):
        return f"IndexExpression(obj={self.obj!r}, index={self.index!r})"
class Identifier(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return (
            f"Identifier(value={self.value!r})"
        )
class BinaryExpression(ASTNode):
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

    def __repr__(self):
        return (
            f"BinaryExpression("
            f"left={self.left!r}, "
            f"operator={self.operator!r}, "
            f"right={self.right!r})"
        )
class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value
    def __repr__(self):
        return (
            f"Assignment(identifier={self.identifier!r}, value={self.value!r})"
        )
class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return (
            f"ExpressionStatement(expression={self.expression!r})"
        )
class UnaryExpression(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryExpression(operator={self.operator}, operand={self.operand})"
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return "Program(statements={})".format(self.statements)