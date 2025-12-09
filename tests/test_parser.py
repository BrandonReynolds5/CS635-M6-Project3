from src.lexer import tokenize
from src.parser import Parser
from src.ast_nodes import Forward, Left, Right, PenUp, PenDown, Repeat

# Test for parsing
def parse_program(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()

# Test for parsing with forward
def test_parse_single_forward():
    program = parse_program("FORWARD 100")
    assert len(program) == 1
    stmt = program[0]
    assert isinstance(stmt, Forward)
    assert stmt.distance == 100.0

# Test for parsing with repeat
def test_parse_repeat_block():
    source = "REPEAT 4 [ FORWARD 50 RIGHT 90 ]"
    program = parse_program(source)
    assert len(program) == 1

    repeat = program[0]
    assert isinstance(repeat, Repeat)
    assert repeat.count == 4

    # Body should have two commands inside
    assert len(repeat.body) == 2
    assert isinstance(repeat.body[0], Forward)
    assert isinstance(repeat.body[1], Right)
    assert repeat.body[0].distance == 50.0
    assert repeat.body[1].angle == 90.0
