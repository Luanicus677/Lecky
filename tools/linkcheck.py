# linkcheck.py : check every relative href (and #anchor) in docs/ resolves. Run after python3 build.py.
import os, re, html, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
ids, files = {}, []
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith('.html'):
            p = os.path.normpath(os.path.join(d, f)); files.append(p)
            ids[p] = set(re.findall(r'\bid="([^"]+)"', open(p, encoding='utf-8').read()))
bad = []
for p in files:
    for h in re.findall(r'href="([^"]+)"', open(p, encoding='utf-8').read()):
        h = html.unescape(h)
        if re.match(r'^[a-z]+:', h) or h.startswith('//'): continue
        path, _, frag = h.partition('#')
        tgt = os.path.normpath(os.path.join(os.path.dirname(p), path)) if path else p
        if path and not os.path.exists(tgt): bad.append((p, h)); continue
        if frag and tgt.endswith('.html') and frag not in ids.get(tgt, set()): bad.append((p, h))
for b in bad: print('BROKEN', os.path.relpath(b[0], root), b[1])
print(len(bad), 'broken links')
sys.exit(1 if bad else 0)
