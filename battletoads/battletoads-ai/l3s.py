"""Turbo Tunnel section 5 by beam search. The last course runs at 12 px/frame with walls alternating lanes every
~21 frames while a lane change takes ~26: reacting is always a frame short, so search the inputs instead.
Actions are 4-frame holds (Left always held): nothing / A / Up / Down / A+Up / A+Down. Beam keeps the furthest
survivors, diversified by depth (y) so one doomed line cannot fill it.

    python l3s.py [start_x] [width]   -> logs/pbeam_L3t.json (mount -> level end), knowledge/l3s_inputs.json
"""
import json, sys, time
import l3r
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens

ACTS = [(), ("A",), ("Up",), ("Down",), ("A", "Up"), ("A", "Down")]
MACRO = 4


def rd(e):
    r = e.ram_all()
    return dict(x=r[0x3FD] + 256 * r[0x3EE], y=r[0x41B], z=r[0x475], hp=r[0x51A], lvl=r[0x10], lives=r[0x11])


def search(e, start_x=56000, width=400, max_steps=400):
    """Layered BFS: at constant speed x says nothing, so keep every distinct (depth, height, rising) state per
    layer and let collisions prune. A layer holds a few hundred states at most."""
    m = sorted(tuple(x) for x in json.load(open(PROJECT / "knowledge" / "l3r_map.json")))
    o, prefix, info = l3r.attempt(e, m, stop_x=start_x)
    assert o == "reached", (o, info)
    q0 = rd(e)
    layer = {(q0["y"], q0["z"], 0): dict(sid=e.msave(), x=info["x"], raw=q0["x"], ins=[], y=q0["y"], z=q0["z"])}
    lives0 = q0["lives"]
    t0 = time.time()
    for step in range(max_steps):
        nxt = {}
        for node in layer.values():
            for act in ACTS:
                if node["z"] > 13 and "A" in act:
                    continue                                    # A does nothing in the air: same child as without
                e.mload(node["sid"])
                btn = ("Left",) + act
                e.step(btn, MACRO - 1)
                z1 = e.ram_all()[0x475]
                e.step(btn, 1)
                q = rd(e)
                if q["hp"] == 0 or q["lives"] < lives0:
                    continue
                x = node["x"] + ((q["x"] - node["raw"] + 32768) % 65536 - 32768)
                ins = node["ins"] + ["+".join(btn)] * MACRO
                if q["lvl"] != 3:
                    print(f"  LEVEL END at step {step} x {x} ({time.time() - t0:.0f}s)", flush=True)
                    for n in layer.values():
                        e.mfree(n["sid"])
                    return prefix + ins, x
                key = (q["y"], q["z"], (q["z"] > z1) - (q["z"] < z1))
                if key in nxt or len(nxt) >= width:
                    continue
                nxt[key] = dict(x=x, raw=q["x"], ins=ins, y=q["y"], z=q["z"], sid=e.msave())
        for n in layer.values():
            e.mfree(n["sid"])
        if not nxt:
            print("  search died out at step", step, "x", node["x"], flush=True)
            return None, node["x"]
        layer = nxt
        if step % 10 == 0:
            ys = sorted({k[0] for k in layer})
            print(f"  step {step}: x {next(iter(layer.values()))['x']} states {len(layer)} y {ys[0]}..{ys[-1]} ({time.time() - t0:.0f}s)", flush=True)
    return None, 0


if __name__ == "__main__":
    start_x = int(sys.argv[1]) if len(sys.argv) > 1 else 56000
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    e = BizHawk(log_name="l3s.log")
    t0 = time.time()
    ins, x = search(e, start_x, width)
    e.close()
    print("result", "solved" if ins else "unsolved", x, f"{time.time() - t0:.0f}s")
    if ins:
        (PROJECT / "knowledge" / "l3s_inputs.json").write_text(json.dumps(ins))
        (LOGS_DIR / "pbeam_L3t.json").write_text(json.dumps({
            "bookmark": "L3_bike_go", "inputs": ins, "info": {"x": x, "f": len(ins)}, "state": None, "history": [],
            "note": "TURBO TUNNEL: Left held to ride the screen's left edge; walls read on sight through section 4, "
                    "section 5 (12 px/frame, lanes alternating every 21 frames) solved by beam search.||"
                    f"{len(ins)} frames from the mount"}))
        tokens.mark("Turbo Tunnel section 5 solved by beam search", {"frames": len(ins), "x": x})
