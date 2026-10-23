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
FOOTNOTE_REF_RE = re.compile(r'<sup id="fnref:([^"]+)"><a[^>]*>(\d+)</a></sup>')


def render_markdown(body_md: str) -> str:
    html = markdown.markdown(
        body_md,
        extensions=["extra", "footnotes", "smarty", "sane_lists"],
        extension_configs={
            "footnotes": {"BACKLINK_TEXT": "↩"},
        },
    )

    # Pull each footnote's text out of python-markdown's bottom-of-page
    # <div class="footnote"> list and inline it as a margin sidenote right
    # after its reference marker instead -- true Tufte/gwern-style sidenotes,
    # not endnotes. (sidenotes.js, loaded separately, then positions these
    # in the margin and keeps them from overlapping each other.)
    notes = dict(FOOTNOTE_DEF_RE.findall(html))
    html = re.sub(r'<div class="footnote">.*</div>\s*$', "", html, flags=re.DOTALL)

    def inline_sidenote(m):
        note_id, number = m.group(1), m.group(2)
        note_html = notes.get(note_id, "")
        return (
            f'<sup id="fnref:{note_id}" class="footnote-ref">{number}</sup>'
            f'<span class="sidenote" id="sn:{note_id}">'
            f'<span class="sidenote-num">{number}</span>{note_html}'
            f"</span>"
        )

    html = FOOTNOTE_REF_RE.sub(inline_sidenote, html)
    return html


def build_page(src_path: Path, out_path: Path):
    meta, body_md = parse_source(src_path)
    body_html = render_markdown(body_md)

    depth = len(out_path.relative_to(OUT).parts) - 1
    root = "../" * depth

    template = env.get_template("base.html")
    context = dict(meta)  # title, subtitle, abstract, meta_rows, back_link, ...
    context.update(
        title=meta.get("title", SITE_NAME),
        description=meta.get("description", ""),
        body=body_html,
        root=root,
        site_name=SITE_NAME,
        github_repo=GITHUB_REPO,
    )
    html = template.render(**context)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  {src_path.relative_to(ROOT)} -> {out_path.relative_to(ROOT)}")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

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

    print("\nBuild complete:", OUT)


if __name__ == "__main__":
    main()
