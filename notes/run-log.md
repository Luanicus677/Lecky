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
