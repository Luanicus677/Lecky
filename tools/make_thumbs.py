"""Make the small pictures used in the 'rabbit hole' boxes.

For each source page, take its first title-page image (or, failing that, its
first facsimile) and write a 360x240 crop to assets/img/ref/thumbs/.
Run after adding a source page with a picture:  python3 tools/make_thumbs.py
"""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "content" / "ref"
OUT = ROOT / "assets" / "img" / "ref" / "thumbs"
W, H = 360, 240


def first_image(text):
    for cls in ("title-page", "facsimile"):
        m = re.search(r'<figure class="[^"]*\b' + cls + r'\b[^"]*">.*?<img src="\.\./assets/img/ref/([^"]+)"', text, re.S)
        if m:
            return m.group(1)
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for md in sorted(REF.glob("*.md")):
        name = first_image(md.read_text())
        if not name:
            continue
        src, dst = ROOT / "assets" / "img" / "ref" / name, OUT / Path(name).with_suffix(".jpg").name
        if not src.exists() or (dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime):
            continue
        im = Image.open(src).convert("RGB")
        w, h = im.size
        if w / h > W / H:      # wide strip: keep the left part, full height
            im = im.crop((0, 0, int(h * W / H), h))
        else:                  # tall page: keep the top
            im = im.crop((0, 0, w, int(w * H / W)))
        im.resize((W, H), Image.LANCZOS).save(dst, "JPEG", quality=72, optimize=True)
        made += 1
    print(f"{made} thumbnails written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
