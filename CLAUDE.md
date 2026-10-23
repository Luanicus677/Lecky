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

## Workflow: transcribing Rationalism in Europe (all of Vol. I is done; the same steps apply to Vol. II)

`content/rationalism/vol1-ch1.md` is COMPLETE: printed pages 1–150, footnotes `[^1]`–`[^167]`.
`content/rationalism/vol1-ch2.md` is COMPLETE: printed pages 151–205 ("THE MIRACLES OF THE CHURCH"; ends "...a cause of its advance."), footnotes `[^1]`–`[^25]`.
`content/rationalism/vol1-ch3.md` is COMPLETE: printed pages 206–385, footnotes `[^1]`–`[^184]`.
`content/rationalism/vol1-ch4.md` ("ON PERSECUTION. PART I. THE ANTECEDENTS OF PERSECUTION") is COMPLETE as far as Volume I goes: printed pages 386–447, footnotes `[^1]`–`[^45]`; the volume ends "...the soil of England for the last time stained with the misbeliever's blood!" followed by "END OF THE FIRST VOLUME." **Volume I is therefore finished (pp. 1–447).** Next: Volume II (Chapter IV Part II onwards; see Lecky's own contents list for vol. II in `index.md`). The OCR for vol. II must be downloaded; the likely archive.org id is `rationalismeuro02leckuoft` (the same University of Toronto series as vol. I; an HTTP 503 was returned at the last attempt, so check the id and retry). Vol. II printed page p will have its own leaf offset: find it by comparing a page header in the OCR with the image index. Latin, Greek and French in the notes of Chapters II–IV were checked against the scan.
Each chapter has its own sequential footnote series; the 1865 print restarts numbering on every page.
Printer's slips left as printed in ch. II and III ("interpretetion", "one the most common"): "Voltarian", "Lammenais", "Protestanism", "it all difficult", "deepseated", "developement".

1. Download the raw OCR (redirects, so use `-L`):
   `curl -sSL https://archive.org/download/rationalismeuro01leckuoft/rationalismeuro01leckuoft_djvu.txt -o <scratchpad>/lecky1.txt`
   In that file, Chapter III (page 206) starts at line 8678; Chapter IV at line 15626.
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

Source pages so far (`content/ref/`; also Middleton, see below): Grillandi (1 passage), Garinet (3: preface pp. xiii-xiv, pp. 38, 42),
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
  Also done: Cologne preface pp. 461-462 (on the Sprenger page; Dm4y leaves n535-n536) and Spina pp. 191, 299-300 (page `spina-quaestio-de-strigibus.md`; v1J2 leaves n170, n301-n302).
  Also done: Gerson De erroribus p. 253 = vol. II PART 2 (vW5E leaf n321; Lecky's note 82). Spina's p. 253 (part 1, leaf n230) is unrelated. Searched Spina part 1 for Lecky's 'rebellion in north Italy': not found (Quaestio p. 193 = leaf n172 Como figures; Apologia p. 278 = leaf n268 Peter Martyr; checked for notes 5 and 67). Note 5's rebellion/thousand come from Madden vol. i p. 305 (page `madden-phantasmata.md`; phantasmataorill01madd, p. 305 = image n354; the `_page_numbers.json` offset is wrong by 2). 1518 Venice 'rising': checked against Brambilla & Toffolo (Circolo Ghislandi PDF, citing Sanudo and ASVe Consiglio dei Dieci): it was the Council of Ten, not the people; see madden-phantasmata.md#venice-1518 and #sanudo-1518 (Sanudo Diarii vol. XXV, archive id idiariidimarinos25sanu: 14 July entry confirmed; 31 July entry has nothing on Val Camonica; 23 August entry lists five valley delegates asking the inquisition to continue). The Council of Ten's 31 July 1518 letter (ASVe Misto reg. 42 cc. 128v-129r) is transcribed in that PDF (sc.txt lines ~2037-2110): it confirms an earlier stop order; Del Col not online. Thiers p. 138 (1741 ed., not online) checked in the 1697 printing bub_gb_sn7cWyefS5AC pp. 139-140: only papal bulls.
  Not done: Cologne doctors' signatures (pp. 463-468), Lecky's 'rebellion in north Italy' (not found on p. 191/299/300), Nider "p. 522" (not matched).
  The OCR of these Google Books scans is very poor (long s); locate passages with `_djvu.xml` and read the images.
- Garinet: other cited pages (6, 14-15, 35, 39, 45, 75, 121-122, 256, 298-302) are not transcribed. Do not trust `_page_numbers.json`
  for this scan: p. 38 is `n95`, p. 41 is `n98`, p. 42 is `n99`.
- Middleton, Free Inquiry (`middleton-free-inquiry.md`): Dublin 1749 printing `freeinquiryintom00midd` (image index n = djvu object order, p. xv = n22, p. lxxxiv = n89, pp. 85-87 = n232-n234; long-s OCR, search for 'surprizing', 'explicitely'). Done: Ch. II notes 3, 10, 11. Not done: ch. IV note 25 (Introd. p. 86 'ninety heresies') and note 37; the London printings' pagination is unchecked.
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
