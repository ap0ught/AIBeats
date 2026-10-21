"""EARLY track (2026-10-09): two entry bookmarks with byte-identical RAM still roll different dice a few frames later
(early_carry.py).  Where is the hidden difference?  Step both to the RAM-identical frame, save, and diff the cores'
savestate blobs block by block (QuickNES state = tagged blocks: CPUR, PPUR, APUR, CTRL, LRAM, SPRT, NTAB, ...).

    python early_hidden.py A B n      (n idle frames after the bookmark before saving)
"""
import sys
import zipfile

from toads.emulator import BizHawk, STATES_DIR, LOGS_DIR


def unzstd(data):
    """decompress with BizHawk's own libzstd.dll (no Python zstd module on this machine)"""
    import ctypes
    from toads.emulator import BIZHAWK_DIR
    z = ctypes.CDLL(str(BIZHAWK_DIR / "dll" / "libzstd.dll"))
    z.ZSTD_decompress.restype = ctypes.c_size_t
    z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
    cap = 1 << 22
    buf = ctypes.create_string_buffer(cap)
    n = z.ZSTD_decompress(buf, cap, data, len(data))
    assert n < cap, n
    return buf.raw[:n]


def blocks(blob):
    """split a QuickNES state into {tag: bytes}; fall back to one block when the layout is unknown"""
    out, i = {}, 0
    try:
        # header: 'NESS' + size? then blocks tag(4) size(4 LE) data
        if blob[:4] != b"NESS":
            raise ValueError
        i = 8
        while i + 8 <= len(blob):
            tag = blob[i:i + 4].decode("latin1")
            n = int.from_bytes(blob[i + 4:i + 8], "little")
            out[tag + f"@{i}"] = blob[i + 8:i + 8 + n]
            i += 8 + n
    except Exception:
        out = {"ALL": blob}
    return out


def main(a, b, n):
    e = BizHawk(log_name="early_hidden.log")
    cores = {}
    for name in (a, b):
        e.load(name)
        e.step((), 1 + n)
        ram = e.ram_all()
        p = e.save(f"early_hid_{name}")
        e.step((), 1)
        z = zipfile.ZipFile(p)
        names = z.namelist()
        core = next(x for x in names if x.lower().startswith("core"))
        cores[name] = (unzstd(z.read(core)) if core.endswith('.zst') else z.read(core), ram, names)
    e.close()
    (ca, ra, na), (cb, rb, nb) = cores[a], cores[b]
    lines = [f"{a} vs {b} at +{n}: RAM differs in {sum(x != y for x, y in zip(ra, rb))} bytes; zip members {na}; core sizes {len(ca)} {len(cb)}; head {ca[:16].hex()}"]
    ba, bb = blocks(ca), blocks(cb)
    for tag in ba:
        x, y = ba[tag], bb.get(tag, b"")
        d = [i for i in range(min(len(x), len(y))) if x[i] != y[i]]
        lines.append(f"  block {tag} len {len(x)}: {len(d)} bytes differ " + " ".join(f"+{i}:{x[i]:02x}/{y[i]:02x}" for i in d[:40]))
    print("\n".join(lines))
    open(LOGS_DIR / "fix" / "early_hidden.txt", "a", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
