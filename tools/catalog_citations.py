import sys, json, re, glob, concurrent.futures as cf
sys.path.insert(0, "/home/user/lecky/tools")
from muse import ask
notes = []
for f in sorted(glob.glob("/home/user/lecky/content/rationalism/vol*.md")):
    stem = f.split("/")[-1][:-3]
    for line in open(f, encoding="utf-8"):
        m = re.match(r"\[\^(\d+)\]: (.*)", line)
        if m and "../ref/" not in line:
            txt = re.sub(r"<span class=\"translation editorial\"[^>]*>.*?</span>", "", m.group(2))
            txt = re.sub(r"<[^>]+>", "", txt)
            notes.append((stem, int(m.group(1)), txt[:1500]))
P = """For each numbered footnote below (from W. E. H. Lecky, History of Rationalism, 1865), list every work it cites or quotes.
Return JSON only: {"items":[{"id":"<id>","cites":[{"author":"","work":"<short title, normalised, e.g. 'De civitate Dei'>","locator":"<vol/book/chapter/page exactly as Lecky gives, or ''>","quote":"<first 12 words of any quotation from that work, or ''>","lang":"<la|fr|it|en|de|''>"}]}]}
Use only what is in the note; do not add page numbers or titles Lecky does not give (but you may expand an obvious abbreviated author name). If a note cites nothing, give "cites":[].

"""
batches = [notes[i:i+8] for i in range(0, len(notes), 8)]
def run(b):
    body = "\n\n".join(f"[{s}#{n}] {t}" for s, n, t in b)
    for k in range(5):
        try:
            a, u = ask(P + body, max_tokens=16000)
            return json.loads(a[a.find("{"):a.rfind("}")+1])["items"], u
        except Exception as e:
            err = e
    return [{"id": f"{s}#{n}", "error": repr(err)} for s, n, t in b], {}
out, tin, tout = [], 0, 0
with cf.ThreadPoolExecutor(4) as ex:
    for items, u in ex.map(run, batches):
        out += items; tin += u.get("prompt_tokens", 0); tout += u.get("completion_tokens", 0)
json.dump(out, open("/home/user/lecky/data/unlinked-citations.json", "w"), indent=1, ensure_ascii=False)
print(len(notes), "notes", len(out), "items", "errors", sum(1 for o in out if "error" in o), "cost $", round(tin*1e-7+tout*2e-7, 4))
