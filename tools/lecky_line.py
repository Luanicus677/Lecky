# lecky_line.py VOL OUT.jpg "words ..." ["words ..."] : crop full-width lines from Lecky's own 1865 page images,
# to check an OCR reading in the chapters (VOL = 1 or 2). Downloads the item's djvu.xml once into the cache dir.
# Each strip is labelled with the image number n<i> (vol. I: printed page ~ n-29; vol. II: printed page = n-15).
import re, sys, os, subprocess
from PIL import Image, ImageDraw
CACHE = os.environ.get('LECKY_CACHE', '/tmp/lecky-cache'); os.makedirs(CACHE, exist_ok=True)
vol, out, queries = sys.argv[1], sys.argv[2], sys.argv[3:]
ID = {'1': 'rationalismeuro01leckuoft', '2': 'rationalismineur02leckuoft'}[vol]
xmlp = f'{CACHE}/v{vol}.xml'
if not os.path.exists(xmlp) or os.path.getsize(xmlp) < 100000:
    for _ in range(4):
        subprocess.run(['curl', '-sSL', '-m', '300', f'https://archive.org/download/{ID}/{ID}_djvu.xml', '-o', xmlp])
        if os.path.getsize(xmlp) > 100000: break
objs = open(xmlp, encoding='utf-8', errors='replace').read().split('<OBJECT')[1:]
norm = lambda w: re.sub(r'[^a-z0-9]', '', w.lower())
strips = []
for q in queries:
    seq = [norm(x) for x in q.split()]; done = False
    for pi, o in enumerate(objs):
        ws = [(norm(t), [int(x) for x in c.split(',')[:4]]) for c, t in re.findall(r'<WORD coords="([^"]+)"[^>]*>([^<]*)</WORD>', o)]
        ws = [w for w in ws if w[0]]
        for k in range(len(ws) - len(seq) + 1):
            if all(ws[k + j][0].startswith(seq[j]) for j in range(len(seq))):
                H = int(re.search(r'height="(\d+)"', o).group(1))
                p = f'{CACHE}/v{vol}_{pi}.jpg'
                if not os.path.exists(p):
                    subprocess.run(['curl', '-sSL', '-m', '90', f'https://archive.org/download/{ID}/page/n{pi}.jpg', '-o', p])
                im = Image.open(p); sy = im.height / H
                ys = sorted(ws[k][1][1::2]); lh = ys[1] - ys[0]
                c = im.crop((0, int((ys[0] - lh * 0.5) * sy), im.width, int((ys[1] + lh * 1.6) * sy)))
                c = c.resize((1100, int(c.height * 1100 / c.width))); strips.append((q, pi, c)); done = True; break
        if done: break
    if not done: print('NOT FOUND', q)
if strips:
    M = Image.new('RGB', (1100, sum(c.height + 18 for _, _, c in strips)), 'white'); y = 0; d = ImageDraw.Draw(M)
    for q, pi, c in strips:
        d.text((4, y), f'{q} [n{pi}]', fill='black'); M.paste(c, (0, y + 16)); y += c.height + 18
    M.save(out); print(out, M.size)
