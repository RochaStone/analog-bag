"""Tests for analog-bag. Run from the repo root: python3 -m unittest"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tarot", ROOT / "launch", ROOT / "week", ROOT / "readback"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
