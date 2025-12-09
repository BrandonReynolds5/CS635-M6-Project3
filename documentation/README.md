# CS635 Module 6 Project 3  
Interpreter for a Simplified Turtle Graphics Language

This repository contains the implementation and supporting files for CS635 Module 6 Project 3. The project includes a tokenizer, parser, abstract syntax tree, interpreter, visitors for program analysis, a mock turtle for testing, and integration with the Python turtle framework. A full test suite using the pytest framework is also included.

# Project Members
Leo Paredes, Brandon Reynolds

---
## Running the Interpreter

You can run the interpreter from the root directory by passing a turtle program file as a command line argument. All turtle programs can be found in the 'turtle_programs' directory. 

## Running the Interpreter using the GUI

You can run the interpreter with a custom gui as well. This gui will allow you to load in text files with the commands to help navigate their turtle. The GUI serves multiple purposes such as:
- Code editor (Load/Save)
- Execution Controls
- Turtle Canvas for turtle graphics
- Execution Info Panel
- Export functionality with PNG images

### Basic Usage

Command Line:
python main.py <turtle_program>

GUI:
python gui.py

### Example
python main.py turtle_programs/square.txt

### Running Without Arguments 
If you run the interpreter through command line without providing a program file, a simple demo program will be executed automatically. 

## Running the Test Suite

Follow the steps below to set up the virtual environment and run the tests. All commands should be executed from the project root directory:

### 1. Create a virtual environment  
python -m venv .venv

### 2. Activate the virtual environment  
Windows: .venv\Scripts\activate
Mac or Linux: source .venv/bin/activate

### 3. Install dependencies 
pip install pytest  

### 4. Run the tests
pytest -v

### Generating a HTML Test Report
pytest --html=report.html