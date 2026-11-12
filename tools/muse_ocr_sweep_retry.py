#!/usr/bin/env python3
"""Re-run only the chunks of muse_ocr_sweep.py that failed (entries with chunk_error) and
merge the results into data/ocr-flags.json. Chunking is deterministic, so chunk numbers
match as long as paragraph lengths have not moved a 6,000-character boundary.
Each failure is logged with its reason; the token allowance grows on each attempt, because
the usual failure is Muse spending its whole allowance on hidden reasoning."""
import sys, os, json, time, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from muse import ask
from muse_ocr_sweep import chunks, OUT, P

def run(a):
    i, (ch, c) = a
    for k, mt in enumerate((12000, 20000, 32000)):
        try:
            ans, u = ask(P + c, max_tokens=mt)
            j = json.loads(ans[ans.find('{'):ans.rfind('}') + 1])
            fl = []
            for x in j.get('flags', []):
                x['chapter'] = ch; x['context_found'] = x.get('context', '') in c and x.get('error', '') in c
                fl.append(x)
            return i, fl, u
        except Exception as e:
            print(f'  chunk {i} attempt {k + 1} (max_tokens {mt}): {type(e).__name__}: {str(e)[:120]}', flush=True)
            time.sleep(3 * (k + 1))
    return i, [{'chapter': ch, 'chunk_error': True}], {}

if __name__ == '__main__':
    out = json.load(open(OUT, encoding='utf-8'))
    bad = {x['chunk'] for x in out if x.get('chunk_error')}
    cs = [(i, c) for i, c in enumerate(chunks()) if i in bad]
    print('retrying', len(cs), 'chunks', flush=True)
    tin = tout = 0
    with cf.ThreadPoolExecutor(8) as ex:
        # as_completed, not map: a slow chunk must not hold back finished ones
        for n, fut in enumerate(cf.as_completed([ex.submit(run, c) for c in cs]), 1):
            i, fl, u = fut.result()
            out = [x for x in out if x.get('chunk') != i] + [dict(x, chunk=i) for x in fl]
            tin += u.get('prompt_tokens', 0); tout += u.get('completion_tokens', 0)
            json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
            print(f'done {n}/{len(cs)} (chunk {i}: {len([x for x in fl if not x.get("chunk_error")])} flags{", FAILED" if any(x.get("chunk_error") for x in fl) else ""})', flush=True)
    print(f'flags now {sum(1 for x in out if not x.get("chunk_error"))}; still failed {sum(1 for x in out if x.get("chunk_error"))}; cost ${tin*1e-7+tout*2e-7:.4f}', flush=True)
