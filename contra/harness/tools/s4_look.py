"""Print selected RAM of captured frames: python tools/s4_look.py <stage> <tag> <from> <to> [slots...]"""
import sys, json, numpy as np
st, tag, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
slots = [int(x) for x in sys.argv[5:]] or [14, 13]
R = np.load(f"logs/s{st}/x_cap_{tag}.npy")
J = json.load(open(f"logs/s{st}/x_cap_{tag}.json"))
for i in range(a, b + 1):
    r = R[i]
    row = "+".join(J["rows"][i - 1]) if i > 0 else ""
    s = f"i={i:3d} fc={r[0x1a]:3d} {'L' if J['lag'][i] else ' '} in={row:14s} P({r[0x334]},{r[0x31a]}.{r[0x94]:02x} vy={r[0xc6]:02x}{r[0xc4]:02x} j={r[0xa0]:02x} aim={r[0xc2]}) pl={r[0x87]} cr={r[0x86]} bd={r[0x3b]}"
    for k in slots:
        s += (f" | e{k} t{r[0x528+k]:02x} r{r[0x4b8+k]} hp{r[0x578+k]:02x} x{r[0x33e+k]} y{r[0x324+k]} st{r[0x598+k]:02x} d{r[0x538+k]:02x} sp{r[0x30a+k]:02x}"
              f" v1={r[0x5b8+k]:02x} v4={r[0x5e8+k]:02x} of={r[0x4e8+k]:02x}.{r[0x4f8+k]:02x} dir={r[0x508+k]:02x} at={r[0x558+k]:02x} fr={r[0x568+k]}")
    bl = " B:" + " ".join(f"{k}:{r[0x3c8+k]},{r[0x3b8+k]}r{r[0x438+k]}t{r[0x418+k]}" for k in range(10) if r[0x388+k])
    print(s + bl)
