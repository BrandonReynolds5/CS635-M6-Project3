# tests/test_visitors.py

from src.lexer import tokenize
from src.parser import Parser
from src.turtle_core import MockTurtle
from src.visitors import MementoVisitor, DistanceVisitor


def build_program(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()


def almost_equal(a: float, b: float, eps: float = 1e-6):
    return abs(a - b) < eps


def test_distance_visitor_square():
    source = "REPEAT 4 [ FORWARD 100 RIGHT 90 ]"
    program = build_program(source)

    visitor = DistanceVisitor()
    for stmt in program:
        stmt.accept(visitor)

    # Four sides of length 100
    assert visitor.total_distance == 400.0


def test_memento_visitor_steps():
    source = "FORWARD 50 RIGHT 90 FORWARD 50"
    program = build_program(source)

    turtle = MockTurtle()
    visitor = MementoVisitor(turtle)

    for stmt in program:
        stmt.accept(visitor)

    # Initial state plus three commands
    assert len(visitor.mementos) == 4

    first = visitor.mementos[0]
    second = visitor.mementos[1]
    third = visitor.mementos[2]
    fourth = visitor.mementos[3]

    # Initial state
    assert almost_equal(first.x, 0.0)
    assert almost_equal(first.y, 0.0)
    assert almost_equal(first.heading, 0.0)

    # After first forward: moved along +x
    assert almost_equal(second.x, 50.0)
    assert almost_equal(second.y, 0.0)

    # After right turn: heading changed, position same
    assert almost_equal(third.x, 50.0)
    assert almost_equal(third.y, 0.0)
    assert almost_equal(third.heading, -90.0)

    # After second forward: move along negative y
    assert almost_equal(fourth.x, 50.0)
    assert almost_equal(fourth.y, -50.0)
