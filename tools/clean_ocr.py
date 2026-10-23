#!/usr/bin/env python3
"""First-pass automated cleanup of Archive.org djvu.txt OCR for Lecky's
Rationalism in Europe. Produces a draft that still needs a human read-through
(this script does NOT claim perfect output) but removes the bulk of
mechanical scan noise: running page headers, hyphenated line-break splits,
stray OCR artefacts, and collapses physical-line breaks into paragraphs.
"""
import re
import sys

from spellchecker import SpellChecker

_SPELL = SpellChecker()


def rejoin_dropped_hyphens(text: str) -> str:
    """OCR sometimes loses the hyphen glyph at a mid-paragraph line break
    entirely, leaving e.g. "intel lectual" with nothing marking the break.
    Join two adjacent word-fragments when the combined form is a real
    dictionary word but at least one fragment alone is not -- this avoids
    false joins on genuine word pairs (where both halves are already real
    words, e.g. "a bout"), while catching lost-hyphen splits.
    """
    tokens = text.split(" ")
    out = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens):
            w1, w2 = tokens[i], tokens[i + 1]
            core1 = re.sub(r"[^A-Za-z]", "", w1).lower()
            core2 = re.sub(r"[^A-Za-z]", "", w2).lower()
            if core1 and core2 and w1.isalpha() and re.match(r"^[a-z]+\W*$", w2):
                combined = core1 + core2
                if (
                    combined in _SPELL
                    and (core1 not in _SPELL or core2 not in _SPELL)
                    and len(core1) >= 2 and len(core2) >= 2
                ):
                    out.append(w1 + w2)
                    i += 2
                    continue
        out.append(tokens[i])
        i += 1
    return " ".join(out)

# Known running-header fragments that appear as isolated short lines
# (verso/recto page headers), interspersed through the body text at
# page boundaries. Matched case-insensitively against a WHOLE stripped line.
HEADER_PATTERNS = [
    r"^\S{1,8}\s+introduction\.?$",         # garbled roman numeral + "INTRODUCTION."
    r"^introduction\.?\s+\S{1,8}$",
    r"rationalism\s+in\s+europe\.?\s*\S{0,8}$",
    r"^contents.*$",
    r"^the\s+first\s+volume\.?\s*\S{0,8}$",
    r"^[ivxlc]+\s*$",                      # a bare roman numeral (page no.)
    r"^\d{1,4}$",                           # a bare arabic page number
]
HEADER_RE = re.compile("|".join(f"(?:{p})" for p in HEADER_PATTERNS), re.I)


def is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) > 60:
        return False
    return bool(HEADER_RE.match(s))


def clean(raw: str) -> str:
    lines = raw.split("\n")
    # Drop isolated running-header / page-number lines.
    kept = [ln for ln in lines if not is_noise_line(ln)]

    # Regroup into paragraphs: blank line(s) separate paragraphs; within a
    # paragraph, physical OCR line breaks get rejoined. A trailing hyphen on
    # a line means the word continues on the next line with NO space; an
    # isolated leading "-" on a line (page-break artefact) is dropped.
    paragraphs = []
    current = []
    for ln in kept:
        if ln.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
            continue
        text = ln.strip()
        text = re.sub(r"^-\s*", "", text)  # stray leading dash artefact
        current.append(text)
    if current:
        paragraphs.append(current)

    out_paragraphs = []
    for para_lines in paragraphs:
        buf = ""
        for i, seg in enumerate(para_lines):
            if buf.endswith("-") and not buf.endswith("--"):
                # hyphenated word split across a line break: join directly
                buf = buf[:-1] + seg
            elif buf:
                buf += " " + seg
            else:
                buf = seg
        out_paragraphs.append(rejoin_dropped_hyphens(buf))

    text = "\n\n".join(out_paragraphs)

    # Common OCR substitution fixes for this scan (long-s / ligature misreads).
    # Conservative: only applied to whole-word matches of words we've
    # actually observed garbled in this source, not blind substitution.
    fixes = [
        (r"\bOP\b(?=\s+THE|\s+RATIONALISM)", "OF"),
        (r"\bnationalism\b", "Rationalism"),  # mid-sentence OCR drop of initial R/cap
    ]
    for pat, repl in fixes:
        text = re.sub(pat, repl, text)

    # Collapse runs of 2+ spaces (OCR kerning artefacts) to one.
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Normalise ' ;' ' :' etc spacing before punctuation left by OCR.
    text = re.sub(r"\s+([;:,.!?])", r"\1", text)

    return text.strip() + "\n"


if __name__ == "__main__":
    src = sys.argv[1]
    with open(src, encoding="utf-8") as f:
        raw = f.read()
    sys.stdout.write(clean(raw))
