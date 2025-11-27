import sys
from pathlib import Path

# Ensure src/ is on sys.path so editable installs work without PYTHONPATH.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
