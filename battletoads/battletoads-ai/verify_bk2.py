"""Play a .bk2 hands-off in a fresh EmuHawk (private config, no bridge, no joypad calls) and print the RAM sha1 at a frame.

    python verify_bk2.py <movie.bk2> <frame> [expected sha1]

Uses verify_movie.lua. The core is the one named in the movie's header."""
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from toads.emulator import BIZHAWK_DIR, EMUHAWK, PROJECT, ROM

movie, frame = Path(sys.argv[1]).resolve(), int(sys.argv[2])
want = sys.argv[3] if len(sys.argv) > 3 else None
d = PROJECT / "emu_tmp" / f"{os.getpid()}_{uuid.uuid4().hex[:8]}"
d.mkdir(parents=True, exist_ok=True)
conf = json.loads((BIZHAWK_DIR / "config.ini").read_text(encoding="utf-8-sig"))
if "Rewind" in conf:
    conf["Rewind"]["Enabled"] = False
cfg = d / "config.ini"
cfg.write_text(json.dumps(conf, indent=1), encoding="utf-8")
out = d / "end.ram"
lua = Path(__file__).resolve().parent / "verify_movie.lua"
p = subprocess.run([str(EMUHAWK), f"--config={cfg}", f"--lua={lua}", f"--userdata=frames:{frame};out:{out}",
                    f"--movie={movie}", str(ROM)], cwd=str(BIZHAWK_DIR), timeout=1800)
sha = hashlib.sha1(out.read_bytes()).hexdigest() if out.exists() else None
print(f"{movie.name}: RAM sha1 at movie frame {frame}: {sha}" + (f"  ({'MATCH' if sha == want else 'MISMATCH'} with {want})" if want else ""))
