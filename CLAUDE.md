# Lecky edition: notes for Claude sessions

A reading edition of W. E. H. Lecky's works, modelled as closely as possible on gwern.net.
Live at https://luanicus677.github.io/Lecky/ (GitHub Pages serves `docs/` from `main`).
README.md explains the build, the Markdown conventions, and the source-page layout. Read it first.

## The owner

- Not a programmer. When they need to click something, give exact directions
  (e.g. "top nav of your repo, right after 'Insights'").
- Wants criticism, not agreement; concise, explicit answers. After long replies, suggest a good follow-up question.
- Pays per session from limited credits. Keep each session to one well-scoped batch, avoid re-reading
  large files unnecessarily, and don't take screenshots beyond what verification needs.
- Wants gwern.net fidelity, and rabbit holes *within the site*: every work Lecky cites should eventually
  get a source page with the passage transcribed, translated, and linked to a scan.

## Ground rules for the text

- Lecky's text is never corrected. OCR errors are fixed; Lecky's own errors are discussed on source pages
  (e.g. his "fifteenth century" for Grillandi) and left as printed.
- Translations, links, and notes are editorial: `span.translation.editorial` for translations, and source pages
  for commentary. Translations are this edition's own drafts and say so.
- Never invent a citation, a page number, or a reading. Verify against a scan (archive.org page images) or
  label it as unverified.

## Workflow: transcribing Rationalism in Europe (Vol. I, Chapter I is done; the same steps apply to Chapter II onward)

`content/rationalism/vol1-ch1.md` is COMPLETE: printed pages 1–150 (the chapter ends at the bottom of page 150,
"...which the spirit of Rationalism has destroyed."). Footnotes are `[^1]`–`[^167]`. Chapter II starts on printed page 151
("CHAPTER II. ... THE MIRACLES OF THE CHURCH"; OCR line ~6655; page 151 is `n180` in the image index).
One sequential series for the whole chapter; the 1865 print restarts numbering on every page.

1. Download the raw OCR (redirects, so use `-L`):
   `curl -sSL https://archive.org/download/rationalismeuro01leckuoft/rationalismeuro01leckuoft_djvu.txt -o <scratchpad>/lecky1.txt`
   In that file, Chapter II (page 151) starts near line 6655, after the end of Chapter I on page 150.
2. `python3 tools/clean_ocr.py <file>` gives a first pass. It is not sufficient: hand-check every page.
   Common faults: dropped hyphens where both halves are real words ("con science"), misread
   Latin and French ("cteteris", "Christ!", "feterni"), and running headers injected mid-text.
3. Footnotes: in the OCR, a page's notes follow its main text. A note that runs over a page break continues
   *after the next page's main text*; stitch it by grammatical continuity. Check doubtful spots against
   the page image: `https://archive.org/download/rationalismeuro01leckuoft/page/n<leaf>.jpg`
   (use `_page_numbers.json` to map printed page to leaf; the image index is leaf − 1, i.e. printed page p is `n<p+29>` in this part of the book).
4. Update the chapter's `description` and `Status` meta row to the new page range, and update
   `content/rationalism/index.md` and `content/about.md` if the status wording there changes.

## Workflow: source pages (`content/ref/`)

Model: `content/ref/grillandi-de-sortilegiis.md`. For a cited work:
- Search archive.org (`https://archive.org/advancedsearch.php?q=...&fl[]=identifier&output=json`), download
  `<id>_djvu.txt`, and grep for the quoted words. Map a text offset to a page with
  `<id>_hocr_pageindex.json.gz` and `<id>_hocr_searchtext.txt.gz`, then read the page image
  (`/download/<id>/page/n<i>.jpg`) to confirm by eye. Scan links: `https://archive.org/details/<id>/page/n<i>/mode/2up`.
- Page shape: `meta_rows` (author, work, editions with scan links, "Cited in" backlinks, status); an abstract
  (a YAML `abstract: |` block: unquoted colons break YAML); each passage in `<section id="...">` with
  `div.parallel > div.original[lang] + div.rendering`, the words Lecky quotes wrapped in `span.cited-passage`;
  a collation table when Lecky's quotation differs from the source.
- Raw HTML blocks skip the smart-quotes pass: type curly quotes and apostrophes yourself in them and in front matter.
- Link from Lecky's footnote with `<a class="popup-ref" href="../ref/<page>.html#<section-id>">`.
  Link people to Wikipedia (`https://en.wikipedia.org/wiki/...`); popups and icons are automatic.
- Add the page to `content/ref/index.md`.

Source pages so far (`content/ref/`): Grillandi (1 passage), Garinet (3: preface pp. xiii-xiv, pp. 38, 42),
Bodin's Demonomanie (3: pp. 15, 151-152, Refutation near p. 252), Codex Theodosianus IX.16 (laws 4 and 6).
Notes for continuing:
- Bodin: use the 1582 Paris printing (`per_witchcraft-in-europe-and-america_bodin-jean_1582_125`); its pagination matches Lecky's
  pp. 15 and 152 (image index = leaf; p. 15 is `n52`, pp. 151-152 are `n332`-`n333`). The OCR is poor, so locate passages with
  `<id>_djvu.xml` (split on `<OBJECT`), then read the page image. Not yet done: Bodin pp. 40, 107, 109, 217, 228.
- Codex Theodosianus: Ritter, Leipzig 1738, vol. III is `BRes1409273` (law 4 on p. 128 = `n143`; law 6 on pp. 133-134 = `n148`-`n149`).
  Laws 1-3, 5 and 7 (cited in ch. I notes 26, 27, 32) are not transcribed.
- Malleus Maleficarum: Lecky's "Mall. Mal. vol. i/ii" matches the Lyon 1620 edition (NOT checked against Lyon 1669 vol. II: no readable scans).
  Vol. I = `bub_gb_Dm4ywfjNpVUC` (Cologne documents of 1487 at pp. 459-467 = leaves `n533`-`n541`).
  Vol. II part 1 = `bub_gb_v1J2VHKuIVEC` (Gerson, De probatione spirituum, begins p. 77 = `n109`; Spina, Quaestio de strigibus from ~p. 181 = `n160`).
  Vol. II part 2 = `bub_gb_vW5EtV4e8MgC` (Grillandus, Tractatus de sortilegiis, from p. 381 = `n460`; pp. 393-394 = `n472`-`n473`).
  The two parts of vol. II are paged separately, so "vol. ii. p. 77" is ambiguous (Gerson in part 1; Ananias in part 2).
  Done: the Grillandus physicians passage (on the Grillandi source page, with an edition table).
  Also done (page `sprenger-malleus-maleficarum.md`, vol. I = Dm4y): Pars I Quaest. III p. 32 (leaf n77, Paul/angels/incubi; Lecky says Quaest. 4),
  Pars II Quaest. II cap. I p. 273 (n312, hair), cap. VI pp. 300, 305 (n352, n355, baptismal exorcism). In Dm4y printed page = leaf - 45 near p. 32; leaf - 39 near p. 273.
  Also done: Gerson p. 77 (page `gerson-de-probatione-spirituum.md`; vol. II part 1 = v1J2, leaf n108).
  Not done: Spina pp. 191, 253, 299, 300, the Cologne text, Nider "p. 522" (not matched).
  The OCR of these Google Books scans is very poor (long s); locate passages with `_djvu.xml` and read the images.
- Garinet: other cited pages (6, 14-15, 35, 39, 45, 75, 121-122, 256, 298-302) are not transcribed. Do not trust `_page_numbers.json`
  for this scan: p. 38 is `n95`, p. 41 is `n98`, p. 42 is `n99`.
- Thiers, Wier, Maury, Michelet, Madden are cited often but have no source pages.

## Build, test, deploy

- `python3 build.py` regenerates `docs/` (commit `docs/` too; never hand-edit it).
- Preview: `cd docs && nohup python3 -m http.server 8911 >/dev/null 2>&1 &` (start it on its own; never combine
  `pkill` with other commands in one shell call, as it kills the shell).
- Playwright: `require('/opt/node-tools/node_modules/playwright')`, launch with
  `executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'`, and use `hasTouch: false` for hover tests.
  Scroll the element into view and wait before hovering: scrolling closes popups by design, and
  Playwright's auto-scroll otherwise fires just after the hover.
- Wikipedia's API sometimes rate-limits this cloud machine (HTTP 429); that is not a site bug.
- Commit to `main` and push (`git push -u origin main`). Pages redeploys in about a minute.
