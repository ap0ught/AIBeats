"""l62: insert a note as the FIRST bullet(s) of '### Agent notes (6-3 / bosses, l62)' (created just before '### Agent notes (6-5 Demon, l65)')."""
import os, shutil, sys
p = 'knowledge/LOCKED_CHAIN.md'
b = open(p, 'rb').read(); crlf = b'\r\n' in b
s = b.decode('utf-8').replace('\r\n', '\n')
note = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n') + '\n'
h = '### Agent notes (6-3 / bosses, l62)\n'
if h not in s:
    j = s.index('### Agent notes (6-5 Demon, l65)\n')
    s = s[:j] + h + '\n' + s[j:]
i = s.index(h) + len(h)
s2 = s[:i] + note + s[i:]
shutil.copy(p, p + '.backup')
out = s2.replace('\n', '\r\n') if crlf else s2
open(p + '.tmp', 'wb').write(out.encode('utf-8')); os.replace(p + '.tmp', p)
print('ok', len(b), len(out))
