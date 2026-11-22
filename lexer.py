import enum
from Errors import LexerError


class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
    def current_char(self):
        if self.position < len(self.text):
            return self.text[self.position]
        else:
            return None
    def advance(self):

        if self.current_char() == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    def is_at_end(self):
        return self.position >= len(self.text)
    def skip_whitespace(self):
        while not self.is_at_end() and self.current_char().isspace():
            self.advance()
    def read_number(self):
        integer = ""
        while not self.is_at_end() and  self.current_char().isdigit():
            integer += self.current_char()
            self.advance()
        return int(integer)
    def read_identifier(self):
        string = ""
        if self.current_char().isalpha() or self.current_char() == "_":
            while not self.is_at_end() and (self.current_char().isalpha() or self.current_char().isdigit() or self.current_char() == "_"):
                string += self.current_char()
                self.advance()
        return string
    def read_string(self):
        string = ''
        if self.current_char() == '"':
            self.advance()
            while not (self.current_char() == '"') and not self.is_at_end():
                if self.current_char() == "\\" :
                    self.advance()
                    if self.current_char() in escapes and not self.is_at_end():
                        string += escapes[self.current_char()]
                        self.advance()
                    else:
                        raise LexerError("Unexpected escape in string", self.line, self.column)
                else:
                    string += self.current_char()
                    self.advance()
            if self.is_at_end():
                raise LexerError("Unterminated string literal", self.line, self.column)
        return string
    def tokenize(self):
        tokens = []
        while not self.is_at_end():
            token = self.current_char()
            start_line = self.line
            start_column = self.column
            if token.isdigit():
                tokens.append(Token(TokenType.INTEGER, self.read_number(), start_line, start_column))
            elif token.isspace():
                self.skip_whitespace()
            elif token.isalpha() or token == "_":
                identifier = self.read_identifier()
                if identifier not in keywords:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier,  start_line, start_column))
                else:
                    type_ = keywords[identifier]
                    tokens.append(Token(type_, identifier,  start_line, start_column))
            elif token == '"':
                string = self.read_string()
                tokens.append(Token(TokenType.STRING, string, start_line, start_column))
            elif token == "=":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.EQ, "==", start_line, start_column))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_column))
            elif token == "+":
                tokens.append(Token(TokenType.PLUS, "+", start_line, start_column))
                self.advance()
            elif token == "-":
                tokens.append(Token(TokenType.MINUS, "-", start_line, start_column))
                self.advance()
            elif token == "*":
                tokens.append(Token(TokenType.MULTIPLY, "*", start_line, start_column))
                self.advance()
            elif token == "/":
                tokens.append(Token(TokenType.DIVIDE, "/", start_line, start_column))
                self.advance()
            elif token == "!":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.NE, "!=", start_line, start_column))
                    self.advance()
                else:
                    raise LexerError("Unexpected character '!'", start_line, start_column)

            elif token == "%":
                tokens.append(Token(TokenType.MODULO, "%", start_line, start_column))
                self.advance()
            elif token == ">":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.GE, ">=", start_line, start_column))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT, ">", start_line, start_column))

            elif token == "<":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.LE, "<=", start_line, start_column))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT, "<", start_line, start_column))
            elif token == ")":
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_column))
                self.advance()
            elif token == "(":
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_column))
                self.advance()
            elif token == ",":
                tokens.append(Token(TokenType.COMMA, ",", start_line, start_column))
                self.advance()
            elif token == ".":
                tokens.append(Token(TokenType.DOT, ".", start_line, start_column))
                self.advance()
            elif token == ";":
                tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_column))
                self.advance()
            elif token == "}":
                tokens.append(Token(TokenType.RBRACE, "}", start_line, start_column))
                self.advance()
            elif token == "{":
                tokens.append(Token(TokenType.LBRACE, "{", start_line, start_column))
                self.advance()
            elif token == "[":
                tokens.append(Token(TokenType.LBRACKET, "[", start_line, start_column))
                self.advance()
            elif token == "]":
                tokens.append(Token(TokenType.RBRACKET, "]", start_line, start_column))
                self.advance()
            else:
                raise LexerError("Unexpected token '%s'" % token, start_line, start_column)
        tokens.append(Token(TokenType.EOF, "EOF", start_line , start_column))


        return tokens
class TokenType(enum.Enum):
    INTEGER = enum.auto()
    IDENTIFIER = enum.auto()
    ASSIGN = enum.auto()
    PLUS = enum.auto()
    UNKNOWN = enum.auto()
    IF = enum.auto()
    ELSE = enum.auto()
    WHILE = enum.auto()
    CLASS = enum.auto()
    FUNCTION = enum.auto()
    RETURN = enum.auto()
    STRING = enum.auto()
    MODULO = enum.auto()
    MULTIPLY = enum.auto()
    DIVIDE = enum.auto()
    MINUS = enum.auto()
    EQ = enum.auto()
    NE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    GE = enum.auto()
    LE = enum.auto()
    DOT = enum.auto()
    LPAREN = enum.auto()
    RPAREN = enum.auto()
    COMMA = enum.auto()
    BOOLEAN = enum.auto()
    AND = enum.auto()
    OR = enum.auto()
    NOT = enum.auto()
    LBRACE = enum.auto()
    RBRACE = enum.auto()
    SEMICOLON = enum.auto()
    EOF = enum.auto()
    NULL = enum.auto()
    LBRACKET = enum.auto()
    RBRACKET = enum.auto()
    FOR = enum.auto()
    EXTEND = enum.auto()
class Token:
    def __init__(self, tokentype, value, line, column):
        self.tokentype = tokentype
        self.value = value
        self.line = line
        self.column = column
    def __repr__(self):
        return f"Token({self.tokentype.name}, {self.value!r}, {self.line!r}, {self.column!r})"

booleans = {
    "true": True,
    "false": False,
}

escapes = {
    "\\": "\\",
    "n": "\n",
    "t": "\t",
    '"': "\"",
}
keywords = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "Class": TokenType.CLASS,
    "Function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "true": TokenType.BOOLEAN,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "false": TokenType.BOOLEAN,
    "Null": TokenType.NULL,
    "for": TokenType.FOR,
    "extends": TokenType.EXTEND,
}


