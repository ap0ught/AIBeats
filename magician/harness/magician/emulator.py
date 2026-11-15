"""Thin wrapper: launch magician-nes milestones / play harness."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

MNES = Path.home() / "code" / "games" / "magician-nes"

def run_milestone(name: str, *args: str) -> int:
    script = MNES / "src" / "play" / "milestones" / f"{name}.py"
    return subprocess.call([sys.executable, str(script), *args], cwd=str(MNES))
