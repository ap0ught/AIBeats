"""At a stage start: on which frame does a one-frame Right press first have an effect?

    python tools/first_effect.py <state one frame before L> [frames] [button]

For j = 0..7 the button is pressed only on frame L+j; the player's x,y are printed for every frame.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.resync import Pool, play  # noqa: E402

state = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
btn = sys.argv[3] if len(sys.argv) > 3 else "Right"
js = [None] + list(range(0, 8))
with Pool(3, name="firsteffect") as pool:
    res = pool.map(lambda emu, j: play(emu, state, [((btn,) if i == j else ()) for i in range(n)], keep_trace=True), js)
base = res[0].trace
print("L =", base[0]["frame"], " no input:")
print("   " + " ".join(f"{s['x']},{s['y']}/{s['pstate']}" for s in base))
for j, r in zip(js[1:], res[1:]):
    diff = next((i for i, (a, b) in enumerate(zip(base, r.trace)) if (a["x"], a["y"]) != (b["x"], b["y"])), None)
    print(f"{btn} on L+{j}: first x/y difference at L+{diff}; final x,y {r.trace[-1]['x']},{r.trace[-1]['y']} "
          f"(no input: {base[-1]['x']},{base[-1]['y']})")
