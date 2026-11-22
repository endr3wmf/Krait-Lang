from unittest import case

from .environment import *
from parser import *
from lexer import *
from Errors import *


def hiss(value):
    print(value)
class BuiltinFunction:
    def __init__(self, name, function):
        self.name = name
        self.function = function

class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.environment.define(
            "hiss",
            BuiltinFunction("hiss", hiss)
        )
    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        return True
    def evaluate(self, node):
        if isinstance(node, (NumberLiteral, StringLiteral, BooleanLiteral,NullLiteral)):
            if isinstance(node, NullLiteral):
                return None
            else:
                return node.value

        elif isinstance(node, BinaryExpression):
            left = self.evaluate(node.left)
            operator = node.operator
            match operator:
                case TokenType.PLUS:
                    return left + self.evaluate(node.right)
                case TokenType.MINUS:
                    return left - self.evaluate(node.right)
                case TokenType.MULTIPLY:
                    return left * self.evaluate(node.right)
                case TokenType.DIVIDE:
                    return left / self.evaluate(node.right)
                case TokenType.MODULO:
                    return left % self.evaluate(node.right)
                case TokenType.GT:
                    return left > self.evaluate(node.right)
                case TokenType.LT:
                    return left < self.evaluate(node.right)
                case TokenType.EQ:
                    return left == self.evaluate(node.right)
                case TokenType.NE:
                    return left != self.evaluate(node.right)
                case TokenType.LE:
                    return left <= self.evaluate(node.right)
                case TokenType.GE:
                    return left >= self.evaluate(node.right)
                case TokenType.AND:
                    if self.is_truthy(left):
                        return self.is_truthy(left) and self.is_truthy(self.evaluate(node.right))
                    else:
                        return self.is_truthy(left)
                case TokenType.OR:
                    if self.is_truthy(left):
                        return self.is_truthy(left)
                    else:
                        return self.is_truthy(self.evaluate(node.right))
        elif isinstance(node, Program):
            result = None
            for statement in node.statements:
                result = self.evaluate(statement)
            return result
        elif isinstance(node, ExpressionStatement):
            return self.evaluate(node.expression)
        elif isinstance(node, UnaryExpression):
            operand = self.evaluate(node.operand)
            operator = node.operator
            match operator:
                case TokenType.PLUS:
                    return operand
                case TokenType.MINUS:
                    return -operand
                case TokenType.NOT:
                    return not self.is_truthy(operand)
        elif isinstance(node, IfStatement):
            condition = self.evaluate(node.condition)
            if self.is_truthy(condition):
                return self.evaluate(node.then_branch)
            elif node.else_branch is not None:
                return self.evaluate(node.else_branch)
            else:
                return None
        elif isinstance(node, BlockStatement):
            res = None
            for statement in node.statements:
                res = self.evaluate(statement)
            return res
        elif isinstance(node, WhileStatement):
            condition = self.evaluate(node.condition)
            res = None
            while(self.is_truthy(condition)):
                res = self.evaluate(node.body)
                condition = self.evaluate(node.condition)
            return res
        elif isinstance(node, ReturnStatement):
            if node.value is None:
                res = None
            else:
                res = self.evaluate(node.value)

            raise ReturnException(res)
        elif isinstance(node, FunctionDeclaration):
            name = node.name
            self.environment.define(name, node)
            return None
        elif isinstance(node, FunctionCall):
            function = self.evaluate(node.callee)
            if isinstance(function, BuiltinFunction):
                arguments = [self.evaluate(arg) for arg in node.arguments]
                return function.function(*arguments)


            elif isinstance(function, FunctionDeclaration):
                if len(function.parameters) != len(node.arguments):
                    raise InterpreterError(
                        f"Function '{function.name}' expects "
                        f"{len(function.parameters)} arguments, "
                        f"got {len(node.arguments)}"
                    )
                local_env = Environment(parent=self.environment)
                for parameter, argument in zip(function.parameters, node.arguments):
                    name = parameter.value
                    value = self.evaluate(argument)
                    local_env.define(name, value)
                previous_env = self.environment
                self.environment = local_env

                try:
                    self.evaluate(function.body)
                except ReturnException as e:
                    return e.value
                finally:
                    self.environment = previous_env

                return None
            else:
                if not isinstance(function, FunctionDeclaration):
                    raise InterpreterError("Object is not callable")
        elif isinstance(node, Identifier):
            name = self.environment.get(node.value)
            return name
        elif isinstance(node, ListLiteral):
            lister = []
            for item in node.items:
                lister.append(self.evaluate(item))

            return lister
        elif isinstance(node, IndexExpression):
            index = self.evaluate(node.index)
            obj = self.evaluate(node.obj)
            return obj[index]
        elif isinstance(node, Assignment):
            target = node.identifier

            if isinstance(target, IndexExpression):
                obj = self.evaluate(target.obj)
                index = self.evaluate(target.index)
                value = self.evaluate(node.value)

                obj[index] = value

            elif isinstance(target, Identifier):
                name = target.value
                value = self.evaluate(node.value)

                if self.environment.contains(name):
                    self.environment.set(name, value)
                else:
                    self.environment.define(name, value)

                return value
        elif isinstance(node, ForStatement):
            res = None
            if node.initializer is not None:
                self.evaluate(node.initializer)

            while(node.condition is None
                or self.is_truthy(self.evaluate(node.condition))
            ):

                res = self.evaluate(node.body)
                if node.increment is not None:
                    self.evaluate(node.increment)
            return res
        else:
            raise InterpreterError(f"Undefined node '{node} for now'")
