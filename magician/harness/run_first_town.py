#!/usr/bin/env python3
"""Run the Magician first-town route (reuses magician-nes src/play).

    python harness/run_first_town.py --beta1 --no-replay
"""
import subprocess
import sys
from pathlib import Path

MNES = Path.home() / "code" / "games" / "magician-nes"
script = MNES / "src" / "play" / "milestones" / "m1_first_town.py"
raise SystemExit(subprocess.call([sys.executable, str(script)] + sys.argv[1:], cwd=str(MNES)))
