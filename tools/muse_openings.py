#!/usr/bin/env python3
"""Muse drafts plain-English openings for older source pages; a mechanical check
(every number and capitalised name in the draft must occur in the page's own text)
decides whether a draft is applied. Old abstracts move into a folded Editor's notes box.
Usage: python3 tools/muse_openings.py [--apply]"""
import sys, re, json, glob, os, subprocess, time, html, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from muse import ask
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'data', 'openings-drafts.json')
P = """You are helping edit a scholarly website about W. E. H. Lecky's "History of Rationalism" (1865). Below is the full text of one "source page": it checks a book Lecky cited against the original.
Write (1) a plain-English OPENING of 2-4 sentences (max 110 words) for a general reader, leading with the single most surprising or concrete finding on the page (what the source really says, what Lecky changed or got wrong, a vivid detail); and (2) a plain-English SUBTITLE of at most 12 words.
Rules: use ONLY facts stated in the page text below; do not add any name, date, number, title or claim that is not in it; no hype words ("fascinating", "remarkable"); British spelling; curly quotes. Refer to the author by surname.
Answer as JSON only: {"subtitle": "...", "opening": "..."}

PAGE TEXT:
"""
STOP = set("The A An In On At Of And But Or For To By From With As His Her Their Its This That These Those It He She They We I Lecky’s Lecky Here There When Where What Which Who Why How Both Also Even Only So Yet Not No Then Than One Two Three First Second Third Book Part Chapter Note Notes Vol Volume Latin French Italian English Greek".split())
def plain(t):
    t = re.sub(r'<[^>]+>', ' ', t); t = html.unescape(t); return re.sub(r'\s+', ' ', t)
def targets():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/ref/*.md'))):
        s = os.path.basename(f)[:-3]
        if s == 'index': continue
        t = open(f, encoding='utf-8').read()
        if 'editor-notes' in t or 'abstract: |' not in t: continue
        d = subprocess.run(['git', '-C', ROOT, 'log', '--diff-filter=A', '--format=%ad', '--date=short', '--', f], capture_output=True, text=True).stdout.split()
        if d and d[-1] >= '2026-10-31': continue
        out.append((s, f, t))
    return out
def check(draft, src):
    srcl = src.lower(); bad = []
    for n in re.findall(r'\d[\d,.–-]*\d|\d', draft):
        if n.strip('.,') not in src: bad.append(n)
    for w in re.findall(r'\b[A-ZÀ-Þ][\w’\'-]+', draft):
        if w in STOP: continue
        if w.lower().rstrip('’s').rstrip("'s") not in srcl: bad.append(w)
    return bad
def run(item):
    s, f, t = item
    src = plain(t)[:14000]
    for k in range(4):
        try:
            a, u = ask(P + src, max_tokens=6000)
            j = json.loads(a[a.find('{'):a.rfind('}') + 1])
            bad = check(j['opening'] + ' ' + j['subtitle'], plain(t))
            return s, dict(j, bad=bad, ok=not bad), u
        except Exception as e:
            err = repr(e); time.sleep(5 * (k + 1))
    return s, {'error': err}, {}
def apply(res):
    n = 0
    for s, j in res.items():
        if not j.get('ok'): continue
        f = os.path.join(ROOT, 'content/ref', s + '.md'); t = open(f, encoding='utf-8').read()
        if 'editor-notes' in t: continue  # already applied: never append a second notes box
        m = re.match(r'(---\n)(.*?)(\n---\n)(.*)', t, re.S); fm, body = m.group(2) + '\n', m.group(4)
        am = re.search(r'^abstract: \|\n((?:  .*\n?|\n)*)', fm, re.M)
        old = '\n'.join(l[2:] if l.startswith('  ') else l for l in am.group(1).rstrip('\n').split('\n')).strip()
        op = j['opening'].replace('"', '“', 1) if False else j['opening']
        fm = fm[:am.start()] + 'abstract: |\n  <p>' + op + '</p>\n' + fm[am.end():]
        sub = j['subtitle'].replace('"', '”')
        fm = re.sub(r'^subtitle:.*$', 'subtitle: "' + sub + '"', fm, count=1, flags=re.M) if re.search(r'^subtitle:', fm, re.M) else fm
        body = body.rstrip('\n') + '\n\n<details class="collapse editor-notes"><summary>Editor’s notes on this page</summary>\n' + old + '\n</details>\n'
        open(f, 'w', encoding='utf-8').write('---\n' + fm.rstrip('\n') + '\n---\n' + body); n += 1
    return n
if __name__ == '__main__':
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    items = [x for x in targets() if x[0] not in res or 'error' in res[x[0]]]
    tin = tout = 0
    with cf.ThreadPoolExecutor(3) as ex:
        for s, j, u in ex.map(run, items):
            res[s] = j; tin += u.get('prompt_tokens', 0); tout += u.get('completion_tokens', 0)
            json.dump(res, open(OUT, 'w'), indent=1, ensure_ascii=False)
    ok = sum(1 for j in res.values() if j.get('ok'))
    print(f'drafted {len(items)}; ok {ok}; failed check {sum(1 for j in res.values() if j.get("bad"))}; errors {sum(1 for j in res.values() if "error" in j)}; cost ${tin*1e-7+tout*2e-7:.4f}')
    if '--apply' in sys.argv: print('applied', apply(res))
