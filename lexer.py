import enum


class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = 0
    def current_char(self):
        if self.position < len(self.text):
            return self.text[self.position]
        else:
            return None
    def advance(self):
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
                        raise LexerError("Unexpected escape in string")
                else:
                    string += self.current_char()
                    self.advance()
            if self.is_at_end():
                raise LexerError("Unterminated string literal")
        return string
    def tokenize(self):
        tokens = []
        while not self.is_at_end():
            token = self.current_char()
            if token.isdigit():
                tokens.append(Token(TokenType.INTEGER, self.read_number()))
            elif token.isspace():
                self.skip_whitespace()
            elif token.isalpha() or token == "_":
                identifier = self.read_identifier()
                if identifier not in keywords:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier))
                else:
                    type_ = keywords[identifier]
                    tokens.append(Token(type_, identifier))
            elif token == '"':
                string = self.read_string()
                tokens.append(Token(TokenType.STRING, string))
                self.advance()
            elif token == "=":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.EQ, "=="))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.ASSIGN, "="))
            elif token == "+":
                tokens.append(Token(TokenType.PLUS, "+"))
                self.advance()
            elif token == "-":
                tokens.append(Token(TokenType.MINUS, "-"))
                self.advance()
            elif token == "*":
                tokens.append(Token(TokenType.MULTIPLY, "*"))
                self.advance()
            elif token == "/":
                tokens.append(Token(TokenType.DIVIDE, "/"))
                self.advance()
            elif token == "!":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.NE, "!="))
                    self.advance()
                else:
                    raise LexerError("Unexpected character '!'")

            elif token == "%":
                tokens.append(Token(TokenType.MODULO, "%"))
                self.advance()
            elif token == ">":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.GE, ">="))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT, ">"))

            elif token == "<":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.LE, "<="))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT, "<"))
            elif token == ")":
                tokens.append(Token(TokenType.RPAREN, ")"))
                self.advance()
            elif token == "(":
                tokens.append(Token(TokenType.LPAREN, "("))
                self.advance()
            elif token == ",":
                tokens.append(Token(TokenType.COMMA, ","))
                self.advance()
            elif token == ".":
                tokens.append(Token(TokenType.DOT, "."))
                self.advance()
            elif token == ";":
                tokens.append(Token(TokenType.SEMICOLON, ";"))
                self.advance()
            elif token == "}":
                tokens.append(Token(TokenType.RBRACE, "}"))
                self.advance()
            elif token == "{":
                tokens.append(Token(TokenType.LBRACE, "{"))
                self.advance()
            elif token == "[":
                tokens.append(Token(TokenType.LBRACKET, "["))
                self.advance()
            elif token == "]":
                tokens.append(Token(TokenType.RBRACKET, "]"))
                self.advance()
            else:
                raise LexerError("Unexpected token '%s'" % token)
        tokens.append(Token(TokenType.EOF, "EOF"))


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
    def __init__(self, tokentype, value):
        self.tokentype = tokentype
        self.value = value
    def __repr__(self):
        return f"Token({self.tokentype.name}, {self.value!r})"

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

code = """
x = [1, 2, 3];
"""
lexer = Lexer(code)
print(lexer.tokenize())
