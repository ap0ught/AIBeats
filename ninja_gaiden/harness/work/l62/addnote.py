"""l62: insert a note file as the FIRST bullet(s) of '### Agent notes (6-1 / 6-2)' (created at the end of the 'Next: 6-1 / 6-2 plan'
section, just before '## History', if missing) in LOCKED_CHAIN.md (CRLF kept, .backup, temp+rename). python work/l62/addnote.py note.md"""
import os, shutil, sys
p = 'knowledge/LOCKED_CHAIN.md'
b = open(p, 'rb').read(); crlf = b'\r\n' in b
s = b.decode('utf-8').replace('\r\n', '\n')
note = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n') + '\n'
h = '### Agent notes (6-1 / 6-2)\n'
if h not in s:
    j = s.index('\n## History\n', s.index('## Next: 6-1 / 6-2 plan'))
    s = s[:j + 1] + h + '\n' + s[j + 1:]
i = s.index(h) + len(h)
s2 = s[:i] + note + s[i:]
shutil.copy(p, p + '.backup')
out = s2.replace('\n', '\r\n') if crlf else s2
open(p + '.tmp', 'wb').write(out.encode('utf-8')); os.replace(p + '.tmp', p)
print('ok', len(b), len(out))
