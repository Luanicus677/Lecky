#!/usr/bin/env python3
"""Muse reads every chapter of Rationalism in ~6,000-character chunks and flags likely OCR
errors that a spell-checker cannot catch. Nothing is changed: flags go to data/ocr-flags.json
for checking against the page images. Each flag's context is verified to exist in the file."""
import sys, re, json, glob, os, time, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from muse import ask
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'data', 'ocr-flags.json')
P = """The text below is an OCR transcription of W. E. H. Lecky's "History of Rationalism" (London, 1865), already partly corrected. Find remaining OCR ERRORS only: real-word substitutions (e.g. "modem" for "modern", "arid" for "and", "tbe", "bad" for "had"), wrongly split or joined words, misread letters in English words, garbled punctuation that breaks sense. Do NOT flag: 1865 spellings or Lecky's style ("shew", "connexion", "to-day"), quotations in Latin/French/Italian/German, proper names you are unsure of, HTML or Markdown markup.
Return JSON only: {"flags":[{"error":"<exact wrong text>","fix":"<corrected text>","context":"<8-15 consecutive words copied exactly from the text, containing the error>","confidence":"high|medium"}]}. Return {"flags":[]} if none.

TEXT:
"""
def chunks():
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/rationalism/vol*.md'))):
        t = open(f, encoding='utf-8').read()
        t = t.split('\n---\n', 1)[1] if t.startswith('---') else t
        paras = t.split('\n\n'); buf = ''
        for p in paras:
            if len(buf) + len(p) > 6000 and buf:
                yield os.path.basename(f)[:-3], buf; buf = ''
            buf += p + '\n\n'
        if buf: yield os.path.basename(f)[:-3], buf
def run(a):
    i, (ch, c) = a
    for k in range(4):
        try:
            ans, u = ask(P + c, max_tokens=8000)
            j = json.loads(ans[ans.find('{'):ans.rfind('}') + 1])
            fl = []
            for x in j.get('flags', []):
                x['chapter'] = ch; x['context_found'] = x.get('context', '') in c and x.get('error', '') in c
                fl.append(x)
            return i, fl, u
        except Exception as e:
            time.sleep(5 * (k + 1))
    return i, [{'chapter': ch, 'chunk_error': True}], {}
if __name__ == '__main__':
    cs = list(enumerate(chunks()))
    out, tin, tout = [], 0, 0
    with cf.ThreadPoolExecutor(3) as ex:
        for i, fl, u in ex.map(run, cs):
            out += [dict(x, chunk=i) for x in fl]; tin += u.get('prompt_tokens', 0); tout += u.get('completion_tokens', 0)
            json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
    good = [x for x in out if x.get('context_found')]
    print(f'chunks {len(cs)}; flags {len(out)}; verified-in-text {len(good)}; chunk errors {sum(1 for x in out if x.get("chunk_error"))}; cost ${tin*1e-7+tout*2e-7:.4f}')
