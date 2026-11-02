"""Replay an input list from power-on in Mesen (test runner, headless) and compare per-frame fields with a NesHawk trace.

    python work/fastcore/sync_test.py <inputs.txt> <trace.csv> <tag> [--ioff 0] [--raminit nes|none] [--n N] [--full]
"""
import argparse, csv, json, struct, subprocess, sys, time
from pathlib import Path
P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P))
from ng.inputs import read_inputs, to_mask
MESEN = Path(r"G:\AI World Record\Mesen2\Mesen.exe")
ROM = P / "Ninja Gaiden (USA).nes"
W = P / "work" / "fastcore"
FIELDS = json.loads((P / "knowledge" / "ram.json").read_text())["fields"]
NAMES = list(FIELDS)
ADDRS = [int(v, 16) for v in FIELDS.values()]

def run(inputs, tag, ioff, raminit, n, full, extra=(), force=False, masks=None, tpl="replay_tpl.lua"):
    rows = read_inputs(inputs)
    n = n or len(rows)
    mfile = W / "out" / f"{tag}.masks"
    mfile.write_bytes(bytes(masks) if masks is not None else bytes(to_mask(r) for r in rows))
    out = W / "out" / f"{tag}.bin"
    for s in ("", ".done", ".ram"):
        Path(str(out) + s).unlink(missing_ok=True)
    hdr = (f'MASKS = [[{mfile.as_posix()}]]\nOUT = [[{out.as_posix()}]]\nIOFF = {ioff}\nRAMINIT = "{raminit}"\n'
           f'FULLRAM = {"true" if full else "false"}\nNFRAMES = {n}\nFORCE = {"true" if force else "false"}\n')
    body = (W / tpl).read_text().replace("FIELDS_LIST", "{" + ",".join(map(str, ADDRS)) + "}")
    lua = W / "out" / f"{tag}.lua"
    lua.write_text(hdr + body)
    t = time.time()
    cmd = [str(MESEN), "--testrunner", str(ROM), str(lua), "--debug.scriptWindow.allowIoOsAccess=true",
           "--nes.allowInvalidInput=true", "--timeout=3000", *extra]
    p = subprocess.run(cmd, creationflags=0x08000000, timeout=900)
    wall = time.time() - t
    done = Path(str(out) + ".done")
    print("exit", p.returncode, "wall %.1fs" % wall, "done:", done.read_text().strip() if done.exists() else None)
    return out

def load_mesen(out):
    d = out.read_bytes(); rs = 14 + len(ADDRS); res = []
    for i in range(0, len(d), rs):
        fr, polls, reads, cur, bits = struct.unpack_from("<IIBBI", d, i)
        res.append((fr, polls, reads, cur, d[i + 14:i + rs], bits))
    return res

def load_trace(path):
    res = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            res[int(r["row"])] = (r, bytes(int(r[k]) if k in r else 0 for k in NAMES))
    return res

def compare(mes, tr, fo, skip=()):
    """mes frame f vs trace row f+fo; returns list of (frame, [diff fields])."""
    diffs = []
    idx = [i for i, k in enumerate(NAMES) if k not in skip and k != "hudphase"]
    for fr, polls, reads, cur, b, bits in mes:
        r = tr.get(fr + fo)
        if r is None:
            continue
        d = [NAMES[i] for i in idx if b[i] != r[1][i]]
        if d:
            diffs.append((fr, d))
    return diffs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs"); ap.add_argument("trace"); ap.add_argument("tag")
    ap.add_argument("--ioff", type=int, default=0); ap.add_argument("--raminit", default="nes")
    ap.add_argument("--n", type=int, default=0); ap.add_argument("--full", action="store_true")
    ap.add_argument("--force", choices=["", "rows", "tracepad"], default="")
    ap.add_argument("--norun", action="store_true"); ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    out = W / "out" / f"{a.tag}.bin"
    if not a.norun:
        masks = None
        if a.force == "tracepad":
            tr0 = load_trace(a.trace); ip = NAMES.index("pad")
            masks = [tr0[k][1][ip] if k in tr0 else 0 for k in range(1, max(tr0) + 1)]
        out = run(a.inputs, a.tag, a.ioff, a.raminit, a.n, a.full, a.extra, force=bool(a.force), masks=masks)
    mes = load_mesen(out); tr = load_trace(a.trace)
    print("mesen frames", len(mes), "trace rows", len(tr))
    for fo in range(-3, 4):
        d = compare(mes, tr, fo)
        print("frame offset", fo, "differing frames", len(d), "first", d[0] if d else None)
