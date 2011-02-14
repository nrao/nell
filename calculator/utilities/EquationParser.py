import compiler, types # WARNING: compiler is deprecated in Python 3k
from functions            import *
from nell.utilities.TimeAgent  import *

def isFunction(dep):
    """
    Checks to see if the dep is a defined function.
    """
    try:
        if isinstance(eval(dep), types.FunctionType):
            return True
    except NameError:
        pass
    return False

class EquationParser(object):
    def __init__(self):
        self.src = ''
        self.deps = ''
        self.deplist = []

    def __call__(self, equation):
        return [dep for dep in compiler.walk(compiler.parse(equation), self).deplist 
                      if not isFunction(dep)]

    def visitName(self,t):
        if t.name != "math" and t.name not in self.deplist:
            self.src += t.name
            self.deps += t.name
            self.deplist.append(t.name) 

    def visitConst(self,t):
        self.src += str(t.value)

    def visitAssName(self, t):
        self.src += t.name + " = "
