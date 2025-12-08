# tests/test_interpreter_and_geometry.py

from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter
from src.turtle_core import MockTurtle


def run_with_mock(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    program = parser.parse()
    turtle = MockTurtle()
    interp = Interpreter(turtle)
    interp.execute(program)
    return turtle


def almost_equal(a: float, b: float, eps: float = 1e-6):
    return abs(a - b) < eps


def test_square_returns_near_start_and_heading_zero():
    source = "REPEAT 4 [ FORWARD 100 RIGHT 90 ]"
    turtle = run_with_mock(source)
    state = turtle.get_state()

    # Turtle should be back at or very near origin
    assert almost_equal(state.x, 0.0)
    assert almost_equal(state.y, 0.0)

    # Heading should be equivalent to original (0 degrees) modulo 360
    normalized_heading = state.heading % 360
    assert almost_equal(normalized_heading, 0.0)


def test_forward_and_turn_geometry():
    source = "RIGHT 90 FORWARD 50"
    turtle = run_with_mock(source)
    state = turtle.get_state()

    # Facing south means negative y direction
    assert almost_equal(state.x, 0.0)
    assert almost_equal(state.y, -50.0)
