#!/usr/bin/env python3
"""Static site builder for the Lecky edition.

Reads Markdown files (with YAML front matter) from content/, renders them
through templates/, and writes static HTML into docs/ (served directly by
GitHub Pages — no build step runs on GitHub's side).

Usage: python3 build.py
"""
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
OUT = ROOT / "docs"

SITE_NAME = "The Complete Works of W. E. H. Lecky"
GITHUB_REPO = "Luanicus677/lecky"
# The public address of the site, for link previews (Open Graph) and canonical
# links. Change this if the site moves to its own domain.
SITE_URL = "https://luanicus677.github.io/Lecky/"
DEFAULT_SHARE_IMAGE = "assets/img/ref/grillandi-1545-title.jpg"

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)

env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)


def parse_source(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML front matter")
    meta = yaml.safe_load(m.group(1)) or {}
    body_md = text[m.end():]
    return meta, body_md


FOOTNOTE_DEF_RE = re.compile(
    r'<li id="fn:([^"]+)">\s*<p>(.*?)&#160;'
    r'<a class="footnote-backref"[^>]*>.*?</a></p>\s*</li>',
    re.DOTALL,
)
# python-markdown marks a second citation of the same note as fnref2:label.
FOOTNOTE_REF_RE = re.compile(
    r'<sup id="fnref(\d*):([^"]+)"><a class="footnote-ref"[^>]*>(\d+)</a></sup>'
)


def render_markdown(body_md: str) -> str:
    html = markdown.markdown(
        body_md,
        extensions=["extra", "footnotes", "smarty", "sane_lists"],
        extension_configs={
            "footnotes": {"BACKLINK_TEXT": "↩"},
        },
    )

    # Rewrite python-markdown's footnotes into the Pandoc shape gwern.net's
    # footnote CSS targets: a.footnote-ref > sup in the text, and a
    # section.footnotes > hr + ol at the end, each note ending in a
    # boxed a.footnote-back. Plain ids (fn3, fnref3) avoid the colons
    # python-markdown uses, which need escaping in CSS selectors.
    notes = dict(FOOTNOTE_DEF_RE.findall(html))
    html = re.sub(r'<div class="footnote">.*</div>\s*$', "", html, flags=re.DOTALL)

    numbers = {}

    def ref(m):
        repeat, label, number = m.group(1), m.group(2), m.group(3)
        numbers.setdefault(label, number)
        ref_id = f"fnref{number}" + (f"-{repeat}" if repeat else "")
        return (
            f'<a href="#fn{number}" class="footnote-ref" id="{ref_id}" '
            f'role="doc-noteref"><sup>{number}</sup></a>'
        )

    html = FOOTNOTE_REF_RE.sub(ref, html)

    if numbers:
        items = []
        for label, number in sorted(numbers.items(), key=lambda kv: int(kv[1])):
            items.append(
                f'<li id="fn{number}"><p>{notes.get(label, "")}'
                f'<a href="#fnref{number}" class="footnote-back" role="doc-backlink" '
                f'title="Back to the text">↑</a></p></li>'
            )
        html += (
            '\n<section class="footnotes" role="doc-endnotes"><hr>\n<ol>\n'
            + "\n".join(items)
            + "\n</ol>\n</section>\n"
        )
    return html


HEADING_RE = re.compile(r'<h([23]) id="([^"]+)">(.*?)</h\1>', re.DOTALL)


def build_toc(body_html: str) -> str:
    """A gwern.net-style numbered table of contents (nav#TOC) from the page's
    h2/h3 headings, for long pages only (5+ sections)."""
    heads = HEADING_RE.findall(body_html)
    if sum(1 for level, _, _ in heads if level == "2") < 5:
        return ""
    out, n2, n3, open_sub = ['<nav id="TOC" class="TOC" aria-label="Contents"><ul>'], 0, 0, False
    for level, anchor, text in heads:
        if level == "2":
            if open_sub:
                out.append("</ul>")
                open_sub = False
            if n2:
                out.append("</li>")
            n2, n3 = n2 + 1, 0
            out.append(f'<li><a href="#{anchor}"><span class="toc-num">{n2}</span>{text}</a>')
        elif n2:
            if not open_sub:
                out.append("<ul>")
                open_sub = True
            n3 += 1
            out.append(f'<li><a href="#{anchor}"><span class="toc-num">{n2}.{n3}</span>{text}</a></li>')
    if open_sub:
        out.append("</ul>")
    out.append("</li></ul></nav>")
    return "".join(out)


REF_LINK_RE = re.compile(r'href="\.\./ref/([a-z0-9-]+)\.html(?:#[^"]*)?"')
CHAPTER_LABELS = {"vol1-ch4": "Chapter IV, Part I", "vol2-ch4": "Chapter IV, Part II"}


def collect_backlinks():
    """Map each source-page slug to the places in the book that link to it:
    {slug: [(page label, page stem, note number or None)]}, in reading order.
    Used for the automatic Backlinks section on source pages (as gwern.net
    generates backlinks), so it never goes stale like hand-kept lists."""
    links = {}
    for src in sorted((CONTENT / "rationalism").glob("*.md")):
        if src.stem == "index":
            continue
        meta, body = parse_source(src)
        label = CHAPTER_LABELS.get(src.stem) or re.split(r"<br>", str(meta.get("heading") or meta.get("title")))[0]
        for line in body.split("\n"):
            m = re.match(r"\[\^(\d+)\]:", line)
            note = int(m.group(1)) if m else None
            for slug in dict.fromkeys(REF_LINK_RE.findall(line)):
                if note is not None:
                    NOTE_REFS.setdefault((src.stem, note), [])
                    if slug not in NOTE_REFS[(src.stem, note)]:
                        NOTE_REFS[(src.stem, note)].append(slug)
                entry = (label, src.stem, note)
                if entry not in links.setdefault(slug, []):
                    links[slug].append(entry)
    return links


def backlinks_html(entries):
    groups = {}
    for label, stem, note in entries:
        groups.setdefault((label, stem), []).append(note)
    items = []
    for (label, stem), notes in groups.items():
        parts = [f'<a class="popup-ref" href="../rationalism/{stem}.html#fn{n}">note {n}</a>'
                 for n in notes if n is not None]
        if None in notes:
            parts.append(f'<a href="../rationalism/{stem}.html">the text</a>')
        items.append(f"<li><strong>{label}</strong>: " + ", ".join(parts) + "</li>")
    return ('<section id="backlinks" class="backlinks"><h2>Backlinks</h2>'
            '<p class="backlinks-intro">Every place in <i>Rationalism in Europe</i> that links to this page '
            '(generated automatically when the site is built).</p><ul>' + "".join(items) + "</ul></section>\n")


NOTE_REFS = {}   # (chapter stem, note number) -> [source slugs], filled by collect_backlinks
REFMETA = {}     # source slug -> {"title", "subtitle", "teaser"}
CHAPTERS = []    # [(stem, short title)] in reading order
CHAPTER_ORDER = ["introduction", "vol1-ch1", "vol1-ch2", "vol1-ch3", "vol1-ch4", "vol2-ch4", "vol2-ch5", "vol2-ch6"]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", str(s or "")).replace("&amp;", "&").strip()


def collect_refmeta():
    """Titles, plain-English subtitles and a one-sentence teaser for every
    source page, used by the rabbit-hole boxes, chapter ends and the
    random-source button."""
    for src in sorted((CONTENT / "ref").glob("*.md")):
        if src.stem == "index":
            continue
        meta, body = parse_source(src)
        abstract = re.sub(r"\s+", " ", strip_tags(meta.get("abstract")))
        first = re.split(r"(?<=[.!?\u201d])\s+(?=[A-Z\u201c])", abstract)[0] if abstract else ""
        if len(first) > 280:
            first = first[:277].rsplit(" ", 1)[0] + "\u2026"
        thumb = None
        for cls in ("title-page", "facsimile"):
            m = re.search(r'<figure class="[^"]*\b' + cls + r'\b[^"]*">.*?<img src="\.\./assets/img/ref/([^"]+)"', body, re.S)
            if m:
                name = Path(m.group(1)).with_suffix(".jpg").name
                if (ROOT / "assets" / "img" / "ref" / "thumbs" / name).exists():
                    thumb = name
                break
        REFMETA[src.stem] = {
            "thumb": thumb,
            "title": strip_tags(meta.get("heading") or meta.get("title") or src.stem),
            "subtitle": strip_tags(meta.get("subtitle")),
            "teaser": first,
        }
    for stem in CHAPTER_ORDER:
        path = CONTENT / "rationalism" / f"{stem}.md"
        if path.exists():
            meta, body = parse_source(path)
            parts = [strip_tags(s) for s in re.split(r"<br>", str(meta.get("heading") or meta.get("title")))]
            name = ": ".join(s for s in parts if s).replace("&mdash;", "\u2014")
            text = re.sub(r"^\[\^\d+\]:.*$", "", body, flags=re.M)      # main text only
            words = len(strip_tags(text).split())
            CHAPTERS.append((stem, name, words))


def related_sources(slug, k=6):
    """Other source pages Lecky cites close to the notes that cite `slug`:
    the same note scores 1, a neighbouring note 1/(1+distance), up to four
    notes away; pages cited elsewhere in the same chapters fill any gap."""
    score = {}
    for _label, stem, note in BACKLINKS.get(slug, []):
        if note is None:
            continue
        for d in range(-4, 5):
            for other in NOTE_REFS.get((stem, note + d), []):
                if other != slug and other in REFMETA:
                    score[other] = score.get(other, 0) + 1.0 / (1 + abs(d))
    if len(score) < k:
        stems = {stem for _l, stem, _n in BACKLINKS.get(slug, [])}
        for (stem, _note), slugs in NOTE_REFS.items():
            if stem in stems:
                for other in slugs:
                    if other != slug and other in REFMETA and other not in score:
                        score[other] = 0.01
    return sorted(score, key=lambda t: (-score[t], REFMETA[t]["title"]))[:k]


def source_item(slug, prefix=""):
    m = REFMETA[slug]
    sub = f'<span class="rh-sub">{m["subtitle"]}</span>' if m["subtitle"] else ""
    return f'<li><a class="popup-ref" href="{prefix}{slug}.html">{m["title"]}</a>{sub}</li>'


def source_card(slug, prefix="", root="../"):
    """A source as a small card: a crop of its old printed page (or a large
    initial when it has no picture), its title and plain-English subtitle."""
    m = REFMETA[slug]
    if m.get("thumb"):
        pic = (f'<img src="{root}assets/img/ref/thumbs/{m["thumb"]}" alt="" loading="lazy" '
               f'width="180" height="120">')
    else:
        initial = re.sub(r"[^A-Za-z\u00c0-\u024f]", "", m["title"])[:1] or "\u00b6"
        pic = f'<span class="rh-noimg">{initial}</span>'
    sub = f'<span class="rh-sub">{m["subtitle"]}</span>' if m["subtitle"] else ""
    return (f'<li><a class="rh-pic" href="{prefix}{slug}.html" tabindex="-1" aria-hidden="true">{pic}</a>'
            f'<a class="popup-ref rh-title" href="{prefix}{slug}.html">{m["title"]}</a>{sub}</li>')


def rabbit_hole_html(slug):
    rel = related_sources(slug)
    if not rel:
        return ""
    return ('<section id="rabbit-hole" class="rabbit-hole"><h2>Further down the rabbit hole</h2>'
            '<p class="rabbit-intro">Sources that Lecky cites in the notes next to the ones that cite this page.</p><ul class="rh-cards">'
            + "".join(source_card(t) for t in rel) +
            '</ul><p class="rabbit-random"><a class="random-source" href="index.html">Or jump to a random source \u2192</a></p></section>\n')


def gallery_html():
    """Every source page that has a picture, as a grid of cards (old-books.md)."""
    slugs = sorted((s for s, m in REFMETA.items() if m.get("thumb")), key=lambda s: REFMETA[s]["title"].lower())
    return ('<ul class="rh-cards gallery">' + "".join(source_card(s, "ref/", "") for s in slugs) + "</ul>",
            len(slugs))


def newest_sources_html(k=6):
    """The source pages most recently added (by the commit that created each
    file), as picture cards for the home page."""
    import subprocess
    try:
        log = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=%at", "--", "content/ref"],
                             cwd=ROOT, capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ""
    seen, order = set(), []
    for line in log.splitlines():
        m = re.match(r"content/ref/([a-z0-9-]+)\.md$", line.strip())
        if m and m.group(1) in REFMETA and m.group(1) not in seen:
            seen.add(m.group(1)); order.append(m.group(1))
    if not order:
        return ""
    return '<ul class="rh-cards new-sources">' + "".join(source_card(s, "ref/", "") for s in order[:k]) + "</ul>"


def by_chapter_html():
    """For the Sources index: under each chapter, the source pages its notes
    link to, most-cited first, with the number of notes."""
    out = ['<div class="by-chapter">']
    for stem, name, _words in CHAPTERS:
        counts = {}
        for (st, _note), slugs in NOTE_REFS.items():
            if st == stem:
                for s in slugs:
                    if s in REFMETA:
                        counts[s] = counts.get(s, 0) + 1
        if not counts:
            continue
        top = sorted(counts, key=lambda s: (-counts[s], REFMETA[s]["title"]))
        items = "".join(
            f'<li><a class="popup-ref" href="{s}.html">{REFMETA[s]["title"]}</a> '
            f'<span class="bc-count">{counts[s]} note{"s" if counts[s] > 1 else ""}</span></li>' for s in top)
        out.append(f'<details><summary>{name} <span class="bc-count">{len(top)} sources</span></summary>'
                   f'<p class="bc-read"><a href="../rationalism/{stem}.html">Read the chapter \u2192</a></p><ol>{items}</ol></details>')
    out.append("</div>")
    return "".join(out)


def reading_time(words):
    """At 250 words a minute, main text only."""
    mins = round(words / 250 / 5) * 5
    return f"about {mins} minutes" if mins < 90 else f"about {round(mins / 60 * 2) / 2:g} hours"


def chapter_next_html(stem):
    """At the end of a chapter: the next chapter, and the sources this chapter
    leans on most (by the number of its notes that link to them)."""
    counts = {}
    for (st, _note), slugs in NOTE_REFS.items():
        if st == stem:
            for slug in slugs:
                if slug in REFMETA:
                    counts[slug] = counts.get(slug, 0) + 1
    top = sorted(counts, key=lambda t: (-counts[t], REFMETA[t]["title"]))[:6]
    order = [c[0] for c in CHAPTERS]
    nxt = ""
    if stem in order and order.index(stem) + 1 < len(order):
        n_stem, n_title, n_words = CHAPTERS[order.index(stem) + 1]
        took = reading_time(n_words)
        nxt = (f'<p class="next-chapter">Next: <a href="{n_stem}.html">{n_title}</a> \u2192'
               f'<span class="rh-sub">{n_words:,} words, {took} of reading, not counting the notes</span></p>')
    srcs = ""
    if top:
        srcs = ('<p class="chapter-next-intro">The sources this chapter cites most, with the passages transcribed:</p><ul class="rh-cards">'
                + "".join(source_card(t, "../ref/") for t in top) + "</ul>")
    if not (nxt or srcs):
        return ""
    return f'<nav class="chapter-next" aria-label="Where next">{nxt}{srcs}<p class="rabbit-random"><a class="random-source" href="../ref/index.html">A random source \u2192</a></p></nav>\n'


LANG_NAMES = {"la": "Latin", "fr": "French", "it": "Italian", "de": "German", "es": "Spanish", "grc": "Greek", "el": "Greek"}
PARALLEL_RE = re.compile(
    r'<div class="parallel">\s*<div class="original"(?: lang="([a-z-]+)")?>(.*?)</div>\s*'
    r'<div class="rendering"([^>]*)>(.*?)</div>\s*</div>', re.DOTALL)


def fold_originals(body_html: str) -> str:
    """On source pages, show the English rendering first and fold the
    original-language text into a gwern-style collapsible block, so readers
    are not met by a wall of Latin. Only the plain two-column form is folded."""
    def sub(m):
        lang, original, rattrs, rendering = m.group(1), m.group(2), m.group(3), m.group(4)
        name = LANG_NAMES.get(lang or "")
        if not name or "<div" in original or "<div" in rendering:
            return m.group(0)
        return (f'<div class="parallel folded"><div class="rendering"{rattrs}>{rendering}</div>'
                f'<details class="original-toggle"><summary>Original {name}</summary>'
                f'<div class="original" lang="{lang}">{original}</div></details></div>')
    return PARALLEL_RE.sub(sub, body_html)


BACKLINKS = {}


def build_page(src_path: Path, out_path: Path):
    meta, body_md = parse_source(src_path)
    body_html = render_markdown(body_md)

    toc_html = build_toc(body_html)

    # Generated blocks, placed by an HTML comment in the Markdown.
    if "<!-- SOURCE-GALLERY -->" in body_html:
        grid, n = gallery_html()
        body_html = body_html.replace("<!-- SOURCE-GALLERY -->", grid)
    if "<!-- NEW-SOURCES -->" in body_html:
        body_html = body_html.replace("<!-- NEW-SOURCES -->", newest_sources_html())
    if "<!-- SOURCES-BY-CHAPTER -->" in body_html:
        body_html = body_html.replace("<!-- SOURCES-BY-CHAPTER -->", by_chapter_html())

    rel = src_path.relative_to(CONTENT)
    if rel.parts[0] == "ref":
        body_html = fold_originals(body_html)
    if rel.parts[0] == "ref" and src_path.stem != "index" and BACKLINKS.get(src_path.stem):
        section = rabbit_hole_html(src_path.stem) + backlinks_html(BACKLINKS[src_path.stem])
        marker = '\n<section class="footnotes"'
        body_html = (body_html.replace(marker, "\n" + section + marker[1:], 1)
                     if marker in body_html else body_html + section)

    if rel.parts[0] == "rationalism" and src_path.stem in CHAPTER_ORDER:
        box = chapter_next_html(src_path.stem)
        if box:
            marker = '\n<section class="footnotes"'
            body_html = (body_html.replace(marker, "\n" + box + marker[1:], 1)
                         if marker in body_html else body_html + box)

    # The 1865 edition's printer's ornament (redrawn as SVG): above the first
    # paragraph of a chapter, and again as a tailpiece where the text ends.
    if meta.get("fleuron"):
        ornament = env.get_template("fleuron.svg").render()
        body_html = f'<div class="fleuron-head">{ornament}</div>\n' + body_html
        tail = f'<div class="fleuron-tail">{ornament}</div>\n'
        marker = '\n<section class="footnotes"'
        if marker in body_html:
            body_html = body_html.replace(marker, "\n" + tail + marker[1:], 1)
        else:
            body_html += tail

    depth = len(out_path.relative_to(OUT).parts) - 1
    root = "../" * depth

    # Link previews: the page's title page or first picture, else a default.
    share_img = None
    for pat in (r'<figure class="[^"]*title-page[^"]*">.*?<img src="(?:\.\./)*(assets/img/[^"]+)"',
                r'<figure[^>]*>.*?<img src="(?:\.\./)*(assets/img/[^"]+)"'):
        m = re.search(pat, body_html, re.S)
        if m:
            share_img = m.group(1)
            break
    page_url = SITE_URL + str(out_path.relative_to(OUT)).replace("\\", "/")
    if page_url.endswith("/index.html") and depth == 0:
        page_url = SITE_URL

    template = env.get_template("base.html")
    context = dict(meta)  # title, subtitle, abstract, meta_rows, back_link, ...
    context.update(
        title=meta.get("title", SITE_NAME),
        description=meta.get("description", ""),
        body=body_html,
        toc=toc_html,
        root=root,
        site_name=SITE_NAME,
        github_repo=GITHUB_REPO,
        page_url=page_url,
        share_title=strip_tags(re.sub(r"<br\s*/?>", " ", str(meta.get("heading") or meta.get("title") or SITE_NAME))),
        share_desc=strip_tags(meta.get("description", "")).replace('"', "&quot;"),
        share_image=SITE_URL + (share_img or DEFAULT_SHARE_IMAGE),
    )
    html = template.render(**context)
    for stem, _name, words in CHAPTERS:
        tag = f"<!-- READTIME:{stem} -->"
        if tag in html:
            html = html.replace(tag, f'<span class="readtime">{reading_time(words)}</span>')
    html = (html.replace("<!-- SOURCE-COUNT -->", str(len(REFMETA)))
                .replace("<!-- GALLERY-COUNT -->", str(sum(1 for m in REFMETA.values() if m.get("thumb")))))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  {src_path.relative_to(ROOT)} -> {out_path.relative_to(ROOT)}")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    BACKLINKS.update(collect_backlinks())
    collect_refmeta()
    print("Rendering pages:")
    for src in sorted(CONTENT.rglob("*.md")):
        rel = src.relative_to(CONTENT)
        out = OUT / rel.with_suffix(".html")
        build_page(src, out)

    print("Copying assets:")
    shutil.copytree(ASSETS, OUT / "assets")
    print(f"  assets/ -> {(OUT / 'assets').relative_to(ROOT)}")

    # Tell GitHub Pages not to run Jekyll over the output (we pre-render
    # everything ourselves; Jekyll would otherwise ignore files/folders
    # starting with an underscore and mangle a few other things).
    (OUT / ".nojekyll").touch()

    # The list the random-source button draws from.
    import json
    sources = [[slug, m["title"], m["subtitle"]] for slug, m in sorted(REFMETA.items())]
    (OUT / "assets" / "js" / "sources.js").write_text(
        "window.LECKY_SOURCES=" + json.dumps(sources, ensure_ascii=False) + ";\n", encoding="utf-8")

    # Custom domain: GitHub Pages reads docs/CNAME. Keep the source copy at
    # the repo root, since docs/ is wiped on every build.
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")

    print("\nBuild complete:", OUT)


if __name__ == "__main__":
    main()
