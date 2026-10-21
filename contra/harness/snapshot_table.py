"""chain2: write SNAPSHOT.md = size / sha1 / mtime of every code and data file the chain runs, against the live folder.

    python snapshot_table.py "<taken at>"
"""
import hashlib
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent
NOTES = {
    "contra/emulator.py": "PATCHED: `BIZHAWK_DIR` is an explicit path (PROJECT resolves to chain2, so ROM, bridge.lua, "
                          "states/, logs/, shots/, knowledge/, emu_tmp/ are all chain2's own); original = `emulator.py.snap0`",
    "logs/s1/s1_w0v3_full.inputs.txt": "stage 1, title_wait 0, rule v2 (verified list; chain A's stage 1)",
    "states/s1/s2_start_legal_v3.State": "stage 2's first frame of the w0v3 list (the chain makes its own from a replay)",
}


def sha1(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


def files():
    out = [Path("Contra (USA).nes"), Path("bridge.lua"), Path("assemble.py"), Path("check_inputs.py")]
    out += sorted(p.relative_to(HERE) for p in (HERE / "contra").rglob("*.py"))
    for t in ("s2_solve.py", "s6_solve.py", "s1_open.py", "s1_finish.py", "s5_finish.py", "s2_verify.py"):
        out.append(Path("tools") / t)
    out += sorted(p.relative_to(HERE) for p in (HERE / "knowledge").glob("*.json"))
    out += [Path("logs/s1/s1_w0v3_full.inputs.txt"), Path("logs/s1/s1_w1v3_full.inputs.txt"),
            Path("logs/s1/s1_w37v3_full.inputs.txt"), Path("states/s1/s2_start_legal_v3.State")]
    return out


def main():
    taken = sys.argv[1] if len(sys.argv) > 1 else "?"
    lines = [f"# chain2 snapshot - what code this folder runs", "",
             f"Taken {taken} (local) from `` by `cp -rp` (root files, `contra/`, `tools/`, "
             f"`knowledge/`, `states/s1/`, the stage 1 openings and rule v2 lists in `logs/s1/`); this table written "
             f"{time.strftime('%Y-%m-%d %H:%M:%S')}. \"against the live folder\" compares with the live file at the time "
             f"this table was written. Fixes made for the chain are in `FIXES.md`; a changed file keeps the snapshot's "
             f"original next to it as `<name>.snap0`.", "",
             "Every `contra/stages/*.py` that the chain runs compiled and imported in the snapshot (s1..s8, s7b, s6run, "
             "base_room3, base_fight3, base_plan3, base_eye, s3s8_fight, s5_ufo_sim).", "",
             "| file | bytes | sha1 | mtime | against the live folder | note |", "|---|---|---|---|---|---|"]
    for rel in files():
        p = HERE / rel
        if not p.exists():
            continue
        lp = LIVE / rel
        if not lp.exists():
            cmp = "not in live"
        else:
            cmp = "same as live now" if sha1(lp) == sha1(p) else "DIFFERS from live now"
        st = p.stat()
        lines.append(f"| `{rel.as_posix()}` | {st.st_size} | `{sha1(p)}` | "
                     f"{time.strftime('%m-%d %H:%M:%S', time.localtime(st.st_mtime))} | {cmp} | {NOTES.get(rel.as_posix(), '')} |")
    lines += ["", "chain2's own files: `chain.py` (from chain1's, see its docstring), `run_s67.py` (chain1's, history "
              "tail 2,000 rows), `finish.py`, `clock_shots.py`, `snapshot_table.py`."]
    (HERE / "SNAPSHOT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-12:]))


if __name__ == "__main__":
    main()
