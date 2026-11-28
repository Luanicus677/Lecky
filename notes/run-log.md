# Run log

One dated entry per work session, newest LAST. Scheduled runs append here (see CLAUDE.md, 'Scheduled runs').
Each entry: what was done (source pages, notes linked, OCR fixes), findings worth the owner's attention,
dead ends, coverage after the run (`python3 tools/coverage.py`), and any 'Questions for the owner'.

## 2026-11-28 (interactive)
- Custom domain readlecky.com live (Porkbun DNS, GitHub Pages, HTTPS); sitemap.xml + robots.txt; Google Search Console
  (Domain property, TXT verification at Porkbun) and Bing (imported from Google).
- CLAUDE.md trimmed; old contents moved to notes/source-log.md. Helper tools added: tools/ia_page.sh, gbox.py,
  lecky_line.py, linkcheck.py, coverage.py.
- Coverage: 565/850 footnotes linked; about 76 notes cite nothing linkable.
- Scheduled task "Lecky footnote run" created: 02:43 and 14:43 Europe/Dublin, 45-minute runs in the worker session
  "Lecky scheduled worker". First run 28 Nov 14:43. Owner to check the weekly usage bar before/after the first runs.

## 2026-11-28 14:44–15:20 UTC (scheduled run)
Worked on vol. I ch. III (lowest linked share). Coverage there 85/184 → 101/184.
- New source pages (all read on page images, facsimile crops, translation drafts): augustine-de-genesi-contra-manichaeos (5 passages;
  notes 89, 90, 92, 104), seneca-epistle-31 (56), justin-martyr-first-apology (1), more-utopia (179), lessing-laokoon (55),
  plato-phaedo (163), heyne-opuscula-academica (61), denis-idees-morales (124, 141, 142).
- Extended: tertullian-de-anima ch. 9 (167), bacon-novum-organum aph. 79 (103), raoul-rochette-tableau-des-catacombes pp. 187,
  191–192 (6). 16 notes linked in all.
- Findings for the owner (added to lecky-and-his-sources / curiosities):
  - Seneca's "Deus nudus est", Lecky's only evidence that the gods were "emphatically said" to be naked, means God has no robe of
    office (*praetexta*); it is about rank, not bodies or art.
  - Heyne's p. 339 already cites and dismisses the Pausanias passage that Lecky raises against him.
  - More's "twenty on one gibbet" is a lawyer's boast in praise of English justice; More's Latin says "sometimes", Robinson's
    English "for the moste part".
  - Bacon gives theology as his *second* cause of the neglect of science; Lecky: "more than to any other single cause".
  - Augustine: Lecky's "Lib. v. cap. 25" is book I (the work has two books); note 89's "bone of his bone" gloss is from II.13 and
    concerns the soul, not Christ and the Church. Recorded on lecky-and-his-sources ("Wrong chapter"); NOT added to as-printed.md,
    since it may be Lecky's own slip rather than the printer's.
  - Curiosities added: the naked God (Seneca); a soul seen in ecstasy at Sunday service, just after Tertullian had preached on the soul.
- Not found (two quick searches only, not yet a dead end): Raoul-Rochette, *Discours sur les types de l'art chrétien* p. 71 (n19).
- Linkcheck: 0 broken links. Muse not used ($0).
- ALL: 581/850 linked; 193 unlinked notes cite a work.
- Questions for the owner: none.
