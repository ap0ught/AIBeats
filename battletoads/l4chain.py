"""The new Level 4 (2026-09-30): intro skipped, TAS #5093's own inputs through checkpoint 3, then legal sections
searched along the TAS's path (l4s.py follow mode, checkpoint goals). Rebuilds everything from L3skip_end, saves a
bookmark after each section and reports the toad's absolute height H (unwrapped from the placement) for the next
search's L4S_HROOT.

    python l4chain.py            -> logs/pbeam_L4n.json, bookmarks L4n_<section>
"""
import json
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from l4tas import load_tas, conv

SECTIONS = [                       # (name, file with inputs, idle frames before them)
    ("cp4", "knowledge/l4s_L4_pick53.json", 2),          # follow: carry the block down the shaft, throw it into barrier 4
    ("ledge5", "knowledge/l4s_L4n_cp4.json", 2),         # reach: over the spike pit (floating platform) to the ledge at 633
    ("cp5", "knowledge/l4s_L4n_ledge5.json", 0),         # old l4.py logic to the x-512 snowman, searched landing + kill of the x-244 one, pile throws, walk past
    ("onp1", "knowledge/l4n_onp1.json", 0),              # old logic: corner, stop/lift/carry/throw the shaft ball, to the floor by platform 1
    ("onp2", "knowledge/l4_p2hop.json", 0),              # closed-loop hops: platform 1 (heading left past x 224), ride crouched, platform 2
    ("pillar", "knowledge/l4s_n2_L4_cp6_onp2.json", 2),  # reach 560 +49: from platform 2 onto the ice pillar top (h 190)
    ("spiky", "knowledge/l4n_spiky.json", 0),            # old searched section: past the spiky ball on the upper ledge
    ("lower", "knowledge/l4s_n4_L4_cp6_past_spiky.json", 2),   # reach_down 790 -96: off the ledge's right end to the lower ledge (h 62)
    ("ledge3", "knowledge/l4s_n5_L4_cp6_lowerstart.json", 2),  # reach_down_left 600 -96: left along it, drop to ledge 3 (h 222)
    ("bowltop", "knowledge/l4s_n6_L4_ledge3.json", 2),   # reach_down 795 -79: right to the pillar, slide off the wall to (795,139)
    ("pillar2", "knowledge/l4n_pillar2.json", 0),        # old logic: left to the bowl's pillar top (436,126)
    ("toball", "knowledge/l4s_n7_L4_pillar.json", 2),    # reach_down 575 -96: down the slope to the ice ball (580,30)
    ("pickup", "knowledge/l4_pickup6.json", 0),          # B on the ball
    ("stackdead", "knowledge/l4_cp6_throw.json", 0),     # carry it up to the pillar top, stand at x 430 facing RIGHT, B: the ball ricochets pillar<->stack, 255 hp in 180 f
    ("left2", "knowledge/l4s_L4n_stackdead.json", 2),    # reach_left 185 -36: over the spiky V-dip onto the left ledge (cp 6 ticks on the way)
    ("shaft", "knowledge/l4s_L4n_left2.json", 2),        # reach_down_left 60 -93: down the shaft to (46,1)
    ("slope", "knowledge/l4s_L4n_shaft.json", 2),        # reach_down 320 -128: down the slope to the cp7 ledge (322,126)
    ("plats", "knowledge/l4s_L4n_slope.json", 2),        # reach 605: across the ledges to x 611
    ("warp", "knowledge/l4_tail9_inputs.json", 0),       # old closed-loop l4.cp7_stack: crouch/hop the snowballs, the stack falls, the sinking platform, the portal, Start-mash into Karnath's Lair
]

def placed(m): return m[0x10] == 4 and m[0x3FD] == 32 and m[0x3EE] == 0 and m[0x41B] == 216

def main():
    rows = load_tas()
    e = BizHawk(log_name="l4chain.log")
    ROOT = __import__("os").environ.get("L4CHAIN_ROOT", "L3skip_end")
    e.load(ROOT)
    ins = []; H = [None, None]
    def step(b):
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
        m = e.ram(0, 0x800)
        if H[0] is not None:
            H[0] += (m[0x439] - H[1] + 128) % 256 - 128
        H[1] = m[0x439]
        return m
    for k in range(400):                                    # the intro page: any button skips it
        m = step("B" if k % 2 == 0 else "")
        if placed(m): break
    H[0], H[1] = 0, m[0x439]
    for f in range(15312, 16771):                           # TAS #5093, frame-exact through checkpoint 3
        step("+".join(conv(rows[f][0])))
    for b in json.load(open("knowledge/l4_pick53.json")):   # legal pickup of the ice block (its L+R stop is banned)
        step(b)
    notes = []
    for name, fn, idle in SECTIONS:
        p = PROJECT / fn
        if not p.exists():
            break
        for _ in range(idle): step("")
        for b in json.loads(p.read_text()): m = step(b)
        e.save(f"{__import__('os').environ.get('L4CHAIN_PREFIX', 'L4n')}_{name}")
        notes.append((name, len(ins), m[0x585], H[0]))
        print(f"{name}: input {len(ins)}, cp {m[0x585]}, x {m[0x3FD] | m[0x3EE] << 8}, h {m[0x439]}, H {H[0]}, lvl {m[0x10]}", flush=True)
    json.dump({"bookmark": ROOT, "inputs": ins,
               "note": "LEVEL 4: ARCTIC CAVERNS. The intro page skipped with a button; TAS #5093's own inputs through checkpoint 3, "
                       "then searched sections along its path (its Left+Right walk-plane trick is banned, so the block pickup "
                       "and the rest are ours).||Every checkpoint is a barrier; ice blocks and snowballs break them"},
              open(LOGS_DIR / "pbeam_L4n.json", "w"))
    print("total", len(ins), notes)
    e.close()

if __name__ == "__main__":
    main()
