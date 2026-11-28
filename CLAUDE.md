# Lecky edition: notes for Claude sessions

A reading edition of W. E. H. Lecky's works, modelled as closely as possible on gwern.net. Live at https://readlecky.com/
(GitHub Pages serves `docs/` from `main`; DNS at Porkbun; the repo-root `CNAME` is copied into docs/ by build.py; the old
luanicus677.github.io/Lecky/ address redirects). README.md explains the build and Markdown conventions.

**Read next, only when needed:** `notes/source-log.md` (the full working log to 28 Nov 2026: every scan id, printed-page/image
offsets, findings, and the DEAD ENDS list; grep it for an author before searching for a book) and `notes/run-log.md`
(one entry per session, newest last; read the last entry to see where work stopped).

## The owner
- Not a programmer. When they need to click something, give exact directions ("top nav of your repo, right after 'Insights'").
- Wants criticism, not agreement; concise, explicit answers. After long replies, suggest a good follow-up question.
- Pays from a Claude Pro plan (weekly limit). Keep each session to one well-scoped batch; avoid re-reading large files; screenshots
  only where verification needs them.
- Wants gwern.net fidelity, and rabbit holes *within the site*: every work Lecky cites should get a source page with the passage
  transcribed, translated, and linked to a scan. Goal: every footnote that cites a work links to a source page.

## Ground rules
- Lecky's text is never corrected. OCR errors are fixed (check on Lecky's page image: `python3 tools/lecky_line.py 1|2 out.jpg
  "words"`); Lecky's own slips are left as printed and recorded on `content/rationalism/as-printed.md`; his errors of fact
  are discussed on source pages and, when substantive, on `content/rationalism/lecky-and-his-sources.md`.
- NOT slips, never normalise: "develope" and "developement" (1865 house spelling); "development" occurs 3x in vol. II as printed.
- Never invent a citation, page number, reading, date or biographical fact. Verify on a scan, or label it unverified/"from the OCR"/
  "our identification". Facts from memory must be checked or left out.
- Translations are this edition's drafts and say so (`p.editorial-note` "Translation: this edition's draft.").
- Only public-domain material goes to Muse (see below); never put keys in code, chat or env vars.

## State of the text
All of *Rationalism in Europe* is transcribed: `content/rationalism/vol1-ch1..ch4.md`, `vol2-ch4..ch6.md` (vol. II ch. IV is
Part II of the persecution chapter). Each chapter numbers its footnotes `[^1]`... sequentially (the 1865 print restarts per page).
Scans: vol. I `rationalismeuro01leckuoft` (printed p ~ image n-29), vol. II `rationalismineur02leckuoft` (p = n-15).
Readability layer (editorial `## headings {: #id }` with Lecky's analytical contents in `p.section-argument`, figures, fleuron,
drop caps, TOC, sidenotes) exists in all chapters: never split or reword Lecky's paragraphs.

## Source pages (`content/ref/<slug>.md`)
Workflow for a footnote:
1. `python3 tools/coverage.py --todo` lists unlinked notes that cite a work. Grep notes/source-log.md for the author first.
2. Find the book: `https://archive.org/advancedsearch.php?q=...&fl[]=identifier&fl[]=title&fl[]=date&rows=30&output=json`.
   Prefer Lecky's own edition (match his page numbers). Download `<id>_djvu.txt` (curl -sSL, retry: archive.org sometimes
   returns a tiny error page) and grep for distinctive words (long-s OCR reads s as f: try both spellings).
3. Map text to an image: range-fetch `<id>_djvu.xml` (`curl -r` at the same fraction of the file as the line in the txt), split on
   `<OBJECT`, read `usemap="..._NNNN.djvu"` (regex `usemap="[^"]*_(\d{4})\.djvu"`; ids contain years). The image is n = object
   or object-1 (varies): fetch with `tools/ia_page.sh ID N out.jpg` and CHECK THE PAGE HEADER on the image.
4. Read the passage on the image (not just the OCR). Crop a facsimile with `tools/gbox.py` (word bounding boxes; eye estimates
   from preview thumbnails are ~10% off). Huge images: `Image.MAX_IMAGE_PIXELS=None`. Title pages: `<id>_scandata.xml`
   (`<pageType>Title</pageType>`), or fetch a few early leaves into one contact sheet and look once.
5. Write the page, link the note, add it to `content/ref/index.md`, build, `python3 tools/make_thumbs.py`, build again.

Page shape (model: `content/ref/temple-observations-united-provinces.md`, `cyprian-epistle-62.md`):
- Front matter: `title`, `description`, `heading`, plain-English `subtitle` (quote it if it has a colon), `back_link`,
  `meta_rows` (Author with Wikipedia link; Edition used with archive id, page = image links `https://archive.org/details/<id>/page/n<i>/mode/2up`,
  whether it is Lecky's edition; Cited in; Status: what was read on images vs OCR), `abstract: |` (plain-English nugget first:
  what is surprising, what Lecky got right or wrong; HTML attributes inside it use plain `"`, not `\"`).
- Body: `<section id="..." class="passage">` with `h2`, `p.passage-source`, `figure.facsimile` (crop ~1000px wide JPEG q80 in
  `assets/img/ref/`, caption + `span.credit` "Scan: Internet Archive · public domain") or `figure.title-page`, then the text:
  `div.parallel > div.original[lang] + div.rendering` for foreign languages (the build folds the original), or a `blockquote`
  for English; Lecky's words wrapped in `span.cited-passage`; `table.collation` when his quotation differs.
- Raw HTML skips the smart-quote pass: type ’ ‘ “ ” yourself (a straight ' right after a closing tag renders wrongly).
- Footnote link: `<a class="popup-ref" href="../ref/<slug>.html#<section-id>">...</a>` around the citation words. Work-level
  links (no #) are allowed when the passage is not identified. Backlinks on source pages are automatic.
- Index entry in `content/ref/index.md`: `<li>` with `div.work-title` (link + `span.work-status`) and `div.work-desc`.
- Good nuggets go into `content/curiosities.md` (1-3 sentences, checked against the transcribed passage, ending with a
  popup-ref link); substantive disagreements into `content/rationalism/lecky-and-his-sources.md` (sections: The source says
  something else / The right words, the wrong speaker / Stronger than the source / Dates, figures and names / Wrong chapter, wrong page).
- Where Lecky gives no page, say the passage is "our identification". Do not claim his edition unless his pages match.

Other sources: Migne PL volumes are `bim_early-english-books-1641-1700_patrologiae-cursus-completus-_<year>_<vol>` (two columns
per page: crop each column). EEBO/ECCO scans are `bim_...`. Wikipedia popups are automatic for en.wikipedia links (check the
article exists: curl status, 1 s apart). Gutenberg/Wikisource texts may be used, labelled "text, not a scan". This machine cannot
read Gallica, HathiTrust or Google Books page images: books only there go on the owner's list (see source-log DEAD ENDS).

## Tools
- `python3 build.py` regenerates `docs/` (never hand-edit docs/; commit it). Also writes sitemap.xml/robots.txt.
  After a container restart: `pip install -r requirements.txt`.
- `tools/coverage.py [--todo]`, `tools/linkcheck.py` (run after big edits), `tools/make_thumbs.py`, `tools/ia_page.sh`,
  `tools/gbox.py`, `tools/lecky_line.py`, `tools/hunt.py` (Muse full-text hunt for paraphrased quotations; try grep first).
- Muse (`tools/muse.py`, Meta's model; key is a network secret added by the proxy): public-domain text only; first drafts and
  bulk searching only; never trust its page numbers or flags unverified. Cap: about $0.20 per session.
- Preview: `cd docs && nohup python3 -m http.server 8911 >/dev/null 2>&1 &`. Playwright: `require('/opt/node-tools/node_modules/playwright')`.
- Never put `cat` without a file in a shell chain; never combine `pkill` with other commands.
- Commit to `main` and push (`git push -u origin main`, retry on network errors). Pages redeploys in about a minute.

## Scheduled runs
A scheduled task wakes the worker session twice a day (02:43 and 14:43 Europe/Dublin). Each run follows its stored prompt:
about 45 minutes, the next batch from `tools/coverage.py --todo`, verified source pages, commits to main, an entry in
notes/run-log.md. Unattended runs must not create or change scheduled tasks, environments or network settings, must not
spend more than ~$0.20 on Muse, and write anything needing a human decision under "Questions for the owner" in the run log.
