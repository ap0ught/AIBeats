"""l4s.py sharded over several emulators. Each worker process owns one BizHawk and a slice of the beam; per layer
the coordinator gathers every child's (rank, key) from all workers, picks the global best `width` (deduped by
key across workers) and tells each worker which of its children to keep. Workers with nothing left get refilled
by replaying input lists from the bookmark (cheap at fast speed). Same goals, env and outputs as l4s.py.

    L4S_WORKERS=3 python l4sp.py <bookmark> <gx> <gdh> [width] [mode]
"""
import json, os, sys, time
import multiprocessing as mp
import l4s
from toads.emulator import BizHawk, PROJECT


def worker(wid, bookmark, mode, gx, gdh, conn):
    rank = l4s.make_rank(mode, gx, gdh)
    goal = l4s.make_goal(mode, gx, gdh)
    e = BizHawk(log_name=f"l4sp_{bookmark}_{wid}.log")
    e.load(bookmark); e.step((), 2)
    q0 = l4s.rd(e); hp0, lives0 = q0["hp"], q0["lives"]
    nodes = {}                                                   # local id -> node
    nid = 0
    if wid == 0:
        nodes[nid] = dict(sid=e.msave(), ins=[], x=q0["x"], h=q0["h"], dh=0, z=q0["z"]); nid += 1
    while True:
        msg = conn.recv()
        if msg[0] == "expand":
            children = []
            for lid, node in nodes.items():
                for act in l4s.ACTS:
                    if node["z"] > 0 and ("B" in act or ("A" in act and "A" not in (node.get("act") or ()))):
                        continue
                    e.mload(node["sid"]); e.step(act, l4s.MACRO)
                    q = l4s.rd(e)
                    if q["hp"] < hp0 or q["lives"] < lives0 or (l4s.LVL and q["lvl"] != l4s.LVL):
                        continue
                    dh = node["dh"] + ((q["h"] - node["h"] + 128) % 256 - 128)
                    ins = node["ins"] + ["+".join(act)] * l4s.MACRO
                    if goal(q["x"], dh, q):
                        e.step((), l4s.SAFE); q2 = l4s.rd(e)
                        if q2["hp"] >= hp0 and q2["lives"] >= lives0:
                            conn.send(("goal", ins, q)); continue
                    children.append(dict(ins=ins, x=q["x"], h=q["h"], dh=dh, z=q["z"], act=act, parent=lid))
            conn.send(("children", [(rank(c), (c["x"] // (4 if l4s.CLIMB else 8), c["h"] // 4, c["z"] > 0), i, c["dh"], c["x"]) for i, c in enumerate(children)]))
            keep = conn.recv()[1]                                # indices into children
            new = {}
            for i in keep:
                c = children[i]
                e.mload(nodes[c["parent"]]["sid"]); e.step(c["act"], l4s.MACRO)
                c["sid"] = e.msave(); new[nid] = c; nid += 1
            for n in nodes.values():
                e.mfree(n["sid"])
            nodes = new
            conn.send(("ready", len(nodes)))
        elif msg[0] == "export":                                 # hand over input lists for rebalancing
            k = msg[1]; out = []
            for lid in list(nodes)[:k]:
                n = nodes.pop(lid); e.mfree(n["sid"]); out.append((n["ins"], n["dh"]))
            conn.send(("nodes", out))
        elif msg[0] == "import":
            for ins, dh in msg[1]:
                e.load(bookmark); e.step((), 2)
                for s in ins:
                    e.step(tuple(b for b in s.split("+") if b), 1)
                q = l4s.rd(e)
                nodes[nid] = dict(sid=e.msave(), ins=ins, x=q["x"], h=q["h"], dh=dh, z=q["z"]); nid += 1
            conn.send(("ready", len(nodes)))
        elif msg[0] == "quit":
            e.close(); return


def search(bookmark, gx, gdh, width, mode, nworkers):
    procs, conns = [], []
    for wid in range(nworkers):
        a, b = mp.Pipe()
        p = mp.Process(target=worker, args=(wid, bookmark, mode, gx, gdh, b)); p.start()
        procs.append(p); conns.append(a)
    t0 = time.time(); best = None
    try:
        for step in range(l4s.MAXSTEPS):
            for c in conns:
                c.send(("expand",))
            allc = []; goal_hit = None
            for wid, c in enumerate(conns):
                while True:
                    m = c.recv()
                    if m[0] == "goal":
                        goal_hit = goal_hit or m; continue
                    break
                allc += [(rank, key, wid, i, dh, x) for rank, key, i, dh, x in m[1]]
            if goal_hit:
                q = goal_hit[2]
                print(f"  GOAL at step {step}: x {q['x']} ({time.time() - t0:.0f}s)", flush=True)
                for c in conns:
                    c.send(("keep", []))
                for c in conns:
                    c.recv()
                return goal_hit[1], q
            allc.sort(key=lambda t: t[0]); seen, keep = set(), {w: [] for w in range(nworkers)}
            kept = 0
            for rank, key, wid, i, dh, x in allc:                # sorted by rank: the first of a bucket is its best
                if key in seen or kept >= width:
                    continue
                seen.add(key); keep[wid].append(i); kept += 1
            for wid, c in enumerate(conns):
                c.send(("keep", keep[wid]))
            counts = [c.recv()[1] for c in conns]
            if allc:
                b = max(allc, key=lambda t: (t[4], t[5]))
                if best is None or b[4] > best[0]:
                    best = (b[4], b[5])
            if not any(counts):
                print("  died out at step", step, flush=True); break
            if step % 5 == 0 and min(counts) == 0 and max(counts) >= 4:   # refill an idle worker
                src, dst = counts.index(max(counts)), counts.index(0)
                t1 = time.time()
                conns[src].send(("export", max(counts) // 2)); moved = conns[src].recv()[1]
                conns[dst].send(("import", moved)); conns[dst].recv()
                print(f"  rebalanced {len(moved)} nodes {src}->{dst} in {time.time() - t1:.0f}s", flush=True)
            if step % 10 == 0:
                print(f"  step {step}: states {sum(counts)} {counts} best dh {best[0]} x {best[1]} ({time.time() - t0:.0f}s)", flush=True)
        return None, None
    finally:
        for c in conns:
            try:
                c.send(("quit",))
            except Exception:
                pass
        for p in procs:
            p.join(timeout=30)


if __name__ == "__main__":
    bm, gx, gdh = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    mode = sys.argv[5] if len(sys.argv) > 5 else "reach"
    n = int(os.environ.get("L4S_WORKERS", 3))
    ins, q = search(bm, gx, gdh, width, mode, n)
    if ins:
        (PROJECT / "knowledge" / f"l4s_{bm}.json").write_text(json.dumps(ins))
        e = BizHawk(log_name=f"l4sp_{bm}_final.log"); e.load(bm); e.step((), 2)
        for s in ins:
            e.step(tuple(b for b in s.split("+") if b), 1)
        e.save(f"{bm}_solved"); e.close()
        print("solved", len(ins), "frames", q)
    else:
        print("unsolved")
