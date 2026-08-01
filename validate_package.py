#!/usr/bin/env python3
"""Validate mechanical Vanguard written-entry requirements before upload."""

from __future__ import annotations

import re
from pathlib import Path


def words(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z]+(?:[-’'][A-Za-z]+)*\b", text))


entry = Path("entry.md").read_text(encoding="utf-8")
main, rest = entry.split("## Required rationale", 1)
rationale, rest = rest.split("## AI use disclosure", 1)
disclosure, entrant = rest.split("## Entrant information", 1)

checks = {
    "main_words": words(main),
    "rationale_words": words(rationale),
    "has_ai_disclosure": bool(disclosure.strip()),
    "personal_fields_unfilled": "[participant must complete" in entrant,
    "pdf_exists": Path("the-classroom-with-no-attention-score.pdf").is_file(),
}

if checks["main_words"] > 2500:
    raise SystemExit(f"main entry exceeds 2,500 words: {checks['main_words']}")
if checks["rationale_words"] > 300:
    raise SystemExit(f"rationale exceeds 300 words: {checks['rationale_words']}")
if not checks["has_ai_disclosure"] or not checks["pdf_exists"]:
    raise SystemExit("AI disclosure or final PDF is missing")

print(checks)
if checks["personal_fields_unfilled"]:
    print("BOUNDARY: entrant identity fields and personal authorship review remain required")
