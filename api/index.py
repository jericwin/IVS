import os
import sys

# Add the project root to the python path so the api/index.py can import the main app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app
