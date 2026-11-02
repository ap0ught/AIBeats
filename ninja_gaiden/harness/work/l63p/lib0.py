"""6-3/6-4 prep: TAS dump reader. TM(f) = TAS RAM after row f (f = 34563 .. 39700 from tas63_ram.bin; earlier -> work/l61p)."""
D = open('work/l63p/tas63_ram.bin', 'rb').read(); TF0 = int.from_bytes(D[:4], 'little'); D = D[4:]
NF = len(D) // 2048
_old = None
def TM(f):
    global _old
    if f > TF0:
        i = f - TF0 - 1; return D[i*2048:(i+1)*2048]
    if _old is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location('l61lib0', 'work/l61p/lib0.py'); _old = importlib.util.module_from_spec(spec); spec.loader.exec_module(_old)
    return _old.TM(f)
def XY(m):
    hi = m[0x52]; hi = hi - 256 if hi >= 128 else hi
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
