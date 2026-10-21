"""Replay a segment from its bookmark and dump the RAM after every input: logs/fix/l13z_full_<seg>.bin"""
import json, sys
import l13z_beam as zb
from toads.emulator import LOGS_DIR
e = zb.Emu(log_name="l13z_dump.log")
for seg in sys.argv[1:]:
    j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    e.load(j["bookmark"])
    out = open(LOGS_DIR / "fix" / f"l13z_full_{seg}.bin", "wb")
    prev = None
    for n, b in enumerate(j["inputs"], 1):
        e.step(tuple(v for v in b.split("+") if v), 1)
        r = e.ram_all(); out.write(r)
        if r[0x10] != prev:
            print(seg, "input", n, "level", prev, "->", r[0x10], "0B", r[0x0B], "0C", r[0x0C], flush=True); prev = r[0x10]
    out.close()
e.close()
