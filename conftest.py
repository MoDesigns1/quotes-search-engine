import sys
import os

# make sure the repo root is on the path so "from src.x import ..." works
# regardless of where pytest is invoked from
sys.path.insert(0, os.path.dirname(__file__))
