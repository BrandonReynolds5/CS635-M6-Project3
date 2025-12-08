# CS635 Module 6 Project 3  
Interpreter for a Simplified Turtle Graphics Language

This repository contains the implementation and supporting files for CS635 Module 6 Project 3. The project includes a tokenizer, parser, abstract syntax tree, interpreter, visitors for program analysis, a mock turtle for testing, and integration with the Python turtle framework. A full test suite using the pytest framework is also included.

# Project Members
Leo Paredes, Brandon Reynolds

---

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

### Generating an HTML Test Report
pytest --html=report.html