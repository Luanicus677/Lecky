#!/usr/bin/env python3
"""Hunt for a (possibly paraphrased) quotation in a long, badly OCRed book, using Muse.

Usage: python3 tools/hunt.py BOOK_djvu.txt "target sentence or description" OUT.json [--from 0.0 --to 1.0]

The book's OCR is cut into ~120k-character chunks; each chunk goes to Muse
(Contributor tier, public-domain text only) with the target. Failed requests
(Meta returns HTTP 502 quite often) are re-sent in further rounds until every
chunk has been read, so "no hit" really means every chunk was read. Each hit's
quote is checked against the OCR (whitespace-insensitive): quotes that are not
really in the OCR are marked verbatim=NO. Hits are leads only: read the page
image before using anything.

Try cheap keyword searches first (grep for a word the OCR is likely to read
correctly); use this when those fail.
"""
import argparse, concurrent.futures as cf, json, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muse import ask

PROMPT = """Below is raw OCR (poor quality: long s read as f, broken ligatures, missing accents, words run together) of part of an old book.
Task: find any passage whose WORDING or MEANING is close to this, which a 19th-century author quotes or summarises (possibly loosely, compressed, or in translation) from the book:

TARGET: {t}

Answer in JSON only: {{"hits":[{{"quote":"<copy 8-25 consecutive words EXACTLY as they appear in the OCR, errors included>","why":"<one sentence>","strength":"exact|close|loose"}}]}}. If nothing is reasonably close, answer {{"hits":[]}}. Do not invent text; the quote must be copied character for character from the OCR.

OCR:
{c}"""


def find(text, q):
    pat = r"\s*".join(re.escape(ch) for ch in re.sub(r"\s+", "", q))
    m = re.search(pat, text)
    return m.start() if m else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book"); ap.add_argument("target"); ap.add_argument("out")
    ap.add_argument("--from", dest="frm", type=float, default=0.0)
    ap.add_argument("--to", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    text = Path(a.book).read_text(encoding="utf-8", errors="replace")
    lo, hi = int(len(text) * a.frm), int(len(text) * a.to)
    N, OV = 120000, 3000
    todo = {i: text[i:i + N] for i in range(lo, hi, N - OV)}
    done, tin, tout = {}, 0, 0
    for rnd in range(6):
        if not todo:
            break
        def run(i):
            try:
                return i, ask(PROMPT.format(t=a.target, c=todo[i]), max_tokens=6000), None
            except Exception as e:
                return i, None, repr(e)
        with cf.ThreadPoolExecutor(a.workers) as ex:
            for i, res, err in ex.map(run, list(todo)):
                if res:
                    done[i] = res[0]; tin += res[1].get("prompt_tokens", 0); tout += res[1].get("completion_tokens", 0)
        todo = {i: c for i, c in todo.items() if i not in done}
        if todo:
            time.sleep(20 * (rnd + 1))
    hits = []
    for i, ans in sorted(done.items()):
        try:
            for h in json.loads(ans[ans.find("{"):ans.rfind("}") + 1])["hits"]:
                pos = find(text, h["quote"])
                hits.append(dict(h, chunk=i, pos=pos, line=text.count("\n", 0, pos) + 1 if pos >= 0 else None))
        except Exception:
            hits.append({"chunk": i, "bad_json": ans[:300]})
    Path(a.out).write_text(json.dumps({"hits": hits, "unread_chunks": sorted(todo)}, indent=1))
    print(f"chunks read {len(done)}, unread {len(todo)}; tokens in {tin} out {tout}; cost ${tin * 0.1e-6 + tout * 0.2e-6:.4f}")
    for h in hits:
        if "quote" in h:
            print(f"[{h.get('strength')}] line={h['line']} verbatim={'YES' if h['pos'] >= 0 else 'NO'} {h['quote']!r} -- {h.get('why')}")


if __name__ == "__main__":
    main()
