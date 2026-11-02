"""5-2 prep: TAS dump reader. TM(f) = TAS RAM after row f (f = 24429 .. 26828). TAS 5-2 control row 24427 (Left 180->178).
Earlier frames (22126..24525) come from work/l51p/tas51_ram.bin."""
D = open('work/l52p/tas52_ram.bin', 'rb').read(); TF0 = int.from_bytes(D[:4], 'little'); D = D[4:]
NF = len(D) // 2048
D1 = open('work/l51p/tas51_ram.bin', 'rb').read(); TF1 = int.from_bytes(D1[:4], 'little'); D1 = D1[4:]
def TM(f):
    if f <= TF0:
        i = f - TF1 - 1; return D1[i*2048:(i+1)*2048]
    i = f - TF0 - 1; return D[i*2048:(i+1)*2048]
def XY(m):
    hi = m[0x52]; hi = hi - 256 if hi >= 128 else hi
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
CTL = 24427
