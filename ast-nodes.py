from lexer import *
class ParserError(Exception):
    pass
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
        if self.current().tokentype != tokentype:
            raise ParserError("Unexpected type")
        else:
            return self.advance()
    def is_at_end(self):
        return self.current().tokentype == TokenType.EOF
    def factor(self):
        if self.current().tokentype == TokenType.INTEGER:
            value = self.current().value
            self.advance()
            return NumberLiteral(value)
        elif self.current().tokentype == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            expression = self.expression()
            self.expect(TokenType.RPAREN)
            return expression
        else:
            raise ParserError("Unexpected token")
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
        left = self.term()
        while self.current().tokentype == TokenType.PLUS or self.current().tokentype == TokenType.MINUS:
            operator = self.current().tokentype
            self.advance()
            right = self.term()
            expression = BinaryExpression(left, right, operator)
            left = expression
        return left
    def parse(self):
        return self.expression()

class ASTNode:
    pass
class NullLiteral(ASTNode):
    pass
class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberLiteral(value={self.value!r})"
class BooleanLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
class BlockStatement(ASTNode):
    def __init__(self, statements):
        self.statements = statements
class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
class ForStatement(ASTNode):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body
class FunctionDeclaration(ASTNode):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body
class FunctionCall(ASTNode):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
class ReturnStatement(ASTNode):
    def __init__(self, value=None):
        self.value = value
class ClassDeclaration(ASTNode):
    def __init__(self, name, body, superclass=None):
        self.name = name
        self.superclass = superclass
        self.body = body
class MemberExpression(ASTNode):
    def __init__(self, object, property):
        self.object = object
        self.property = property
class SelfExpression(ASTNode):
    pass
class ListLiteral(ASTNode):
    def __init__(self, items=[]):
        self.items = items
class IndexExpression(ASTNode):
    def __init__(self, object, index):
        self.object = object
        self.index = index
class Identifier(ASTNode):
    def __init__(self, value):
        self.value = value
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
class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
class UnaryExpression(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
lexer = Lexer("2 + 3 * 4")
parser = Parser(lexer.tokenize())
print(parser.parse())