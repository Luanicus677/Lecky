# gbox.py XML N IMG startregex endregex OUT.jpg WIDTH : crop the bounding box of the words from start to end (column-safe).
# XML = an archive.org <id>_djvu.xml (or a byte-range slice of it); N = 0-based index of the <OBJECT> in that file;
# IMG = the page image of that object (tools/ia_page.sh). Regexes run over the joined page text, case-insensitive; avoid ^ and $.
import re, sys, html
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
xmlp, n, imgp, a, b, out, wd = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], int(sys.argv[7])
o = open(xmlp, encoding='utf-8', errors='replace').read().split('<OBJECT')[1:][n]
W = int(re.search(r'width="(\d+)"', o).group(1)); H = int(re.search(r'height="(\d+)"', o).group(1))
ws = [(html.unescape(t).strip(), [int(x) for x in c.split(',')[:4]]) for c, t in re.findall(r'<WORD coords="([^"]+)"[^>]*>([^<]*)</WORD>', o)]
j=''; st=[]
for w,c in ws: st.append(len(j)); j+=w+' '
def idx(p, after=0):
    m = re.compile(p, re.I).search(j, after)
    if not m: sys.exit('NOT FOUND '+p)
    return max(i for i,s in enumerate(st) if s <= m.start()), m.end()
ia, e = idx(a); ib, _ = idx(b, e)
sel=[c for _,c in ws[ia:ib+1]]
x0=min(min(c[0],c[2]) for c in sel); x1=max(max(c[0],c[2]) for c in sel)
y0=min(min(c[1],c[3]) for c in sel); y1=max(max(c[1],c[3]) for c in sel)
lh=abs(sel[0][1]-sel[0][3])
im=Image.open(imgp); sx=im.width/W; sy=im.height/H
c=im.crop((max(0,int((x0-20)*sx)), max(0,int((y0-lh*0.6)*sy)), min(im.width,int((x1+20)*sx)), min(im.height,int((y1+lh*0.4)*sy))))
c=c.resize((wd,int(c.height*wd/c.width))); c.convert('RGB').save(out,quality=80); print(out,c.size)
