from src.lexer import tokenize

# Simple tokenize test
def test_tokenize_simple_program():
    source = "PENDOWN FORWARD 100 RIGHT 90"
    tokens = tokenize(source)
    assert tokens == ["PENDOWN", "FORWARD", "100", "RIGHT", "90"]

# Advanved tokenize test with order
def test_tokenize_with_brackets_and_newlines():
    source = """
    REPEAT 4 [ 
        FORWARD 50
        RIGHT 90
    ]
    """
    tokens = tokenize(source)
    # Test for order since order matters but whitespace and newlines should not
    assert tokens == [
        "REPEAT", "4", "[",
        "FORWARD", "50",
        "RIGHT", "90",
        "]",
    ]
