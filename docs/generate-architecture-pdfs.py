from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
DOCS = [
    ("architecture-fonctionnelle.md", "architecture-fonctionnelle.pdf"),
    ("architecture-reseau.md", "architecture-reseau.pdf"),
    ("architecture-technique.md", "architecture-technique.pdf"),
]


def clean(text: str) -> str:
    replacements = {
        "->": "->",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "é": "e",
        "è": "e",
        "ê": "e",
        "à": "a",
        "ù": "u",
        "ç": "c",
        "É": "E",
        "À": "A",
        "Ç": "C",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def inline_md(text: str) -> str:
    text = clean(text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;font name='Courier'&gt;", "<font name='Courier'>")
    text = text.replace("&lt;/font&gt;", "</font>")
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=colors.HexColor("#082653"),
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0a3f86"),
            spaceBefore=9,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "h3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0a3f86"),
            spaceBefore=7,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=11.2,
            textColor=colors.HexColor("#102033"),
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["BodyText"],
            leftIndent=9,
            firstLineIndent=-6,
            fontSize=8.8,
            leading=11.2,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.6,
            leading=8,
            textColor=colors.HexColor("#0f172a"),
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["BodyText"],
            fontSize=6.8,
            leading=8.2,
            wordWrap="CJK",
        ),
        "head": ParagraphStyle(
            "head",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.2,
            textColor=colors.HexColor("#082653"),
            wordWrap="CJK",
        ),
    }


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(15 * mm, 9 * mm, "DECEPTR v1 MVP - Chambre des Representants du Maroc")
    canvas.drawRightString(195 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def parse_markdown(md: str, styles: dict) -> list:
    story = []
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(clean(lines[i]))
                i += 1
            i += 1
            title = "Diagramme Mermaid" if lang == "mermaid" else "Extrait technique"
            story.append(Paragraph(title, styles["h3"]))
            story.append(Preformatted("\n".join(code_lines), styles["code"]))
            story.append(Spacer(1, 5))
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = []
            for idx, raw in enumerate(table_lines):
                if idx == 1 and re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?", raw):
                    continue
                cells = [c.strip() for c in raw.strip("|").split("|")]
                style = styles["head"] if idx == 0 else styles["cell"]
                rows.append([Paragraph(inline_md(c), style) for c in cells])
            if rows:
                table = Table(rows, repeatRows=1, hAlign="LEFT")
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf2ff")),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b7c8de")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 6))
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            style = styles["h1"] if level == 1 else styles["h2"] if level == 2 else styles["h3"]
            story.append(KeepTogether([Paragraph(inline_md(heading.group(2)), style), Spacer(1, 2)]))
            i += 1
            continue

        bullet = re.match(r"^-\s+(.*)$", stripped)
        if bullet:
            story.append(Paragraph("- " + inline_md(bullet.group(1)), styles["bullet"]))
            i += 1
            continue

        paragraph = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|", "-", "```")):
            paragraph.append(lines[i].strip())
            i += 1
        story.append(Paragraph(inline_md(" ".join(paragraph)), styles["body"]))

    return story


def build_pdf(src: Path, dst: Path) -> None:
    styles = make_styles()
    doc = BaseDocTemplate(
        str(dst),
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=13 * mm,
        bottomMargin=14 * mm,
        title=src.stem,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    story = parse_markdown(src.read_text(encoding="utf-8"), styles)
    doc.build(story)


def main() -> None:
    generated = []
    for src_name, dst_name in DOCS:
        src = ROOT / src_name
        dst = ROOT / dst_name
        build_pdf(src, dst)
        generated.append(dst)

    writer = PdfWriter()
    for idx, pdf in enumerate(generated):
        if idx:
            # The individual PDFs already have their own page numbers; just append.
            pass
        writer.append(str(pdf))
    with (ROOT / "architectures-deceptr.pdf").open("wb") as fh:
        writer.write(fh)

    for pdf in [*generated, ROOT / "architectures-deceptr.pdf"]:
        print(f"{pdf.name}: {pdf.stat().st_size} bytes")


if __name__ == "__main__":
    main()
