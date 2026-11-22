
from lexer import *
from parser import Parser, ParserError
from interpreter.interpreter import Interpreter, InterpreterError
import argparse
import sys

arg_parser = argparse.ArgumentParser(
    prog="Krait",
    description="Krait Programming Language Interpreter"
)

arg_parser.add_argument(
    "file",
    help="Path to Krait source file"
)

args = arg_parser.parse_args()
try:
    with open(args.file, "r", encoding="utf-8") as file:
        source = file.read()
except FileNotFoundError:
    arg_parser.error(f"File '{args.file}' not found")

try:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
except LexerError as e:
    print(f"Lexer Error: {e}")
    sys.exit(1)
try:
    parser = Parser(tokens)
    ast = parser.parse()
except ParserError as e:
    print(f"Krait Parser Error: {e}")
    sys.exit(1)
try:
    interpreter = Interpreter()
    result = interpreter.evaluate(ast)
    if result is not None:
        print(result)
except InterpreterError as e:
    print(f"Krait Interpreter Error: {e}")
    sys.exit(1)