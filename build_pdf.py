#!/usr/bin/env python3
"""Build the final written Vanguard Open entry PDF from entry.md."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


SOURCE = Path("entry.md")
OUTPUT = Path("the-classroom-with-no-attention-score.pdf")


def inline_markup(text: str) -> str:
    """Convert the small inline Markdown subset used by the entry."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def build_story(markdown: str):
    """Turn the entry's headings, paragraphs, and lists into ReportLab flowables."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="EntryTitle", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle(name="EntrySubtitle", parent=styles["Heading2"], alignment=TA_CENTER, textColor="#4b3f72", spaceAfter=18))
    styles.add(ParagraphStyle(name="EntryHeading", parent=styles["Heading2"], spaceBefore=12, spaceAfter=7))
    styles.add(ParagraphStyle(name="EntryBody", parent=styles["BodyText"], leading=14, spaceAfter=8))

    story = []
    blocks = re.split(r"\n\s*\n", markdown.strip())
    for block in blocks:
        lines = block.splitlines()
        if block.startswith("# "):
            story.append(Paragraph(inline_markup(block[2:]), styles["EntryTitle"]))
        elif block.startswith("## "):
            title = block[3:]
            style = styles["EntrySubtitle"] if not story or len(story) == 1 else styles["EntryHeading"]
            story.append(Paragraph(inline_markup(title), style))
        elif all(re.match(r"^\d+\. ", line) for line in lines):
            items = [ListItem(Paragraph(inline_markup(re.sub(r"^\d+\. ", "", line)), styles["EntryBody"])) for line in lines]
            story.append(ListFlowable(items, bulletType="1", leftIndent=24))
            story.append(Spacer(1, 5))
        elif all(line.startswith("- ") for line in lines):
            items = [ListItem(Paragraph(inline_markup(line[2:]), styles["EntryBody"])) for line in lines]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=24))
            story.append(Spacer(1, 5))
        elif block == "---":
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph(inline_markup(" ".join(lines)), styles["EntryBody"]))
    return story


def main() -> None:
    """Render entry.md as the final PDF."""
    markdown = SOURCE.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="The Classroom with No Attention Score",
        author="Ren Yi",
    )
    doc.build(build_story(markdown))
    print(OUTPUT)


if __name__ == "__main__":
    main()
