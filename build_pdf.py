#!/usr/bin/env python3
"""Build the final written Vanguard Open entry PDF from entry.md."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


SOURCE = Path("entry.md")
OUTPUT = Path("the-classroom-with-no-attention-score.pdf")


def inline_markup(text: str) -> str:
    """Convert the small inline Markdown subset used by the entry."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def classroom_map() -> Drawing:
    """Render the entry's three spaces and shared refusal as a compact vector map."""
    drawing = Drawing(500, 158)
    box_width = 150
    box_height = 82
    gap = 25
    box_y = 60
    palette = [HexColor("#e9f4ff"), HexColor("#f0ecff"), HexColor("#eef8ee")]
    headings = ["EPHEMERAL WORKBENCH", "EVIDENCE TABLE", "UNSCORED COMMONS"]
    detail_lines = [
        ("Student-invoked AI", "Temporary by default"),
        ("Selected artifacts", "Claims + provenance"),
        ("No AI or grading", "Curiosity without telemetry"),
    ]

    for index, (heading, details) in enumerate(zip(headings, detail_lines)):
        x = index * (box_width + gap)
        drawing.add(Rect(x, box_y, box_width, box_height, rx=8, ry=8, fillColor=palette[index], strokeColor=HexColor("#61548f"), strokeWidth=1.2))
        drawing.add(String(x + box_width / 2, box_y + 59, heading, textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.2, fillColor=HexColor("#372f57")))
        drawing.add(String(x + box_width / 2, box_y + 37, details[0], textAnchor="middle", fontName="Helvetica", fontSize=8.8, fillColor=HexColor("#292638")))
        drawing.add(String(x + box_width / 2, box_y + 21, details[1], textAnchor="middle", fontName="Helvetica", fontSize=8.8, fillColor=HexColor("#292638")))

        if index < 2:
            start_x = x + box_width + 4
            end_x = x + box_width + gap - 5
            arrow_y = box_y + box_height / 2
            drawing.add(Line(start_x, arrow_y, end_x, arrow_y, strokeColor=HexColor("#8b82a8"), strokeWidth=1))
            drawing.add(Polygon([end_x, arrow_y, end_x - 5, arrow_y + 3, end_x - 5, arrow_y - 3], fillColor=HexColor("#8b82a8"), strokeColor=None))

    drawing.add(Rect(0, 8, 500, 34, rx=7, ry=7, fillColor=HexColor("#fff0ee"), strokeColor=HexColor("#a54b42"), strokeWidth=1.2))
    drawing.add(String(250, 27, "THE SHARED REFUSAL", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.5, fillColor=HexColor("#7c302b")))
    drawing.add(String(250, 14, "No automated inference about attention, effort, emotion, honesty, motivation, or character", textAnchor="middle", fontName="Helvetica", fontSize=8.2, fillColor=HexColor("#4b2926")))
    return drawing


def build_story(markdown: str):
    """Turn the entry's headings, paragraphs, and lists into ReportLab flowables."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="EntryTitle", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle(name="EntrySubtitle", parent=styles["Heading2"], alignment=TA_CENTER, textColor="#4b3f72", spaceAfter=18))
    styles.add(ParagraphStyle(name="EntryHeading", parent=styles["Heading2"], spaceBefore=12, spaceAfter=7))
    styles.add(ParagraphStyle(name="EntryBody", parent=styles["BodyText"], leading=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="DiagramCaption", parent=styles["BodyText"], alignment=TA_CENTER, fontSize=8, textColor="#5c5866", spaceAfter=10))

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
            if style is styles["EntrySubtitle"]:
                story.append(classroom_map())
                story.append(Paragraph("Three spaces, three data boundaries, one refusal that keeps agency with the learner.", styles["DiagramCaption"]))
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
