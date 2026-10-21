"""Level 8 re-fit assembly (2026-10-01): from the replay-exact entry L8_entry_r: knowledge/l8r_prefix.json (Start
mash to the placement + 30 idle), the climb sections knowledge/l4s_L8_r1..7.json (2 idle before each, like
l8.py), 160 idle (arrival animation) -> L8r_arena; the boss section knowledge/l4s_L8r_arena.json if present
(2 idle before it); then l8.py's end-of-level/drop code. Writes logs/pbeam_L8n.json (bookmark L8_entry_r).

    python l8refit.py            (stops after saving L8r_arena when the boss section is missing)
"""
import inspect, json, textwrap
import l8
from toads.emulator import BizHawk, LOGS_DIR, PROJECT

def main():
    e = BizHawk(log_name="l8refit.log")
    e.load("L8_entry_r")
    rec = l8.Rec(e); H = l8.Unwrap()
    def log(s): print(f"[{rec.f}] {s}", flush=True)
    for b in json.load(open("knowledge/l8r_prefix.json")): rec.step(tuple(v for v in b.split("+") if v), 1)
    H(e.ram_all()[0x439], anchor=94)
    for i in range(1, 8):
        p = PROJECT / "knowledge" / f"l4s_L8_r{i}.json"
        if not p.exists(): print("missing section", i); e.close(); return
        rec.step((), 2)
        for b in json.loads(p.read_text()): rec.step(tuple(v for v in b.split("+") if v), 1)
        t = l8.toad(e.ram_all()); log(f"section r{i} -> {t} H {H(t['h'])}")
    e.save("L8r_top"); rec.step((), 160); e.save("L8r_arena")
    boss = PROJECT / "knowledge" / "l4s_L8r_arena.json"
    if not boss.exists(): print("saved L8r_arena; run: L4S_LVL=7 python l4s.py L8r_arena 0 0 300 boss"); e.close(); return
    rec.step((), 2)
    for b in json.loads(boss.read_text()): rec.step(tuple(v for v in b.split("+") if v), 1)
    r = e.ram_all(); log(f"boss: {l8.toad(r)} boss alive {[hex(r[0x3C1+s]) for s in range(2,15) if r[0x3C1+s] == 0x7d]}")
    src = inspect.getsource(l8.run); body = textwrap.dedent(src[src.index("    # the level ends ~440 frames"):src.index("    return rec, H")])
    emu = e; real_save = e.save; e.save = lambda name: real_save("n_" + name)
    exec(body, {**vars(l8), "emu": emu, "rec": rec, "log": log, "toad": l8.toad})
    t = l8.toad(e.ram_all()); print("end", rec.f, t)
    json.dump({"bookmark": "L8_entry_r", "inputs": rec.inputs, "note": json.load(open(LOGS_DIR / "pbeam_L8a.json"))["note"]}, open(LOGS_DIR / "pbeam_L8n.json", "w"))
    e.close()

if __name__ == "__main__":
    main()
