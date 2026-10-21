"""u16b: read the hidden CPU state (QuickNES core blob: timestamp, PC, registers) from savestates, frame by frame.
    python u16b_phase.py <bookmark> <segment whose inputs are stepped> <frames> [tag]
Prints for each frame: RAM dice $25-$28, level timer, and the first 20 bytes of the core blob."""
import json, sys, zipfile, ctypes
from toads.emulator import BizHawk, LOGS_DIR, BIZHAWK_DIR, STATES_DIR
from u16b_lib import bt


def unzstd(data):
    z = ctypes.CDLL(str(BIZHAWK_DIR / "dll" / "libzstd.dll"))
    z.ZSTD_decompress.restype = ctypes.c_size_t
    z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
    cap = 1 << 22
    buf = ctypes.create_string_buffer(cap)
    n = z.ZSTD_decompress(buf, cap, data, len(data))
    return buf.raw[:n]


def core_of(path):
    z = zipfile.ZipFile(path)
    core = next(x for x in z.namelist() if x.lower().startswith("core"))
    return unzstd(z.read(core)) if core.endswith(".zst") else z.read(core)


def sig(e, name="u16b_phase_tmp"):
    p = e.save(name)
    c = core_of(p)
    return c


if __name__ == "__main__":
    bm, segname, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    ins = json.load(open(LOGS_DIR / f"pbeam_{segname}.json"))["inputs"]
    e = BizHawk(log_name="u16b_phase.log")
    e.load(bm)
    prev = None
    for j in range(n):
        c = sig(e, "u16b_phase_tmp" + (sys.argv[4] if len(sys.argv) > 4 else ""))
        m = e.ram(0, 0x800)
        d = [] if prev is None else [i for i in range(min(len(c), len(prev))) if c[i] != prev[i] and i < 200]
        print(j, "t", m[0x0B], "rng", m[0x25], m[0x26], m[0x27], m[0x28], "core", c[:24].hex(" "), "| len", len(c), "| changed<200:", d[:30])
        prev = c
        e.step(bt(ins[j]), 1)
    e.close()
