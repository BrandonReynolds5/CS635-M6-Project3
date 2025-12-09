from .turtle_core import MockTurtle

class MementoVisitor:
    """
    Visitor that executes the program on a turtle and records
    a TurtleState memento after each command.
    """
    def __init__(self, turtle=None):
        # Allow passing any turtle-like object; default to MockTurtle.
        self.turtle = turtle if turtle is not None else MockTurtle()
        # record initial state
        self.mementos = [self.turtle.get_state()]

    def visit_Forward(self, node):
        self.turtle.forward(node.distance)
        self.mementos.append(self.turtle.get_state())

    def visit_Left(self, node):
        self.turtle.left(node.angle)
        self.mementos.append(self.turtle.get_state())

    def visit_Right(self, node):
        self.turtle.right(node.angle)
        self.mementos.append(self.turtle.get_state())

    def visit_PenUp(self, node):
        self.turtle.penup()
        self.mementos.append(self.turtle.get_state())

    def visit_PenDown(self, node):
        self.turtle.pendown()
        self.mementos.append(self.turtle.get_state())

    def visit_Repeat(self, node):
        for _ in range(node.count):
            for stmt in node.body:
                stmt.accept(self)


class DistanceVisitor:
    """
    Visitor that computes total distance traveled (sum of |FORWARD distances|).
    """
    def __init__(self):
        self.total_distance = 0.0

    def visit_Forward(self, node):
        self.total_distance += abs(node.distance)

    def visit_Left(self, node):
        pass

    def visit_Right(self, node):
        pass

    def visit_PenUp(self, node):
        pass

    def visit_PenDown(self, node):
        pass

    def visit_Repeat(self, node):
        for _ in range(node.count):
            for stmt in node.body:
                stmt.accept(self)
