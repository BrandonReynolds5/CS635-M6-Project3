from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter
from src.turtle_core import MockTurtle

# Test that mock works
def run_with_mock(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    program = parser.parse()
    turtle = MockTurtle()
    interp = Interpreter(turtle)
    interp.execute(program)
    return turtle

# Test almost equal
def almost_equal(a: float, b: float, eps: float = 1e-6):
    return abs(a - b) < eps

# Test that square returns back correctly
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

# Test for moving forward and turning
def test_forward_and_turn_geometry():
    source = "RIGHT 90 FORWARD 50"
    turtle = run_with_mock(source)
    state = turtle.get_state()

    # Facing south means negative y direction
    assert almost_equal(state.x, 0.0)
    assert almost_equal(state.y, -50.0)
