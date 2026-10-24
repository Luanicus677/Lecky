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
`content/rationalism/vol1-ch4.md` ("ON PERSECUTION. PART I. THE ANTECEDENTS OF PERSECUTION") is COMPLETE as far as Volume I goes: printed pages 386–447, footnotes `[^1]`–`[^45]`; the volume ends "...the soil of England for the last time stained with the misbeliever's blood!" followed by "END OF THE FIRST VOLUME." **Volume I is therefore finished (pp. 1–447).** Next: Volume II (Chapter IV Part II onwards; see Lecky's own contents list for vol. II in `index.md`). Volume II: archive.org id `rationalismineur02leckuoft` (NOT `rationalismeuro02...`), printed page p = image n(p+15); raw OCR line numbers in `<id>_djvu.txt`: Ch. IV Part II lines 387–4413 (pp. 1–105), Ch. V from line 4414 (p. 106), Ch. VI from line 9842 (p. 250). `content/rationalism/vol2-ch6.md` (Ch. VI, 'The Industrial History of Rationalism') is COMPLETE: pp. 250-409 (the end of the text; Lecky's index follows and is NOT transcribed), footnotes `[^1]`-`[^189]`. **All of Rationalism in Europe (pp. 1-447 of vol. I, 1-409 of vol. II) is now on the site.** Ch. VI notes: Latin/French/Italian were corrected by grammar and a few image checks only (n352 Malone p. 9; image n = printed page + 15); NOT read letter-by-letter: treat accents and ligatures in notes 25-27, 36, 46, 49, 57, 70, 117, 171, 188 as provisional. Printer's slips left: 'his named erased' (p. 350), 'Eenan'-type OCR errors fixed. Page-header regex needed widening in build6.py for ch. VI (header misreads like 'EAT10NALISM', 'HISTOEY'). Possible next work: proof the Latin/French notes of ch. VI against images; footnote source pages for vol. II (Mariana, Suarez, Bianchi, Concina, Sarpi etc.). `content/rationalism/vol2-ch5.md` (Ch. V, 'On the Secularisation of Politics') is COMPLETE: pp. 106-249, footnotes `[^1]`-`[^140]`; the 1865 print numbers footnotes per page, a page with ONE note may leave it unnumbered (OCR then puts it in the body), and a long note's overflow can sit after the next page's body (ch. V notes 86, 140 were fixed by hand). Page images: image n = printed page + 15 throughout. Latin/French/Italian notes were checked on images except notes 5, 12, 20, 26-27, 37-40, 44, 46-51, 54, 57-59, 62-64, 69-82, 84-95, 97-116, 119-130, 133-139 (English or short citations, only OCR-checked). Ch. V Latin checks: Suarez (notes 34-45), Mariana (52-60), Toletus/Sa/Molina/Ayala (65-68). `content/rationalism/vol2-ch4.md` is COMPLETE (pp. 1–105, footnotes `[^1]`–`[^100]`). Vol. II pipeline pitfalls: running headers missed by the cleaner; footnote that overflows a page continues after the NEXT page's body (sometimes merged into the same block: telltale is a cut word like 'ChrisInquisition'); two notes sometimes merge (split by hand); `* `, `l ` and `4 ` are misread opening quotes; OCR drops accents and Latin ligatures (Lecky prints æ, œ, é, è), so Latin and French notes must be read on the page images. Printer's spelling left as printed: 'Homooisians', 'Cluten' (read as printed on n68; unverified identity), 'Clebergius'. Not viewed on images (ligatures inferred from OCR): Farinacius 'laesae majestatis humanae' in note 43. Vol. II printed page p will have its own leaf offset: find it by comparing a page header in the OCR with the image index. Latin, Greek and French in the notes of Chapters II–IV were checked against the scan.
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
  `<id>_djvu.xml` (split on `<OBJECT`), then read the page image. Done: pp. 40 (God 'au grand nez', f. 40 = n102), 217-218 (n468-n469) and 228 (n490); Bodin's page numbers are FOLIOS (recto + verso images). Not yet done: Bodin pp. 107, 109.
- Codex Theodosianus: Ritter, Leipzig 1738, vol. III is `BRes1409273` (laws 1-2 on p. 123 = `n138`; law 3 on p. 125 = `n140`; law 4 on p. 128 = `n143`; law 6 on pp. 133-134 = `n148`-`n149`; law 7 on p. 136 = `n151`; image index = djvu object - 1).
  Done: laws 1-4, 6, 7 (ch. I notes 26, 27, 28, 32). Law 5 is not transcribed (Lecky only cites it in a run, 'l. 4, 5, 6'). Lecky's law 3 summary adds 'snow' and 'tempests', which are not in the Latin.
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
  Also done (ch. I notes 68, 78, 79; sections femina-65, maleficiendo-26, diabolus-41, sylvanus, serenus-503 on the Sprenger page; Dm4y images): p. 26 = n71 (maleficiendo seu male de fide sentiendo), p. 41 = n84 (diabolus; page number smudged), p. 65 = n106 (femina), Pars II Q. I cap. XI = n260 (Silvanus; page number cut off), Nider Formicarius extracts pp. 503-504 = n577-n578 (Serenus, Equitius, Helias). Lecky's 'Pars I Quaest. vii' for Serenus/Equitius is not matched (p. 77 = n118 has nothing; rest of Q. VII unread). Page numbers in this scan are irregular (p. 35 = n83, p. 47 = n85, p. 65 = n106): match by running title and content, not by an offset.
  Not done: Cologne doctors' signatures (pp. 463-468), Lecky's 'rebellion in north Italy' (not found on p. 191/299/300), Nider "p. 522" (not matched).
  The OCR of these Google Books scans is very poor (long s); locate passages with `_djvu.xml` and read the images.
- Garinet: other cited pages (6, 14-15, 35, 39, 45, 75, 121-122, 256, 298-302) are not transcribed. Do not trust `_page_numbers.json`
  for this scan: p. 38 is `n95`, p. 41 is `n98`, p. 42 is `n99`.
- Middleton, Free Inquiry (`middleton-free-inquiry.md`): Dublin 1749 printing `freeinquiryintom00midd` (image index n = djvu object order, p. xv = n22, p. lxxxiv = n89, pp. 85-87 = n232-n234; long-s OCR, search for 'surprizing', 'explicitely'). Done: Ch. II notes 3, 10, 11 and ch. IV note 25 (Introd. p. lxxxvi footnote [t], `#ninety-heresies`; scan n91 = p. lxxxvi, i.e. image index = XML object index minus 1 here). The London printings' pagination is unchecked.
- Chrysostom (`chrysostom-de-sacerdotio.md`): Lecky's ch. IV note 37 'panegyric on the habit of telling lies in St. Chrysostom On the Priesthood' gives no chapter; identified (inference) as Book I ch. VIII ('Great is the power of deceit'). Cowper 1866 translation `sjohnchrysostom00johngoog` (p. 19 = n46, p. 24 = n51, p. 25 = n52; the OCR misnumbers paragraphs, the print has 57-58, 73-75). Greek not checked. Augustine (`augustine-contra-mendacium.md`): Contra mendacium cc. 1-2 = Migne PL 40 cols. 519-520, archive id `bim_early-english-books-1641-1700_patrologiae-cursus-completus-_1845_40` (image n261; Latin from augustinus.it, checked on the image; Retractationes II.60 only in NPNF English, unchecked). The page has a side-by-side with Chrysostom. Rest of note 37 (Coleridge, Maury p. 268) is not on source pages.
- Agobard Liber de imaginibus (`agobard-de-imaginibus.md`): Baluze 1666 = `bub_gb_gOkJ5k0uktIC` (p. 244 = n327, 247 = n330, 248 = n331, 254 = n337, 264 = n347, 267 = n350; image = djvu object - 1). Lecky's pagination (Paris 1605, one vol.) is 10-13 lower than Baluze's. Other Baluze scans: `bub_gb_EcIfKlL_urIC`, `bub_gb_HKNfSIcAlHQC` (has Valois's notes), `bub_gb_ck3AGLRdEREC`.
- More source pages added in the long autonomous stretch (all English or Latin, verified on page images unless the page says otherwise): tertullian-de-baptismo (PL 1 n616, n618), tertullian-apologeticum (PL 1 n267), tertullian-de-anima (PL 2 `..._1844_2` n329), minucius-felix-octavius (`octavius00minu`, p.175 = n220, p.176 = n221), luther-de-servo-arbitrio (`bub_gb_Sp8ZXu8IePYC`, 1664 annotated ed.; p. = image n - 25; Lecky's "Hoc fulmine" quotation, note IV.32, NOT done), hecker-epidemics (`epidemicsofmiddlin00heck`: p.30 = n61, p.88 = n119, p.89 = n120; image = djvu object - 1; Lecky's page numbers differ), dalyell-darker-superstitions (`darkersuperstit00dalygoog`: image n = page + 16; pp. 623, 624, 644, 645 done; pp. 657, 669, 670 and the bridle p. ~641 not done; pricker pp. 641-643 only via OCR).
- Tried and abandoned: Cosmas Indicopleustes (Montfaucon Nova collectio tom. II: `bub_gb_XVCw0n6PM-wC` is the Eusebius volume, not Cosmas), Fulgentius De fide in PL 65 (`..._1858_65` does not contain it; try `bub_gb_hZ5lpQgaOtIC` / `bub_gb_1-mXL1IBSrIC` with other search terms), Binsfeld 1591 scan (`per_witchcraft...binsfeld_1591_110`, only 158 objects), Palmer (not started).
- Helper scripts live in the session scratchpad only (loc.py: regex over a cached djvu.xml giving the image index; img.py: fetch, crop and resize a page image). Re-create if needed.
- Tertullian De spectaculis c. 30 (`tertullian-de-spectaculis.md`): Migne PL 1 (`bim_early-english-books-1641-1700_patrologiae-cursus-completus-_1844_1`, cols. 659-660 = n347, 661-662 = n348; image index = djvu object - 1). Lecky's note 3.152 quotation differs from Migne in a few places (collated on the page).
- Augustine De civitate Dei (`augustine-de-civitate-dei.md`): Migne PL 41 (`..._1846_41`, XIX.6 col. 633 = n316; XXII.8 cols. 767-768 = n383). Five restorations to life are all on cols. 767-768 (§§ 15-19); the seventy are libelli, not miracles.
- Aquinas Suppl. q. 94 a. 1 (`aquinas-summa-supplement.md`): Opera vol. 25 (`bub_gb_InJN3guK7vwC`, p. 428 = n470). Lecky's note 3.150 Latin is a paraphrase, not a verbatim sentence.
- Simancas (`simancas-de-catholicis-institutionibus.md`): only 1575 Rome editions found online (`bub_gb_n-Ktt0tILHMC`, also `AFD0229`; 1692 Opera `bub_gb_cUhD5jRglLAC`); no 1569 copy. Lecky's p. 365 (fides) matches the 1575 pagination, but his torture pages (297-309, 305) do not: torture is Titulus LXV, pp. 494-513 (Vives p. 495, Spain p. 506). Page images viewed: 365, 366, 494, 495, 506. The 'vivid description of modes of torture' is not confirmed; pp. 497-513 only keyword-scanned.
- Thiers, Wier, Maury, Michelet, Madden are cited often but have no source pages.

- Volume II source pages: `mariana-de-rege.md` (1605 Mainz ed. `bub_gb_FNnUXWPFQEcC`, image n = printed page + 30; ch. V notes 52-60; the sentence 'Nos tamen non quid facturi sint homines...' in note 60 NOT found; 1599 Toledo ed. not seen) and `suarez-defensio-fidei.md` (Vivès vol. 24 `rpfranciscisuare24suar`, image n = page + 19; lib. vi cap. 4 at pp. 680-682; notes 34, 41-43, 45). Not done: Toletus, Sa, Molina, Ayala (`balthazarisayala01ayal`, `dejureetofficiis01ayaluoft`; Molina `rplodouicimolina0Nmoli`), Concina (no scan found), Sarpi, Bianchi, Troplong.

- Also Vol. II: `buchanan-de-jure-regni.md` (1581 ed., p. 16 = image n15; ch. V note 83; poor microfilm, read on image) and `bossuet-defensio-declarationis.md` (1745 ed. vol. 1 `defensiodeclarat01boss`, image n = page + 65; p. 128 Abimelech, note 96). Bossuet note 77 ('Defensio lib. i. c. 15, 16', wolves/sheep) NOT located; Lecky's 'lib. i. c. 3' does not match this edition's chapter numbering. Other scans found (unused): Bianchi 1745-46 Italian `bub_gb_p6UbBtH6D1cC`; Hotman Franco-Gallia 1665 `bub_gb_8IPQdc7m1ukC`; Troplong `bub_gb_GvGwHmfT9LwC`; Desprez de Boissy `lettressurlesspe01desp`; Lebrun `discourssurlacom00lebr`; Bedarride `lesjuifsenfranc00beda`; Eymericus 1607 `10488917bsb`.

- Also Vol. II: `ayala-de-jure-et-officiis-bellicis.md` (Carnegie 1912 reprint of the 1582 text, `dejureetofficiis01ayaluoft`, image n91; ch. V note 68; verbatim; page number and chapter not read). Note: new source-page front matter with a colon in `subtitle:` must be quoted (YAML).

- Also Vol. II: `molina-de-iustitia-et-iure.md` (vol. 4 `rplodouicimolina04moli`, pp. 539-540 = image n27; ch. V note 67; Lecky's Latin is a compressed paraphrase omitting Molina's qualifications). Toletus and Sa (notes 65-66) still not done.

- Also Vol. II: `toletus-instructio-sacerdotum.md` (1625 ed. `bub_gb_KyxnUbkc4K0C`, p. 378 = image n426 = page+48; note 65; chapter number not checked; Lecky's 'p. 653' is another edition) and `sa-aphorismi-confessariorum.md` (1599 ed. `bub_gb_5AK7-pKY-O8C`, p. 308 = n309; note 66, verbatim). Toletus's claim 'made a cardinal in 1583' in Lecky's text: Toledo was made cardinal in 1593 (from memory, unchecked). So all of ch. V notes 65-68 are done.

- Also: `lebrun-discours-sur-la-comedie.md` (1731 ed. `discourssurlacom00lebr`, p. 259 = n312 = page+53; ch. VI note 143) and `montaigne-essais-ii-12.md` (Courbet-Royer 1900 vol. 3 `19essaispublis03montuoft`, p. 179 = n192; ch. V note 117; Lecky reads 'imprudence', text 'impudence'). Still undone Latin/French notes: Hobbes Leviathan (V.118), Rousseau Contrat social IV.8 (IV.81), Beza/Castellio (IV.68-70, 73), Jurieu (IV.62-63), Bossuet Variations (IV.75), Eymericus (IV.40-42), Farinacius (IV.43), Ventura (V.28), Sarpi (V.11), Bianchi French (V.131), ch. VI Leo X bull/Augustine sermon/Turgot (notes 27, 36, 49, 57).

- Also: `rousseau-contrat-social-iv-8.md` (1903 critical ed. `ducontratsocialt00rous`, pp. 331-333 = n334-n336 = page+3; vol2-ch4 note 81; Lecky's French has older spelling and 'tous les religions'). `eymericus-directorium-inquisitorum.md` (BSB copy `10488917bsb`, Pegna commentary, catalogued 1607, image = page+35; p. 516 anecdote n551, p. 481 torture n516, sentence n555 ~p. 520; vol2-ch4 notes 40-42; Lecky's quotation of note 40 stops at 'nescio' and omits the 14-year sequel; the opening 'Si quaestionatus decenter noluerit...' of note 41 not found there). Remaining undone: Farinacius (43), Paramo, Beza/Castellio (68-70, 73), Jurieu (62-63), Bossuet Variations (75), Hobbes (V.118), Ventura, Sarpi, Bianchi French, ch. VI notes 27, 36, 49, 57.

- Also: `hobbes-leviathan-latin.md` (Molesworth Opera latina vol. III, `thomhobbesmalme07hobbgoog`, pp. 235-236 = n247-n248 = page+12; vol2-ch5 note 118; Lecky 'comparari' vs 'comparare') and `beza-de-haereticis.md` (1554 ed. `dehaereticisacivilimagistratu-beze-1554`, image = page+3; pp. 58, 65, 93; vol2-ch4 notes 68, 73; Lecky 'inferiorum' vs 'inferorum', 'defuisset' vs 'desiisset'). Beza's text has no djvu.xml pages in loc.py; use the `_djvu.xml` download directly. Castellio/Bellius passages (notes 69-70, Gluten 1610) not found in any scan. Still undone: Farinacius, Paramo, Jurieu, Bossuet Variations, Ventura, Sarpi, Bianchi French, ch. VI notes 27, 36, 49, 57.

- Also: `castellio-traite-des-heretiques.md` (Geneva 1913, `traitdeshr00castuoft`, p. 31 = n46 = page+15; French version of vol2-ch4 note 69; Latin original and note 70's epithets still NOT found; only French/modern editions online).

- Also: `paramo-de-origine-inquisitionis.md` (1598 ed. `bub_gb_mOToVY5wvVYC`, p. 588 = n706 = page+118; vol2-ch4 note 43; Lecky 'damnatur' vs 'damnetur'; Paramo's 'First Inquisitor'/Adam passages not found). Farinacius (note 43, 'De Delictis et Poenis p. 205, Venice 1619') NOT found: scans `bub_gb_PZLHDHkeQ3YC`, `bub_gb_381AS18arc8C`, `bub_gb_c2EXWUXSeU0C`, `bub_gb_b5ogYhxQQY0C` (Praxis et theoricae criminalis) have bad long-s OCR; searches for 'sordescere', 'solatium', 'uno nummo' failed. Note 85 is Neal's Puritans, not Paramo (user mix-up).

- Also (overnight-style run, 24 Oct): `desprez-de-boissy-lettres-sur-les-spectacles.md` (1777 vol. 1 `lettressurlesspe01desp`, p. 481 = n522 = page+41; ch. VI note 147; arret dated 22 April 1761 = Lecky's 1761, confirmed) and `buckle-history-of-civilization.md` (1857 vol. 1 `10278775bsb`, p. 344 = n371 = page+27; ch. VI notes 150, 167; p. 346 not read). Anderson Annals: Lecky's pagination does not match the 1764 folio (`historicalchrono01ande`, p. 190 = n249 has the St Thomas Becket merchants) nor 1787; skipped. Bedarride editions: `lesjuifsenfranc00beda` (1859), `lesjuifsenfrance00beda` (1864) not matched to Lecky's pages yet.

- Also (24 Oct run): `hallam-middle-ages.md` (1822 vol. 1 `stateofeuropedur01hall`, p. 221 = n244 = page+23; ch. VI note 19), `augustine-enarratio-psalm-36.md` (PL 36 `..._1845_36`, image n192; col. not read; ch. VI note 27), `turgot-memoire-sur-les-prets-dargent.md` (Schelle Oeuvres vol. 3 `turgot-oc-3`, p. 168 = n168; ch. VI note 30; § 29 not confirmed). Ch. VI notes done so far: 19, 27, 30, 147, 150, 167 + earlier 143.

- Also: `ventura-le-pouvoir-politique-chretien.md` (`lepouvoirpolitiq00vent`, p. 139 = n174 = page+35; ch. V note 28) and `llorente-histoire-de-linquisition.md` (French ed. 1817-18: tom. i `bub_gb_6rkHAAAAQAAJ`, pp. 273-275 = n330-n332; tom. iv `histoirecritiqu04llor`, p. 271 = n282 = page+11; vol2-ch4 note 37). Llorente: Lecky's totals match (31,912 burnt; 291,450 penanced); Lecky says Mariana's 2,000 burnt were in 'Andalusia', Llorente says Seville; the inscription's Latin has 'fere millia', Llorente's French 'plus de mille', Lecky 'nearly 1,000'. Tom. iv p. 272 and tom. i p. 272 not read.

- Also: `clementinae-ex-gravi.md` (Friedberg Corpus iuris canonici vol. 2, `BD1141952`, cols. 1183-1184 = n627; Clem. V.5 § 2; ch. VI note 46; Lecky 'istum' for 'illum'; title page not read). The Corpus of 1879 `bub_gb_sfwfAQAAMAAJ` is vol. 1 (Decretum). Lamet & Fromageau's French Dictionnaire (1733; ch. VI notes 28, 31, 139) and the Conférences sur l'usure NOT found online (archive search returns only Pontas).

- Also: `macpherson-annals-of-commerce.md` (1805 quarto; vol. i `annalsofcommerce01macp`, image = page+11: p. 536 = n547, p. 661 = n672; vol. ii `annalsofcommerce02macpuoft`, image = page+9: p. 638 = n647; ch. VI notes 94, 160, 162). Findings: p. 536's footnote is about a VENETIAN consul at Bruges in an English record, not an 'English consul' (note 94); p. 661 is headed A.D. 1443, Lecky says 1440 (note 160); p. 638 says 'about this time' under 1689. Unread: p. 715 mentions 'first consul for the English merchants at Pisa' under King Richard (OCR only).

- Also: `blanqui-histoire-de-leconomie-politique.md` (`histoiredelco01blan`, page foot '3e Edit. t. I.', image = page+31: pp. 225-226 = n256-n257, p. 250 = n281; ch. VI notes 83, 85, 164 (p. 277 = n308, Spain as author of mercantile system; Ustariz footnote)). Lecky's 1294 summary matches; the Florentine 'officer to repress the luxury of women' is in a 1336-38 budget table (Lecky: 'beginning of the fourteenth century'). Notes 96 (pp. 244-270), 159 (271-284), 164 (277), 169 not yet checked. Another copy: `histoiredelcon01blan` (1860 ed., different pagination).

- Also: `pecchio-storia-della-economia-pubblica.md` (`storiadellaecon01peccgoog`, image = page+9, p. 11 = n20; ch. VI note 90). Pecchio p. 11 has the Tavola Amalfitana and compass, NOT Lecky's 'manuscript of Roman laws found at Amalfi'. Not found online: Rios (only Spanish original `estudioshistoric00amad`, not the French ed. Lecky cites), Lamet & Fromageau. Eden's State of the Poor 1797 is online (`bim_eighteenth-century_the-state-of-the-poor-o_eden-frederick-morton-_1797_1`; Lecky's vol. i pp. 10, 50 for notes 11, 17 not yet checked; Champagny `lacharitechreti00chamgoog` notes 9, 15 not checked).

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
