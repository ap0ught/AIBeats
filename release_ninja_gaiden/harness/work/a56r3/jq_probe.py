"""Round 3: Jaquio motion / hit geometry probe (research). Jaquio's AI (bank07 $D357) is deterministic:
enters at x $C0 y $60, paces between x $30 and $D0 at 1.5 px/f, fires two homing fireballs every $78 frames.
This probe logs, from our 6-4b control state:
  (1) Jaquio (slot 7) x/y and Ryu with no input for 330 frames;
  (2) Ryu standing still + jumping straight up repeatedly with the legal cancel cycle at several x spots: hits.
"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa

START = sys.argv[1] if len(sys.argv) > 1 else "tmp/a56r2_64b_control"
CYC = [("Down",), ("Down", "B"), ("B",), (), ()]

e = C.open_emu("a56r3_probe.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    F = dict(e.fields)
    F.update(jx=0x467, jy=0x487, jid=0x407, jhp=0x497, js=0x4A7 if False else 0x467,
             f0id=0x400, f1id=0x401, f2id=0x402, f0x=0x460, f1x=0x461, f0y=0x480, f1y=0x481)
    e.set_fields(F)
    s0 = e.load(START)
    print("start", s0["frame"], "x", s0["x"], "y", s0["y"], "hp", s0["hp"], "rng", s0["rng"], "bosshp", s0["bosshp"])
    sid = e.msave()
    tr = C.play_trace(e, [()] * 330)
    for t in tr[::3]:
        print("idle", t["frame"] - s0["frame"], "J", t["jx"], t["jy"], t["jid"], "R", t["x"], t["y"], "hp", t["hp"],
              "anim", t["anim"], "fb", t["f0id"], t["f0x"], t["f0y"], t["f1id"], t["f1x"], t["f1y"])
    # walk right: speed and terrain profile
    e.mload(sid)
    tr = C.play_trace(e, [("Right",)] * 200)
    print("walkR", [(t["frame"] - s0["frame"], t["x"], t["y"], t["anim"]) for t in tr[::4]])
    # jump straight up profile
    e.mload(sid)
    tr = C.play_trace(e, [("A",)] * 2 + [()] * 60)
    print("jumpup", [(i, t["y"], t["anim"]) for i, t in enumerate(tr)])
finally:
    e.close()
