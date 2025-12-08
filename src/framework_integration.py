# real turtle adapter
# framework_integration.py

import turtle
from dataclasses import dataclass

@dataclass
class RealTurtleState:
    x: float
    y: float
    heading: float
    pen_down: bool

class RealTurtleAdapter:
    """
    Adapter that wraps the real turtle.Turtle so it can be used
    with Interpreter and Visitors like the MockTurtle.
    """
    def __init__(self):
        self.t = turtle.Turtle()
        self.pen_is_down = True

    def forward(self, distance: float):
        self.t.forward(distance)

    def left(self, angle: float):
        self.t.left(angle)

    def right(self, angle: float):
        self.t.right(angle)

    def penup(self):
        self.t.penup()
        self.pen_is_down = False

    def pendown(self):
        self.t.pendown()
        self.pen_is_down = True

    def get_state(self) -> RealTurtleState:
        x, y = self.t.position()
        heading = self.t.heading()
        return RealTurtleState(x, y, heading, self.pen_is_down)
