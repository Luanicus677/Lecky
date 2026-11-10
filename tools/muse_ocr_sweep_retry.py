#!/usr/bin/env python3
"""Re-run only the chunks of muse_ocr_sweep.py that failed (entries with chunk_error) and
merge the results into data/ocr-flags.json. Chunking is deterministic, so chunk numbers
match as long as the chapter files have not changed since the sweep."""
import sys, os, json, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from muse_ocr_sweep import chunks, run, OUT
if __name__ == '__main__':
    out = json.load(open(OUT, encoding='utf-8'))
    bad = {x['chunk'] for x in out if x.get('chunk_error')}
    cs = [(i, c) for i, c in enumerate(chunks()) if i in bad]
    print('retrying', len(cs), 'chunks', flush=True)
    tin = tout = 0
    with cf.ThreadPoolExecutor(4) as ex:
        for i, fl, u in ex.map(run, cs):
            out = [x for x in out if x.get('chunk') != i] + [dict(x, chunk=i) for x in fl]
            tin += u.get('prompt_tokens', 0); tout += u.get('completion_tokens', 0)
            json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'flags now {sum(1 for x in out if not x.get("chunk_error"))}; still failed {sum(1 for x in out if x.get("chunk_error"))}; cost ${tin*1e-7+tout*2e-7:.4f}', flush=True)
