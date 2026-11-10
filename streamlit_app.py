"""
Streamlit Community Cloud Entry Point
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Real-Time Adaptive Navigation System

Ensures working directory and sys.path are correctly configured for both local
and Streamlit Community Cloud environments (/mount/src/<repo>).
"""

import sys
import os
import types
import builtins
from pathlib import Path
import runpy

# Ensure builtins.cur_l is always defined globally across any import or execution context
builtins.cur_l = "en"

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

# Purge cached src submodules so hot reloads on Streamlit Community Cloud pick up fresh code
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith("src."):
        del sys.modules[mod_name]

# Ensure working directory is project root
os.chdir(str(ROOT_DIR))

# Execute main application entrypoint with diagnostic error capture
try:
    runpy.run_path(str(ROOT_DIR / "app.py"), run_name="__main__")
except Exception as e:
    import streamlit as st
    import traceback
    st.error(f"⚠️ Application encountered an issue: {e}")
    with st.expander("🔍 View Error Diagnostics & Traceback", expanded=True):
        st.code(traceback.format_exc(), language="python")
    if st.button("🔄 Reload Pathfinder Application"):
        st.rerun()


