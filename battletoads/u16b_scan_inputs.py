"""u16b: banned-press scan of a route's input file.   python u16b_scan_inputs.py <route>   (logs/<route>.inputs.txt)"""
import sys
r = sys.argv[1]
ins = [l.rstrip("\n") for l in open(f"logs/{r}.inputs.txt") if not l.startswith("#")]
S = lambda b: set(x for x in b.replace(",", "+").split("+") if x)
lr = [i + 1 for i, b in enumerate(ins) if {"Left", "Right"} <= S(b)]
ud = [i + 1 for i, b in enumerate(ins) if {"Up", "Down"} <= S(b)]
st = [i + 1 for i, b in enumerate(ins) if "Start" in S(b)]
odd = sorted(set(x for b in ins for x in S(b)) - {"Up", "Down", "Left", "Right", "Select", "Start", "A", "B"})
print(f"{r}: {len(ins)} frames; Left+Right {len(lr)} {lr[:5]}; Up+Down {len(ud)} {ud[:5]}; Start on {len(st)} frames {st}; "
      f"Select on {sum(1 for b in ins if 'Select' in S(b))}; unknown buttons {odd}; controller 2: none (one pad per line)")
