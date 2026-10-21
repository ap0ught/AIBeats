"""One-off patch (kept for the record): lost-press compensation in emulator.run / resync.play / repair_stage."""
import os
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# ---------------- emulator.py: run(..., comp=True)
p = root / "contra" / "emulator.py"
s = p.read_text(encoding="utf-8")
a = '''    def press(self, *buttons: str, hold: int = 1, release: int = 1) -> State:'''
b = '''    def run_comp(self, rows: Sequence[Iterable[str]], chunk: int = 2000, pad_addr: int = 0xF1, carry: int = 0):
        """Like run(), with lost-press compensation (bridge command stepc): a button that was sent but that the
        game's own controller byte does not show after the frame (NesHawk's DMC/controller conflict made the game
        reuse the previous frame's read) is pressed again on the next frame. Returns (last state, rows really
        sent, carry mask left over). self.inputs gets the rows really sent, so the log replays open-loop."""
        from .inputs import from_mask
        rows = [tuple(r) for r in rows]
        s = None
        tr = []
        sent_all = []
        for i in range(0, len(rows), chunk):
            part = rows[i:i + chunk]
            resp = self.cmd(f"stepc {pad_addr} {carry} " + to_hex(part))
            hx, c, rest = resp.split("|", 2)
            carry = int(c)
            sent = [from_mask(int(hx[k:k + 2], 16)) for k in range(0, len(hx), 2)]
            sent_all.extend(sent)
            self.inputs.extend(sent)
            if self.record or getattr(self, "_trace", False):
                lines = rest.split(";")
                if self.record:
                    self.trace_lines.extend(lines)
                tr.extend(State.parse(l) for l in lines)
                s = tr[-1]
            else:
                s = State.parse(rest)
        self.last_trace = tr
        return (s if s is not None else self.state()), sent_all, carry

    def press(self, *buttons: str, hold: int = 1, release: int = 1) -> State:'''
assert a in s
s = s.replace(a, b)
tmp = p.with_name("emulator.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("emulator.py.backup"))
os.replace(tmp, p)

# ---------------- resync.py
p = root / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")


def rep(a, b, count=1):
    global s
    assert s.count(a) >= 1, a[:70]
    s = s.replace(a, b) if count == 0 else s.replace(a, b, count)


rep('''         stop_on_death: bool = True, stop_on_level: bool = True, stall: int = 0) -> Result:''',
    '''         stop_on_death: bool = True, stop_on_level: bool = True, stall: int = 0, comp: bool = True) -> Result:''')
rep('''    for i in range(0, len(rows), chunk):
        emu.run(rows[i:i + chunk], chunk=chunk)
        tr = emu.last_trace''',
    '''    sent_rows = []
    carry = 0
    for i in range(0, len(rows), chunk):
        if comp:
            _, sent, carry = emu.run_comp(rows[i:i + chunk], chunk=chunk, carry=carry)
            sent_rows.extend(sent)
        else:
            emu.run(rows[i:i + chunk], chunk=chunk)
            sent_rows.extend(rows[i:i + chunk])
        tr = emu.last_trace''')
rep('''    res.last_gain = last_gain
    return res''', '''    res.last_gain = last_gain
    res.sent = sent_rows[:n]              # what was really sent for the frames up to the stop (lost presses repeated)
    return res''')
# repair: when the stage is done, the rows kept are the rows really sent in one pass from the stage state
rep('''        if r.reason in ("level", "end"):
            rows = rows[:D]
            save(True, D)
            log(f"[{out}] DONE: {D} frames from the stage state, {len(edits)} edits: {edits}")
            return True, rows, edits''',
    '''        if r.reason in ("level", "end"):
            # one pass from the stage state: keep what was really sent (lost presses repeated a frame later),
            # which replays open-loop. If that pass does not finish (a carry at a checkpoint edge), go on repairing.
            full = play(e0, state, rows, stall=stall)
            if full.reason not in ("level", "end"):
                log(f"[{out}]    full pass from the stage state differs from the checkpointed one: {full}")
                ck.clear()
                ck[0] = state
                continue
            D = full.frames
            n_comp = sum(1 for a, b in zip(full.sent, rows) if tuple(a) != tuple(b))
            rows = [tuple(x) for x in full.sent]
            check = play(e0, state, rows, stall=stall, comp=False)
            if check.reason not in ("level", "end") or check.frames != D:
                log(f"[{out}]    open-loop check of the kept rows FAILED: {check}")
                return False, rows, edits
            meta = dict(meta or {})
            meta["lost_presses_repeated"] = n_comp
            save(True, D)
            log(f"[{out}] DONE: {D} frames from the stage state, {len(edits)} edits, {n_comp} rows changed by "
                f"lost-press compensation: {edits}")
            return True, rows, edits''')
tmp = p.with_name("resync.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup4"))
os.replace(tmp, p)
print("patched")
