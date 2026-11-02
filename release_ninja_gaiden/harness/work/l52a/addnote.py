"""Insert a bullet under '### Agent notes (5-2)' in knowledge/LOCKED_CHAIN.md (utf-8, temp + rename, .backup)."""
import sys, os, shutil
p = 'knowledge/LOCKED_CHAIN.md'
note = open(sys.argv[1], encoding='utf-8').read().rstrip('\n') + '\n'
s = open(p, encoding='utf-8').read()
h = '### Agent notes (5-2)\n'
i = s.index(h) + len(h)
s2 = s[:i] + note + s[i:]
shutil.copyfile(p, p + '.backup')
open(p + '.tmp', 'w', encoding='utf-8').write(s2); os.replace(p + '.tmp', p)
print('ok', len(s), len(s2))
