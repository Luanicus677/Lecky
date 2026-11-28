# coverage.py [--todo] : how many footnotes of Rationalism link to a source page, per chapter.
# --todo also lists every unlinked note that cites a work (citations from data/unlinked-citations.json,
# Muse-parsed 31 Oct 2026; work titles not normalised), and marks authors named in the DEAD ENDS list of
# notes/source-log.md with [dead end?] so a run can skip or re-try them knowingly.
import re, glob, json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
cat = {x['id']: x for x in json.load(open(f'{R}/data/unlinked-citations.json'))}
log = open(f'{R}/notes/source-log.md', encoding='utf-8').read()
m = re.search(r'## DEAD ENDS(.*?)(\n## |\Z)', log, re.S)
dead = [w.strip().lower() for w in re.findall(r'^- \*\*([^*]+)\*\*', m.group(1) if m else '', re.M)]
tot = lk = 0; todo = []
for f in sorted(glob.glob(f'{R}/content/rationalism/vol*-ch*.md')):
    st = os.path.basename(f)[:-3]; notes = re.findall(r'^\[\^(\d+)\]:(.*)$', open(f, encoding='utf-8').read(), re.M)
    l = sum('href="../ref/' in t for _, t in notes); tot += len(notes); lk += l
    print(f'{st}: {l}/{len(notes)} linked')
    for n, t in notes:
        if 'href="../ref/' in t: continue
        cites = (cat.get(f'{st}#{n}') or {}).get('cites') or []
        if cites:
            key = '; '.join(f"{c.get('author','')} {c.get('work','')} {c.get('locator','')}".strip() for c in cites)
            flag = ' [dead end?]' if any(d and d in key.lower() for d in dead) else ''
            todo.append(f'{st} n{n}: {key}{flag}')
print(f'ALL: {lk}/{tot} linked; {len(todo)} unlinked notes cite a work')
if '--todo' in sys.argv: print('\n'.join(todo))
