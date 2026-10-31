#!/usr/bin/env python3
"""Re-run the failed entries of data/unlinked-citations.json in batches of 4 (Muse), merging results in place."""
import sys, json, re, glob, time, concurrent.futures as cf
sys.path.insert(0, "/home/user/lecky/tools")
from muse import ask
OUT = "/home/user/lecky/data/unlinked-citations.json"
P = """For each numbered footnote below (from W. E. H. Lecky, History of Rationalism, 1865), list every work it cites or quotes.
Return JSON only: {"items":[{"id":"<id>","cites":[{"author":"","work":"<short title, normalised, e.g. 'De civitate Dei'>","locator":"<vol/book/chapter/page exactly as Lecky gives, or ''>","quote":"<first 12 words of any quotation from that work, or ''>","lang":"<la|fr|it|en|de|''>"}]}]}
Use only what is in the note; do not add page numbers or titles Lecky does not give (but you may expand an obvious abbreviated author name). If a note cites nothing, give "cites":[].

"""

data = json.load(open(OUT))
bad = {x["id"] for x in data if "error" in x}
notes = {}
for f in sorted(glob.glob("/home/user/lecky/content/rationalism/vol*.md")):
    stem = f.split("/")[-1][:-3]
    for line in open(f, encoding="utf-8"):
        m = re.match(r"\[\^(\d+)\]: (.*)", line)
        if m and f"{stem}#{m.group(1)}" in bad:
            txt = re.sub(r'<span class="translation editorial"[^>]*>.*?</span>', "", m.group(2))
            notes[f"{stem}#{m.group(1)}"] = re.sub(r"<[^>]+>", "", txt)[:1500]
ids = list(notes)
batches = [ids[i:i+4] for i in range(0, len(ids), 4)]
def run(b):
    body = "\n\n".join(f"[{i}] {notes[i]}" for i in b)
    for k in range(4):
        try:
            a, u = ask(P + body, max_tokens=16000)
            items = json.loads(a[a.find("{"):a.rfind("}")+1])["items"]
            return items, u
        except Exception as e:
            time.sleep(5)
    return [], {}
got, tin, tout = {}, 0, 0
with cf.ThreadPoolExecutor(3) as ex:
    for items, u in ex.map(run, batches):
        for it in items:
            if it.get("id") in notes: got[it["id"]] = it
        tin += u.get("prompt_tokens", 0); tout += u.get("completion_tokens", 0)
data = [got.get(x["id"], x) if "error" in x else x for x in data]
json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
print("retried", len(ids), "fixed", len(got), "still bad", sum(1 for x in data if "error" in x), "cost $", round(tin*1e-7+tout*2e-7, 4))
