"""Chain A: the emulator core's hidden state (what RAM does not show: where the CPU stands in the idle loop that scrambles the
dice).  core(e, tag) saves a state file states/u16a_hid_<tag>.State, unpacks the core blob (method of early_hidden.py) and
returns {block tag: bytes}.  sig(blocks) = the bytes that must be equal for two runs to continue identically."""
import ctypes
import zipfile

from toads.emulator import BIZHAWK_DIR

_z = None


def unzstd(data):
    global _z
    if _z is None:
        _z = ctypes.CDLL(str(BIZHAWK_DIR / "dll" / "libzstd.dll"))
        _z.ZSTD_decompress.restype = ctypes.c_size_t
        _z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
    cap = 1 << 22
    buf = ctypes.create_string_buffer(cap)
    n = _z.ZSTD_decompress(buf, cap, data, len(data))
    assert n < cap, n
    return buf.raw[:n]


def blocks(blob):
    out, i = {}, 0
    if blob[:4] != b"NESS":
        return {"ALL": blob}
    i = 8
    while i + 8 <= len(blob):
        tag = blob[i:i + 4].decode("latin1")
        n = int.from_bytes(blob[i + 4:i + 8], "little")
        out[tag + f"@{i}"] = blob[i + 8:i + 8 + n]
        i += 8 + n
    return out


def core(e, tag):
    p = e.save(f"u16a_hid_{tag}")
    z = zipfile.ZipFile(p)
    name = next(x for x in z.namelist() if x.lower().startswith("core"))
    data = z.read(name)
    z.close()
    blob = unzstd(data) if name.endswith(".zst") else data
    return blob, blocks(blob)
