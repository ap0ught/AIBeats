"""The new Level 4 with the spike-pit damage boost (2026-10-02; l4chain.py is the 2026-09-30 line): intro skipped, TAS #5093's own inputs through checkpoint 3, then legal sections
searched along the TAS's path (l4s.py follow mode, checkpoint goals). Rebuilds everything from L3skip_end, saves a
bookmark after each section and reports the toad's absolute height H (unwrapped from the placement) for the next
search's L4S_HROOT.

    python l4chain2.py           -> logs/pbeam_L4n2.json (L4CHAIN_OUT), bookmarks <L4CHAIN_PREFIX>_<section>; root L4CHAIN_ROOT
"""
import json
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from l4tas import load_tas, conv

SECTIONS = [                       # (name, file with inputs, idle frames before them)
    ("cp4", "knowledge/l4s_L4_pick53.json", 2),          # follow: carry the block down the shaft, throw it into barrier 4
    ("ledge5", "knowledge/l4s_L4n_cp4.json", 2),         # reach: over the spike pit (floating platform) to the ledge at 633
    ("cp5", "knowledge/l4s_L4n_ledge5.json", 0),         # old l4.py logic to the x-512 snowman, searched landing + kill of the x-244 one, pile throws, walk past
    ("edge", "knowledge/l4s_L4r_cp5.json", 2),           # down the zigzag to the spike pit's edge (178,94)
    ("fall", "knowledge/l4_boost_fall.json", 0),         # DAMAGE BOOST: the shaft's ice ball knocks the toad down at x 190; up, walk in, hold Left: through the spikes, placed at x 128
    ("adv", "knowledge/l4_fall_right.json", 2),          # land on the left ledge, run right over pillars A/B/C and the bowl until camera x >= 464 (the object loader catches up)
    ("lift", "knowledge/l4_ball_lift.json", 0),          # back to the ice ball rolling up the bowl's right side: punch = stop + lift
    ("top", "knowledge/l4_carry_top.json", 2),           # carry it to pillar C's top (437,126)
    ("bardead", "knowledge/l4_ball_throw.json", 0),      # Right x5 (stop the slide, face right), B: the ball grinds barrier 6 down (184 f)
    ("left2", "knowledge/l4s_L4r_bardead.json", 2),      # reach_left 185 -36: over the pillars and the V-dip to the left ledge (cp 6)
    ("shaft", "knowledge/l4s_L4r_left2.json", 2),        # reach_down_left 61 -90: over pillar A and the urchins, down the shaft
    ("slope", "knowledge/l4s_L4r_shaft.json", 2),        # reach_down 322 -130: down the snowball slope
    ("plats", "knowledge/l4s_L4r_slope.json", 2),        # reach 611: across the ledges to the barrier-7 ledge
    ("cp7", "knowledge/l4_cp7b_inputs.json", 0),         # closed loop: crouch/hop the snowballs; dash off behind the LAST one so the barrier breaks as the toad arrives
    ("warp", "knowledge/l4s_L4r_cp7b.json", 2),           # l4warp search: the sinking lift until the portal spawns (camera y >= 2090), back up, into the portal
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
    if (m[0x23], m[0x24]) == (0x0D, 0xE5):                  # the warp is engaged: Start through the cutscene into Karnath's Lair
        for _ in range(80):
            m = e.ram(0, 0x800)
            if m[0x10] == 8 and m[0x51A] == 47:
                break
            for b in ["Start"] * 2 + [""] * 18:
                m = step(b)
        for _ in range(30):
            m = step("")
        e.save(f"{__import__('os').environ.get('L4CHAIN_PREFIX', 'L4n')}_end")
        print(f"Karnath's Lair: input {len(ins)}, lvl {m[0x10]}, toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]}", flush=True)
    json.dump({"bookmark": ROOT, "inputs": ins,
               "note": "LEVEL 4: ARCTIC CAVERNS. The intro page skipped with a button; TAS #5093's own inputs through checkpoint 3, "
                       "then searched sections. After checkpoint 5 the record's damage boost: the ice ball knocks the toad down at the "
                       "spike pit's edge and it falls through the spikes while invulnerable, skipping the floating platforms and "
                       "the switchback.||Every checkpoint is a barrier; ice blocks and snowballs break them"},
              open(LOGS_DIR / __import__("os").environ.get("L4CHAIN_OUT", "pbeam_L4n2.json"), "w"))
    print("total", len(ins), notes)
    e.close()

if __name__ == "__main__":
    main()
