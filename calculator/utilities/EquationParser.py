# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

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
