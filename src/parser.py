# parser.py

from .ast_nodes import Forward, Left, Right, PenUp, PenDown, Repeat

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        tok = self.peek()
        if tok is not None:
            self.pos += 1
        return tok

    def parse_number(self):
        tok = self.advance()
        try:
            return float(tok)
        except (TypeError, ValueError):
            raise SyntaxError(f"Expected number, got {tok!r}")

    def parse(self):
        """Parse a full program = list of statements."""
        stmts = []
        while self.peek() is not None:
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        tok = self.advance()
        if tok is None:
            raise SyntaxError("Unexpected end of input")

        upper = tok.upper()

        if upper in ("FORWARD", "FD"):
            distance = self.parse_number()
            return Forward(distance)

        if upper in ("LEFT", "LT"):
            angle = self.parse_number()
            return Left(angle)

        if upper in ("RIGHT", "RT"):
            angle = self.parse_number()
            return Right(angle)

        if upper == "PENUP":
            return PenUp()

        if upper == "PENDOWN":
            return PenDown()

        if upper == "REPEAT":
            count = int(self.parse_number())
            if self.advance() != "[":
                raise SyntaxError("Expected '[' after REPEAT count")
            body = []
            while self.peek() is not None and self.peek() != "]":
                body.append(self.parse_statement())
            if self.advance() != "]":
                raise SyntaxError("Expected ']' to end REPEAT block")
            return Repeat(count, body)

        raise SyntaxError(f"Unknown command {tok!r}")
