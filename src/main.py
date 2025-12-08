# main.py
import sys
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter
from .turtle_core import MockTurtle
from .visitors import MementoVisitor, DistanceVisitor
from .framework_integration import RealTurtleAdapter


def run_program_text(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    program = parser.parse()

    # 1) Normal execution on a mock turtle
    # mock = MockTurtle()
    # interp = Interpreter(mock)
    # interp.execute(program)
    # print("Final turtle state:", mock.get_state())
    real = RealTurtleAdapter()
    interp = Interpreter(real)
    interp.execute(program)
    # print("Final turtle state:", real.get_state())

    # 2) Step-by-step execution using visitors on a fresh turtle
    visitor_turtle = MockTurtle()
    memento_visitor = MementoVisitor(visitor_turtle)
    distance_visitor = DistanceVisitor()

    for stmt in program:
        stmt.accept(memento_visitor)
        stmt.accept(distance_visitor)

    print("Total distance traveled:", distance_visitor.total_distance)
    print("Number of mementos:", len(memento_visitor.mementos))

    # Print a few steps to show "stepping"
    for i, state in enumerate(memento_visitor.mementos[:5]):
        print(f"Step {i}: {state}")

def run_program_file(filename: str):
    with open(filename) as f:
        source = f.read()
    run_program_text(source)

if __name__ == "__main__":
    #   python main.py program.txt 
    import turtle
    if len(sys.argv) > 1:
        run_program_file(sys.argv[1])
    else:
        print("No input file. Executing Demo...")
        demo_source = "REPEAT 4 [ FORWARD 100 RIGHT 90 ]"
        run_program_text(demo_source)

    turtle.done()
    
    
