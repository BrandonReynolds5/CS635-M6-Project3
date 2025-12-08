# turtle_core.py

import math
from dataclasses import dataclass

@dataclass
class TurtleState:
    x: float
    y: float
    heading: float   # degrees
    pen_down: bool

class MockTurtle:
    """
    Mock version of a turtle: keeps track of state and movement math,
    but does not draw anything.
    """
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0    # 0 degrees = east
        self.pen_down = True

    def forward(self, distance: float):
        rad = math.radians(self.heading)
        self.x += math.cos(rad) * distance
        self.y += math.sin(rad) * distance

    def left(self, angle: float):
        self.heading += angle

    def right(self, angle: float):
        self.heading -= angle

    def penup(self):
        self.pen_down = False

    def pendown(self):
        self.pen_down = True

    def get_state(self) -> TurtleState:
        return TurtleState(self.x, self.y, self.heading, self.pen_down)
