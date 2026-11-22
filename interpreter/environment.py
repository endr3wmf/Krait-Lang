from Errors import *


class Environment:

    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def __repr__(self):
        return f"Environment({self.variables})"
    def define(self, name, value):
        self.variables[name] = value
        return self
    def get(self, name):
        if name not in self.variables:
            if self.parent is not None:
                return self.parent.get(name)
            else:
                raise InterpreterError(f"Undefined variable '{name}'")
        return self.variables[name]
    def set(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        else:
            if self.parent is not None:
                self.parent.set(name, value)
            else:
                raise InterpreterError(f"Could not set '{name}'")
    def contains(self, name):
        return name in self.variables

