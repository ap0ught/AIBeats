"""safe insert into a shared notes file: python work/l51c/addnote.py <file> <anchor-substring> <textfile> [after|before]
inserts the text after (default) / before the first line containing the anchor; UTF-8, temp + rename, .backup copy."""
import sys, os, shutil
fn, anchor, tf = sys.argv[1], sys.argv[2], sys.argv[3]; mode = sys.argv[4] if len(sys.argv) > 4 else 'after'
src = open(fn, encoding='utf-8').read().split('\n'); add = open(tf, encoding='utf-8').read().rstrip('\n').split('\n')
i = next(k for k, l in enumerate(src) if anchor in l)
out = src[:i + 1] + add + src[i + 1:] if mode == 'after' else src[:i] + add + src[i:]
shutil.copyfile(fn, fn + '.backup')
tmp = fn + '.tmp'; open(tmp, 'w', encoding='utf-8', newline='\n').write('\n'.join(out)); os.replace(tmp, fn)
print('inserted', len(add), 'lines at', i)
