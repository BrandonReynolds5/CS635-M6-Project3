class Node:
    def accept(self, visitor):
        """Visitor pattern: call visitor.visit_<ClassName>(self)."""
        method_name = "visit_" + self.__class__.__name__
        method = getattr(visitor, method_name)
        return method(self)

# Moves forward
class Forward(Node):
    def __init__(self, distance: float):
        self.distance = distance

# Accepts angle to turn left
class Left(Node):
    def __init__(self, angle: float):
        self.angle = angle

# Accepts angle to turn right
class Right(Node):
    def __init__(self, angle: float):
        self.angle = angle

# Lifts pen up 
class PenUp(Node):
    pass

# Puts pen down
class PenDown(Node):
    pass


class Repeat(Node):
    def __init__(self, count: int, body):
        self.count = count   # int
        self.body = body     # list[Node]
