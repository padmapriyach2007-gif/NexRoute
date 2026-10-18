"""
Streamlit Community Cloud Entry Point
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Real-Time Adaptive Navigation System

Ensures working directory and sys.path are correctly configured for both local
and Streamlit Community Cloud environments (/mount/src/<repo>).
"""

import sys
import os
import types
from pathlib import Path
import runpy

# Determine absolute path to the project root and src directory
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

# Prepend project root and src to sys.path
for p in [str(ROOT_DIR), str(SRC_DIR)]:
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

# Fix for Streamlit Cloud (/mount/src/<repo>):
# If Python imports or creates a namespace package for /mount/src,
# ensure 'src' always resolves to this repository's src package.
if "src" in sys.modules:
    src_mod = sys.modules["src"]
    if not hasattr(src_mod, "__file__") or src_mod.__file__ is None:
        if hasattr(src_mod, "__path__"):
            src_mod.__path__.insert(0, str(SRC_DIR))
else:
    # Pre-register src package pointing directly to SRC_DIR
    src_pkg = types.ModuleType("src")
    src_pkg.__file__ = str(SRC_DIR / "__init__.py")
    src_pkg.__path__ = [str(SRC_DIR)]
    src_pkg.__package__ = "src"
    sys.modules["src"] = src_pkg

# Ensure working directory is project root
os.chdir(str(ROOT_DIR))

# Execute main application entrypoint
runpy.run_path(str(ROOT_DIR / "app.py"), run_name="__main__")

