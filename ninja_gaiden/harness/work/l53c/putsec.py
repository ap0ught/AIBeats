"""l53c: put work/l53c/sec_draft.md as the section '## 5-3 rooms 31-33 + 5-4' of knowledge/legal_a56_notes.md (replace if present,
else append at the end). UTF-8, CRLF kept, .backup, temp + rename."""
import os, shutil
p = 'knowledge/legal_a56_notes.md'
b = open(p, 'rb').read(); crlf = b'\r\n' in b
s = b.decode('utf-8').replace('\r\n', '\n')
sec = open('work/l53c/sec_draft.md', encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n') + '\n'
h = '## 5-3 rooms 31-33 + 5-4'
if h in s:
    i = s.index(h); j = s.find('\n## ', i + 5)
    s2 = s[:i] + sec + (s[j + 1:] if j >= 0 else '')
    if j >= 0 and not sec.endswith('\n\n'): s2 = s[:i] + sec + '\n' + s[j + 1:]
else:
    s2 = s.rstrip('\n') + '\n\n' + sec
shutil.copy(p, p + '.backup')
out = s2.replace('\n', '\r\n') if crlf else s2
open(p + '.tmp', 'wb').write(out.encode('utf-8')); os.replace(p + '.tmp', p)
print('ok', len(b), len(out))
