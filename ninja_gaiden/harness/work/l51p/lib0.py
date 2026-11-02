"""5-1 prep: TAS dump reader. TM(f) = TAS RAM after row f (f = 22126 .. 24525). TAS 5-1 control row 22125."""
D = open('work/l51p/tas51_ram.bin', 'rb').read(); TF0 = int.from_bytes(D[:4], 'little'); D = D[4:]
NF = len(D) // 2048
def TM(f):
    i = f - TF0 - 1; return D[i*2048:(i+1)*2048]
def XY(m):
    hi = m[0x52]; hi = hi - 256 if hi >= 128 else hi
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
CTL = 22125
