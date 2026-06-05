import math

def lerp(a, b, x):
    return a + x * (b - a)

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
        
    def look_at(self, point):
        if isinstance(point, Vector2):
            return Vector2(
                point.x - self.x,
                point.y - self.y
            )
        else:
            return Vector2()
    
    def lerp(self, point, amount: float):
        if isinstance(point, Vector2):
            vector2 = self.copy()
            vector2.x = lerp(vector2.x, point.x, amount)
            vector2.y = lerp(vector2.y, point.y, amount)
            return vector2
        else:
            return self.copy()
    
    def __add__(self, vector2):
        if isinstance(vector2, Vector2):
            vector = Vector2(
            self.x + vector2.x,
            self.y + vector2.y
            )
            return vector
        else:
            return self.copy()
    
    def __sub__(self, vector2):
        if isinstance(vector2, Vector2):
            vector = Vector2(
            self.x - vector2.x,
            self.y - vector2.y
            )
            return vector
        else:
            return self.copy()
    
    def __mul__(self, scalar: int | float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"
