# main.py
import sys
from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter
from src.turtle_core import MockTurtle
from src.visitors import MementoVisitor, DistanceVisitor
from src.framework_integration import RealTurtleAdapter


def run_program_text(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    program = parser.parse()

    real = RealTurtleAdapter()
    interp = Interpreter(real)
    interp.execute(program)
    
    # 2) step by step execution using visitors on a fresh turtle
    visitor_turtle = MockTurtle()
    memento_visitor = MementoVisitor(visitor_turtle)
    distance_visitor = DistanceVisitor()

    for stmt in program:
        stmt.accept(memento_visitor)
        stmt.accept(distance_visitor)

    print("Total distance traveled:", distance_visitor.total_distance)
    print("Number of mementos:", len(memento_visitor.mementos))

    # print steps to show stepping
    for i, state in enumerate(memento_visitor.mementos[:5]):
        print(f"Step {i}: {state}")

def run_program_file(filename: str):
    with open(filename) as f:
        source = f.read()
    run_program_text(source)

if __name__ == "__main__":
    
    import turtle
    if len(sys.argv) > 1:
        run_program_file(sys.argv[1])
    else:
        print("No input file. Executing Demo...")
        demo_source = "REPEAT 4 [ FORWARD 100 RIGHT 90 ]"
        run_program_text(demo_source)

    turtle.done()
    
    
