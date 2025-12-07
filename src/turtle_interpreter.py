"""
Turtle-language interpreter: parser -> AST -> interpreter
Includes:
 - Tokenizer & Parser
 - AST node classes
 - Interpreter (executes on a turtle-like object)
 - MockTurtle (for tests without graphics)
 - MementoVisitor (captures state snapshots)
 - DistanceVisitor (sums forward distances)
 - CLI: run programs, print actions, mementos, and distance
 - Basic built-in tests runnable with --test

Usage:
  python turtle_interpreter.py --file program.txt
  python turtle_interpreter.py --test

Language supported:
  FORWARD <n> | FD <n>
  LEFT <n>    | LT <n>
  RIGHT <n>   | RT <n>
  PENUP
  PENDOWN
  REPEAT <n> [ <statements> ]

This module is designed to be a single-file reference implementation for
coursework. It emphasizes clear separation (parser, AST, interpreter, visitors,
mock turtle) to demonstrate coupling/cohesion and testability.
"""

from __future__ import annotations
import math
import argparse
import sys
from dataclasses import dataclass
from typing import List, Any, Protocol, Optional
import re

# ---------------------- AST Nodes ----------------------
class Stmt: ...
class Expr: ...

@dataclass
class Number(Expr):
    value: float

@dataclass
class Forward(Stmt):
    distance: Expr

@dataclass
class Left(Stmt):
    angle: Expr

@dataclass
class Right(Stmt):
    angle: Expr

@dataclass
class PenUp(Stmt):
    pass

@dataclass
class PenDown(Stmt):
    pass

@dataclass
class Repeat(Stmt):
    times: int
    body: List[Stmt]

@dataclass
class Program:
    stmts: List[Stmt]

# ---------------------- Tokenizer & Parser ----------------------
_TOKEN_SIMPLE = re.compile(r"\d+|[A-Za-z]+|\[|\]")

class Token:
    def __init__(self, typ: str, val: Any):
        self.typ = typ
        self.val = val
    def __repr__(self) -> str:
        return f"Token({self.typ},{self.val})"

def tokenize(source: str) -> List[Token]:
    parts = _TOKEN_SIMPLE.findall(source)
    tokens: List[Token] = []
    for p in parts:
        if p.isdigit():
            tokens.append(Token('NUM', int(p)))
        elif p == '[' or p == ']':
            tokens.append(Token(p, p))
        else:
            tokens.append(Token('WORD', p.upper()))
    tokens.append(Token('EOF', None))
    return tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
    def peek(self) -> Token:
        return self.tokens[self.i]
    def consume(self, expected: Optional[str] = None) -> Token:
        tok = self.tokens[self.i]
        if expected and tok.typ != expected and tok.val != expected:
            raise SyntaxError(f"Expected {expected} but got {tok}")
        self.i += 1
        return tok
    def parse_number_expr(self) -> Number:
        tok = self.peek()
        if tok.typ == 'NUM':
            self.consume('NUM')
            return Number(float(tok.val))
        raise SyntaxError(f"Expected number but got {tok}")
    def parse_stmt(self) -> Stmt:
        tok = self.peek()
        if tok.typ != 'WORD':
            raise SyntaxError(f"Unexpected token {tok}")
        kw = tok.val
        self.consume('WORD')
        if kw in ('FORWARD','FD'):
            num = self.parse_number_expr()
            return Forward(num)
        if kw in ('LEFT','LT'):
            num = self.parse_number_expr()
            return Left(num)
        if kw in ('RIGHT','RT'):
            num = self.parse_number_expr()
            return Right(num)
        if kw == 'PENUP':
            return PenUp()
        if kw == 'PENDOWN':
            return PenDown()
        if kw == 'REPEAT':
            t = self.consume('NUM')
            times = int(t.val)
            self.consume('[')
            body: List[Stmt] = []
            while self.peek().typ != ']':
                body.append(self.parse_stmt())
            self.consume(']')
            return Repeat(times, body)
        raise SyntaxError(f"Unknown keyword {kw}")
    def parse(self) -> Program:
        stmts: List[Stmt] = []
        while self.peek().typ != 'EOF':
            stmts.append(self.parse_stmt())
        return Program(stmts)

def parse_program(text: str) -> Program:
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()

# ---------------------- Mock Turtle ----------------------
@dataclass
class TurtleState:
    x: float
    y: float
    heading_deg: float  # 0 = east, 90 = north
    pen_down: bool

class MockTurtle:
    """A simple mock turtle that records actions and state snapshots.
    Methods mirror a real turtle-like API: forward, left, right, penup, pendown.
    """
    def __init__(self) -> None:
        self.state = TurtleState(0.0, 0.0, 0.0, True)
        self.actions: List[Any] = []
    def forward(self, dist: float) -> None:
        rad = math.radians(self.state.heading_deg)
        dx = math.cos(rad) * dist
        dy = math.sin(rad) * dist
        old = (self.state.x, self.state.y)
        self.state.x += dx
        self.state.y += dy
        self.actions.append(('forward', float(dist), old, (self.state.x, self.state.y)))
    def left(self, angle: float) -> None:
        self.state.heading_deg = (self.state.heading_deg + angle) % 360
        self.actions.append(('left', float(angle), self.state.heading_deg))
    def right(self, angle: float) -> None:
        self.state.heading_deg = (self.state.heading_deg - angle) % 360
        self.actions.append(('right', float(angle), self.state.heading_deg))
    def penup(self) -> None:
        self.state.pen_down = False
        self.actions.append(('penup',))
    def pendown(self) -> None:
        self.state.pen_down = True
        self.actions.append(('pendown',))
    def get_state(self) -> TurtleState:
        return TurtleState(self.state.x, self.state.y, self.state.heading_deg, self.state.pen_down)

# ---------------------- Interpreter ----------------------
class Interpreter:
    """Executes a Program AST against a turtle-like object (duck-typed)."""
    def __init__(self, turtle: Any) -> None:
        self.turtle = turtle
    def eval_expr(self, e: Expr) -> float:
        if isinstance(e, Number):
            return e.value
        raise RuntimeError('Unknown expression type')
    def exec_stmt(self, s: Stmt) -> None:
        if isinstance(s, Forward):
            d = self.eval_expr(s.distance)
            self.turtle.forward(d)
        elif isinstance(s, Left):
            a = self.eval_expr(s.angle)
            self.turtle.left(a)
        elif isinstance(s, Right):
            a = self.eval_expr(s.angle)
            self.turtle.right(a)
        elif isinstance(s, PenUp):
            self.turtle.penup()
        elif isinstance(s, PenDown):
            self.turtle.pendown()
        elif isinstance(s, Repeat):
            for _ in range(s.times):
                for st in s.body:
                    self.exec_stmt(st)
        else:
            raise RuntimeError('Unknown statement type')
    def run(self, program: Program) -> None:
        for st in program.stmts:
            self.exec_stmt(st)

# ---------------------- Visitors ----------------------
@dataclass
class Memento:
    x: float
    y: float
    heading: float
    pen_down: bool
    action: str
    value: Any

class MementoVisitor:
    """Traverse a Program and capture a Memento after every step.

    The visitor uses its own internal MockTurtle to simulate state changes so
    captured mementos are deterministic and independent of an external drawing API.
    """
    def __init__(self) -> None:
        self.mementos: List[Memento] = []
        self.turtle = MockTurtle()
        # initial memento
        self._capture('init', None)
    def _capture(self, action: str, value: Any) -> None:
        s = self.turtle.get_state()
        self.mementos.append(Memento(s.x, s.y, s.heading_deg, s.pen_down, action, value))
    def visit_program(self, program: Program) -> None:
        for st in program.stmts:
            self.visit_stmt(st)
    def visit_stmt(self, s: Stmt) -> None:
        if isinstance(s, Forward):
            self.visit_forward(s)
        elif isinstance(s, Left):
            self.visit_left(s)
        elif isinstance(s, Right):
            self.visit_right(s)
        elif isinstance(s, PenUp):
            self.visit_penup(s)
        elif isinstance(s, PenDown):
            self.visit_pendown(s)
        elif isinstance(s, Repeat):
            self.visit_repeat(s)
        else:
            raise RuntimeError('Unknown stmt in visitor')
    def visit_forward(self, node: Forward) -> None:
        d = node.distance.value
        self.turtle.forward(d)
        self._capture('forward', d)
    def visit_left(self, node: Left) -> None:
        a = node.angle.value
        self.turtle.left(a)
        self._capture('left', a)
    def visit_right(self, node: Right) -> None:
        a = node.angle.value
        self.turtle.right(a)
        self._capture('right', a)
    def visit_penup(self, node: PenUp) -> None:
        self.turtle.penup()
        self._capture('penup', None)
    def visit_pendown(self, node: PenDown) -> None:
        self.turtle.pendown()
        self._capture('pendown', None)
    def visit_repeat(self, node: Repeat) -> None:
        for _ in range(node.times):
            for st in node.body:
                self.visit_stmt(st)

class DistanceVisitor:
    """Calculate total distance traveled (sum of absolute forward distances).

    This counts each FORWARD command's distance literally, including repeated
    ones. Turning doesn't add to distance.
    """
    def __init__(self) -> None:
        self.total: float = 0.0
    def visit_program(self, program: Program) -> None:
        for st in program.stmts:
            self.visit_stmt(st)
    def visit_stmt(self, s: Stmt) -> None:
        if isinstance(s, Forward):
            self.visit_forward(s)
        elif isinstance(s, Repeat):
            self.visit_repeat(s)
        elif isinstance(s, Left) or isinstance(s, Right) or isinstance(s, PenUp) or isinstance(s, PenDown):
            return
        else:
            raise RuntimeError('Unknown stmt in distance visitor')
    def visit_forward(self, node: Forward) -> None:
        self.total += abs(node.distance.value)
    def visit_repeat(self, node: Repeat) -> None:
        for _ in range(node.times):
            for st in node.body:
                self.visit_stmt(st)

# ---------------------- CLI & Tests ----------------------

def run_file(path: str) -> int:
    with open(path, 'r') as f:
        src = f.read()
    program = parse_program(src)
    mock = MockTurtle()
    interp = Interpreter(mock)
    interp.run(program)
    # print actions
    print('Actions:')
    for a in mock.actions:
        print(' ', a)
    # mementos
    mv = MementoVisitor()
    mv.visit_program(program)
    print('\nMementos:')
    for i, m in enumerate(mv.mementos):
        print(f' {i}:', m)
    dv = DistanceVisitor()
    dv.visit_program(program)
    print(f'\nTotal distance (DistanceVisitor): {dv.total}')
    return 0

# Basic internal test-suite
def _test_parser_and_interpreter() -> None:
    # small set of unit-like assertions
    prog_text = 'FD 10 RT 90 FD 10'
    p = parse_program(prog_text)
    assert isinstance(p, Program)
    mock = MockTurtle()
    Interpreter(mock).run(p)
    # two forwards
    fw_actions = [a for a in mock.actions if a[0] == 'forward']
    assert len(fw_actions) == 2
    assert abs(fw_actions[0][1] - 10.0) < 1e-9

    # repeat semantics
    prog_text = 'REPEAT 3 [ FD 5 RT 10 ]'
    p = parse_program(prog_text)
    mock = MockTurtle()
    Interpreter(mock).run(p)
    fw_actions = [a for a in mock.actions if a[0] == 'forward']
    assert len(fw_actions) == 3

    # visitors
    demo = 'REPEAT 4 [ FORWARD 100 RIGHT 90 ] LEFT 45 FORWARD 141 PENUP FORWARD 10 PENDOWN'
    p = parse_program(demo)
    dv = DistanceVisitor(); dv.visit_program(p)
    expected = 4 * 100 + 141 + 10
    assert abs(dv.total - expected) < 1e-9

    mv = MementoVisitor(); mv.visit_program(p)
    # first memento is init
    assert mv.mementos and mv.mementos[0].action == 'init'

    print('All internal tests passed.')

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='Turtle language interpreter (single-file).')
    parser.add_argument('--file', '-f', help='Program file to run')
    parser.add_argument('--test', action='store_true', help='Run built-in tests')
    args = parser.parse_args(argv)
    if args.test:
        _test_parser_and_interpreter()
        return 0
    if args.file:
        return run_file(args.file)
    parser.print_help()
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
