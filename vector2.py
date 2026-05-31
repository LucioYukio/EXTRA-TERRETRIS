import math

class Vector2:
    def __init__(self, x : float = 0, y : float = 0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        length = self.length()
        if length == 0: return
        self.x /= length
        self.y /= length

    def copy(self):
        return Vector2(self.x, self.y)
        
        
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"
