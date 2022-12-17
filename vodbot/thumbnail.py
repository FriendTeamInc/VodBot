# based off picauto
# https://gist.github.com/NotQuiteApex/77cdc6c670ec63aff84dd87d672861e5

import subprocess
from os import walk


class PosInf:
    def __init__(self, x,y, s=1):
        self.x = x
        self.y = y
        self.s = s
    
    def __repr__(self):
        return f"PosInf(x={self.x} y={self.y} s={self.s})"
    
    def __str__(self):
        return f"PosInf(x={self.x} y={self.y} s={self.s})"

class HeadInf:
    def __init__(self, name, ox,oy):
        self.name = name
        self.ox = ox
        self.oy = oy
        self.filename = f"heads/{name}.png"
    
    def __repr__(self):
        return f"HeadInf(name={self.name} ox={self.ox} oy={self.oy})"
    
    def __str__(self):
        return f"{self.name}"

class PosHead:
    def __init__(self, pos, head=None):
        self.pos = pos
        self.head = head
    
    def __repr__(self):
        return f"({self.pos},{self.head})"


