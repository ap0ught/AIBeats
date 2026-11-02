"""Merge nh65.py output into nh_ok.tsv (only kills whose row equals the Mesen kill row in demon_all.tsv) and list mismatches."""
import re, sys
mes = {}
for l in open('work/l65/demon_all.tsv'):
    if l.startswith('#'): continue
    p = l.split('\t'); mes[(int(p[0]), p[1])] = int(p[2])
ok, bad = [], []
for fn in sys.argv[1:]:
    for l in open(fn):
        m = re.match(r'(\S+) bf (\d+) kill (None|\((\d+), (\d+))', l)
        if not m: continue
        bf, line = int(m.group(2)), m.group(1)
        k = int(m.group(4)) if m.group(4) else None
        if (bf, line) in mes:
            (ok if k == mes[(bf, line)] else bad).append((bf, line, k, mes[(bf, line)]))
with open('work/l65/nh_ok.tsv', 'a', newline='\n') as f:
    for bf, line, k, _ in ok: f.write(f'{bf}\t{line}\t{k}\n')
print('NesHawk = Mesen:', len(ok), 'mismatch:', bad)
