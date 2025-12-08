# tests/conftest.py

import os
import sys

# Absolute path to the project root (the folder that contains src/ and tests/)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
