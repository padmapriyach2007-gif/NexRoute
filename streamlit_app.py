"""
Streamlit Community Cloud Entry Point
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Real-Time Adaptive Navigation System

Ensures working directory is correctly set to project root and delegates execution to app.py.
"""

import sys
import os
import runpy
from pathlib import Path

# Ensure workspace root is in sys.path and set working directory to root
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure current working directory is always the project root
os.chdir(str(ROOT_DIR))

# Execute primary application entrypoint
runpy.run_path(str(ROOT_DIR / "app.py"), run_name="__main__")
