"""Insert a note (UTF-8 text file) right after a heading line in a markdown file: temp file + rename, .backup copy.
python work/l52b/addnote.py <md> '<heading line>' <note file>"""
import sys, os, shutil
md, head, nf = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(md, encoding='utf-8').read(); note = open(nf, encoding='utf-8').read().rstrip('\n') + '\n'
i = s.index(head + '\n') + len(head) + 1
shutil.copyfile(md, md + '.backup')
s2 = s[:i] + note + s[i:]
open(md + '.tmp', 'w', encoding='utf-8').write(s2); os.replace(md + '.tmp', md)
print('ok', len(s), '->', len(s2))
