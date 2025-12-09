from .turtle_core import MockTurtle
from .ast_nodes import Forward, Left, Right, PenUp, PenDown, Repeat

# Traverses the AST by executing nodes sequentially on either the real turtle adapter or a mock turtle
class Interpreter:
    """
    Executes AST nodes on a turtle object.
    """
    def __init__(self, turtle=None):
        # allow any turtle-like object; default to MockTurtle
        self.turtle = turtle if turtle is not None else MockTurtle()

    def execute(self, stmts):
        for stmt in stmts:
            self.execute_node(stmt)
    # Execute node based on command given
    def execute_node(self, node):
        if isinstance(node, Forward):
            self.turtle.forward(node.distance)
        elif isinstance(node, Left):
            self.turtle.left(node.angle)
        elif isinstance(node, Right):
            self.turtle.right(node.angle)
        elif isinstance(node, PenUp):
            self.turtle.penup()
        elif isinstance(node, PenDown):
            self.turtle.pendown()
        elif isinstance(node, Repeat):
            for _ in range(node.count):
                for stmt in node.body:
                    self.execute_node(stmt)
        else:
            raise TypeError(f"Unknown node type {type(node)}")
