"""Insert l63p sections: LOCKED_CHAIN (before '## History') and legal_a56_notes (at the end). UTF-8, CRLF kept, .backup, tmp + os.replace."""
import os, shutil, sys
SP = sys.argv[1]
def crlf(t): return t.replace('\r\n', '\n').replace('\n', '\r\n')
# LOCKED_CHAIN
p = 'knowledge/LOCKED_CHAIN.md'
s = open(p, 'rb').read().decode('utf-8')
assert '## Next: 6-3 / 6-4 plan' not in s, 'already inserted'
sec = open(os.path.join(SP, 'draft_notes.md'), encoding='utf-8').read().strip('\n') + '\n\n'
i = s.index('\r\n## History')
shutil.copyfile(p, p + '.backup_l63p')
new = s[:i] + '\r\n' + crlf(sec).rstrip('\r\n') + '\r\n' + s[i:]
open(p + '.tmp', 'wb').write(new.encode('utf-8')); os.replace(p + '.tmp', p)
# legal_a56_notes
p = 'knowledge/legal_a56_notes.md'
s = open(p, 'rb').read().decode('utf-8')
assert '## 6-3 / 6-4 prep' not in s
sec = open(os.path.join(SP, 'draft_a56.md'), encoding='utf-8').read().strip('\n') + '\n'
shutil.copyfile(p, p + '.backup_l63p')
new = s.rstrip('\r\n') + '\r\n\r\n' + crlf(sec)
open(p + '.tmp', 'wb').write(new.encode('utf-8')); os.replace(p + '.tmp', p)
print('ok')
