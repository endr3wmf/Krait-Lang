class InterpreterError(Exception):
    pass
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
class ParserError(Exception):
    def __init__(self, message, token):
        self.message = message
        self.token = token
        super().__init__(
            f"{message} at line {token.line}, column {token.column}"
        )
class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

        super().__init__(
            f"{message} at line {line}, column {column}"
        )
