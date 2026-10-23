# lecky

A reading edition of William Edward Hartpole Lecky's works, in the spirit of
[gwern.net](https://gwern.net)'s [design principles](https://gwern.net/design):
minimalist typography, margin sidenotes, hover-popups for footnotes and
cross-references, and progressive disclosure for long digressions — built so
a reader can follow a citation out of Lecky's text and into the primary
source itself.

**Status:** scaffold only. Layout, typography, footnotes, sidenotes, and the
popup system are built and working; the chapter text currently on the site
is placeholder filler, clearly marked. See `/about` on the published site
for the real status and next steps.

## How this is built

Content is written as Markdown (with a YAML front-matter header) in
`content/`. `build.py` renders it through the Jinja2 template in
`templates/base.html` and writes static HTML into `docs/` — which is what
GitHub Pages actually serves. There is no build step on GitHub's side; the
generated HTML is committed directly, so the published site is exactly what
was generated locally.

```
content/            Markdown source, one file per page
  index.md            homepage
  about.md             status page
  rationalism/         "Rise and Influence of Rationalism in Europe"
    index.md            book table of contents
    vol1-ch01.md         a chapter

templates/base.html  single Jinja2 template; per-page header fields
                      (title, subtitle, abstract, meta_rows, back_link,
                      placeholder_notice) come from each file's front matter

assets/              CSS, JS, self-hosted fonts — copied into docs/ as-is
docs/                generated output — served by GitHub Pages, do not
                      hand-edit, rebuild instead with `python3 build.py`
```

### Rebuilding the site

```sh
pip install -r requirements.txt
python3 build.py
```

### Adding a new page

Create a `.md` file under `content/`, with front matter at minimum:

```yaml
---
title: Page title
description: One-line description for search engines / social previews
heading: What to show as the <h1> (defaults to title if omitted)
---
Body text in plain Markdown. Footnotes use [^name] / [^name]: syntax.
```

Optional front-matter fields: `subtitle`, `abstract` (shown in a bordered
box under the title), `meta_rows` (a list of `[label, value]` pairs shown as
a metadata table), `back_link` (`{url, text}`, shown above the title),
`placeholder_notice` (shown as a dashed warning box — remove once real text
replaces a placeholder), `is_home: true` (suppresses the site-name suffix in
the browser tab title).

Markup conventions used inline in the Markdown body:

- Footnotes: standard Markdown footnote syntax, `text[^id]` ... `[^id]: note text`.
- Dropcap: `<span class="dropcap">T</span>here is...` on a chapter's opening paragraph.
- Small caps: `<span class="sc">TEXT</span>`.
- Margin sidenote: `<span class="sidenote-wrap"><span class="sidenote"><span class="sidenote-num">*</span>note text</span></span>`.
- Cross-reference hover-popup: `<a class="popup-ref" href="...">text</a>` — on hover, fetches the
  linked same-site page and shows its `.abstract` (or the element matching the link's `#fragment`) in a floating preview.
- Collapsible aside: `<details class="collapse"><summary>Label</summary>...</details>` (needs no JS).

## Hosting

GitHub Pages, configured to serve from the `main` branch's `/docs` folder
(Settings → Pages → Build and deployment → Deploy from a branch → main /docs).
No GitHub Actions workflow is needed for this since the HTML is pre-built
and committed.

## Fonts

Body text is set in [EB Garamond](https://github.com/octaviopardo/EBGaramond12)
(SIL Open Font License 1.1), self-hosted from `assets/fonts/` — see
`assets/fonts/EB-GARAMOND-LICENSE.txt`.

## License / attribution

Lecky's own writing, and the primary sources he cites, are in the public
domain. Where a specific scan or edition is used as the source for a
transcription, it is credited on that page. The site design, build tooling,
and original commentary are this project's own work.
