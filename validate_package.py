#!/usr/bin/env python3
"""Validate mechanical Vanguard written-entry requirements before upload."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


ENTRY = Path("entry.md")
PDF = Path("the-classroom-with-no-attention-score.pdf")
EXPECTED_TITLE = "The Classroom with No Attention Score"


def words(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z]+(?:[-’'][A-Za-z]+)*\b", text))


def entrant_fields(section: str) -> dict[str, str]:
    fields = {}
    for line in section.splitlines():
        match = re.match(r"- ([^:]+):\s*(.*)", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def validate(entry_path: Path = ENTRY, pdf_path: Path = PDF) -> dict:
    entry = entry_path.read_text(encoding="utf-8")
    main, rest = entry.split("## Required rationale", 1)
    rationale, rest = rest.split("## AI use disclosure", 1)
    disclosure, entrant = rest.split("## Entrant information", 1)
    fields = entrant_fields(entrant)
    required_fields = {"Name", "Age category", "School or organization (if any)", "Contact email"}
    missing_fields = sorted(name for name in required_fields if not fields.get(name))
    placeholders = sorted(
        name for name, value in fields.items() if re.search(r"placeholder|participant must|todo|tbd", value, re.I)
    )
    if fields.get("Contact email") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", fields["Contact email"]):
        raise ValueError("entrant contact email is malformed")
    if missing_fields or placeholders:
        raise ValueError(f"incomplete entrant fields: missing={missing_fields}, placeholders={placeholders}")
    if words(main) > 2500:
        raise ValueError(f"main entry exceeds 2,500 words: {words(main)}")
    if words(rationale) > 300:
        raise ValueError(f"rationale exceeds 300 words: {words(rationale)}")
    if not disclosure.strip():
        raise ValueError("AI disclosure is missing")
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise ValueError("final PDF is missing or empty")

    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    metadata = reader.metadata or {}
    if not reader.pages:
        raise ValueError("final PDF has no pages")
    if EXPECTED_TITLE not in text or "AI use disclosure" not in text or "Entrant information" not in text:
        raise ValueError("final PDF is stale or missing required sections")
    if metadata.get("/Title") != EXPECTED_TITLE or metadata.get("/Author") != fields["Name"]:
        raise ValueError("PDF title/author metadata does not match the entry")

    return {
        "main_words": words(main),
        "rationale_words": words(rationale),
        "ai_disclosure_present": True,
        "entrant_fields_complete": True,
        "pdf_pages": len(reader.pages),
        "pdf_title": metadata.get("/Title"),
        "pdf_author": metadata.get("/Author"),
        "pdf_required_sections_present": True,
    }


def main() -> None:
    print(json.dumps(validate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
