#!/usr/bin/env python3
"""Generate a schematic construction/engineering basis set for Option F.

This is intentionally not a sealed or permit-ready construction document. It
consolidates known project geometry, current Richmond design criteria, and a
coordinated preliminary structural/MEP basis so an architect and engineer can
finish the permit set without restarting the design.
"""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, black, white
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "adu-option-f-construction-engineering-basis.pdf"
PAGE_W, PAGE_H = 17 * inch, 11 * inch
ISSUE_DATE = date(2026, 8, 3).isoformat()

INK = black
GRAY_1 = Color(0.18, 0.18, 0.18)
GRAY_2 = Color(0.35, 0.35, 0.35)
GRAY_3 = Color(0.58, 0.58, 0.58)
GRAY_4 = Color(0.82, 0.82, 0.82)
GRAY_5 = Color(0.94, 0.94, 0.94)

SHEET_TITLES = [
    ("G001", "COVER / PROJECT BASIS"),
    ("G002", "CODE, ZONING, AND PERMIT MATRIX"),
    ("C101", "SITE / ACCESS / UTILITY CONCEPT"),
    ("A101", "LEVEL 1 DIMENSIONED PLAN"),
    ("A102", "LEVEL 2 DIMENSIONED PLAN"),
    ("A201", "ROOF PLAN / OPENING SCHEDULES"),
    ("A301", "EXTERIOR ELEVATIONS"),
    ("A401", "BUILDING SECTIONS / ENVELOPE"),
    ("S101", "FOUNDATION / FRAMING BASIS"),
    ("M101", "MEP / ELECTRICAL / LIFE SAFETY BASIS"),
    ("G003", "SPECIFICATIONS / CLOSEOUT CHECKLIST"),
]


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        if stringWidth(test, font, size) <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font: str = "Helvetica",
    size: float = 7.5,
    leading: float | None = None,
    color=INK,
    bullet: str | None = None,
) -> float:
    leading = leading or size * 1.28
    prefix = f"{bullet} " if bullet else ""
    lines = wrap(prefix + text, font, size, width)
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def box_title(c: canvas.Canvas, x: float, y: float, w: float, title: str) -> None:
    c.setFillColor(GRAY_1)
    c.rect(x, y - 16, w, 16, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 6, y - 11, title.upper())


def note_box(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    w: float,
    h: float,
    title: str,
    notes: list[str],
    *,
    size: float = 7.2,
) -> None:
    c.setStrokeColor(GRAY_3)
    c.setLineWidth(0.6)
    c.rect(x, y_top - h, w, h, fill=0, stroke=1)
    box_title(c, x, y_top, w, title)
    y = y_top - 28
    for i, note in enumerate(notes, 1):
        y = text_block(c, note, x + 8, y, w - 16, size=size, bullet=f"{i}.") - 4


def draw_title_block(c: canvas.Canvas, sheet: str, title: str) -> None:
    y = 16
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(24, y, PAGE_W - 48, 38, fill=0, stroke=1)
    c.line(PAGE_W - 330, y, PAGE_W - 330, y + 38)
    c.line(PAGE_W - 104, y, PAGE_W - 104, y + 38)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(31, y + 24, "OPTION F DETACHED ADU - 112 W 29TH ST, RICHMOND, VA 23225")
    c.setFont("Helvetica", 6.5)
    c.drawString(
        31,
        y + 10,
        "SCHEMATIC CONSTRUCTION / ENGINEERING BASIS - NOT FOR CONSTRUCTION - FIELD VERIFY",
    )
    c.setFont("Helvetica-Bold", 8)
    c.drawString(PAGE_W - 320, y + 24, title)
    c.setFont("Helvetica", 6.5)
    c.drawString(PAGE_W - 320, y + 10, f"ISSUE {ISSUE_DATE}  |  DRAWN FOR OWNER COORDINATION")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W - 76, y + 13, sheet)


def sheet(c: canvas.Canvas, index: int) -> tuple[str, str]:
    if index:
        c.showPage()
    number, title = SHEET_TITLES[index]
    draw_title_block(c, number, title)
    c.setFillColor(GRAY_1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(28, PAGE_H - 25, f"{number}  {title}")
    c.setFont("Helvetica", 6.5)
    c.drawRightString(PAGE_W - 28, PAGE_H - 25, "OPTION F / 20 FT x 24 FT / 480 SF UPPER ADU")
    c.setStrokeColor(GRAY_3)
    c.line(28, PAGE_H - 31, PAGE_W - 28, PAGE_H - 31)
    return number, title


def dim_line(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, label: str) -> None:
    c.setStrokeColor(GRAY_2)
    c.setFillColor(GRAY_2)
    c.setLineWidth(0.45)
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    for x, y, a in ((x1, y1, ang), (x2, y2, ang + math.pi)):
        c.line(x, y, x + 5 * math.cos(a + 0.45), y + 5 * math.sin(a + 0.45))
        c.line(x, y, x + 5 * math.cos(a - 0.45), y + 5 * math.sin(a - 0.45))
    c.setFont("Helvetica", 6.5)
    if abs(y2 - y1) < abs(x2 - x1):
        c.drawCentredString((x1 + x2) / 2, y1 + 3, label)
    else:
        c.saveState()
        c.translate(x1 + 3, (y1 + y2) / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, label)
        c.restoreState()


def plan_xy(origin: tuple[float, float], scale: float, x: float, y: float) -> tuple[float, float]:
    return origin[0] + x * scale, origin[1] + y * scale


def wall_rect(c: canvas.Canvas, origin, scale, x, y, w, h, fill=GRAY_1) -> None:
    px, py = plan_xy(origin, scale, x, y)
    c.setFillColor(fill)
    c.rect(px, py, w * scale, h * scale, fill=1, stroke=0)


def room_label(c: canvas.Canvas, origin, scale, x, y, title, sub="") -> None:
    px, py = plan_xy(origin, scale, x, y)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(px, py, title)
    if sub:
        c.setFillColor(GRAY_2)
        c.setFont("Helvetica", 5.8)
        c.drawCentredString(px, py - 8, sub)


def opening(c: canvas.Canvas, origin, scale, x, y, length, *, vertical=False, label="") -> None:
    px, py = plan_xy(origin, scale, x, y)
    c.setStrokeColor(white)
    c.setLineWidth(7)
    if vertical:
        c.line(px, py, px, py + length * scale)
    else:
        c.line(px, py, px + length * scale, py)
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    offset = 2
    if vertical:
        c.line(px - offset, py, px - offset, py + length * scale)
        c.line(px + offset, py, px + offset, py + length * scale)
    else:
        c.line(px, py - offset, px + length * scale, py - offset)
        c.line(px, py + offset, px + length * scale, py + offset)
    if label:
        c.setFillColor(GRAY_2)
        c.setFont("Helvetica", 5)
        c.drawString(px + 3, py + 4, label)


def plan_shell(c: canvas.Canvas, origin, scale) -> None:
    wall_rect(c, origin, scale, 0, 0, 24, 20)
    wall_rect(c, origin, scale, 0.5, 0.5, 23, 19, white)


def draw_stair_and_patio(c: canvas.Canvas, origin, scale) -> None:
    x0, y0 = plan_xy(origin, scale, 0.5, -4)
    c.setStrokeColor(GRAY_2)
    c.setLineWidth(0.6)
    c.rect(x0, y0, 27.5 * scale, 4 * scale, fill=0, stroke=1)
    for i in range(14):
        x = x0 + i * (11 / 13) * scale
        c.line(x, y0, x, y0 + 4 * scale)
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(INK)
    c.drawCentredString(x0 + 5.5 * scale, y0 + 2 * scale, "UP / DN - 14 RISERS / 13 TREADS")
    px, py = plan_xy(origin, scale, 24, 0)
    c.setDash(4, 3)
    c.rect(px, py, 4 * scale, 19.5 * scale, fill=0, stroke=1)
    c.setDash()


def draw_level_plan(
    c: canvas.Canvas, level: int, origin: tuple[float, float], scale: float
) -> None:
    plan_shell(c, origin, scale)
    draw_stair_and_patio(c, origin, scale)
    if level == 1:
        wall_rect(c, origin, scale, 0.5, 11.5, 23, 0.33)
        wall_rect(c, origin, scale, 7.5, 11.5, 0.33, 8)
        wall_rect(c, origin, scale, 14, 11.5, 0.33, 8)
        wall_rect(c, origin, scale, 7.5, 13.5, 6.83, 0.33)
        opening(c, origin, scale, 0, 1.3, 9.7, vertical=True, label="D01 9'-8\" OH")
        opening(c, origin, scale, 23.5, 12.3, 6, vertical=True, label="D03")
        opening(c, origin, scale, 23.5, 4, 3, vertical=True, label="W01")
        room_label(c, origin, scale, 12, 7.5, "GARAGE / SHOP", "approx. 23 ft clear depth")
        room_label(c, origin, scale, 4, 16, "MECH / STORAGE", "panel + HPWH")
        room_label(c, origin, scale, 10.8, 17.2, "POWDER", "stacked wet core")
        room_label(c, origin, scale, 10.8, 12.4, "PROTECTED HALL", "20-min door to garage")
        room_label(c, origin, scale, 19, 16, "OWNER FLEX ROOM", "classification by Zoning")
        # plumbing fixtures
        c.setStrokeColor(INK)
        c.circle(*plan_xy(origin, scale, 11.8, 16.1), 0.55 * scale, fill=0, stroke=1)
        wall_rect(c, origin, scale, 8, 14, 2.5, 1.2, GRAY_5)
    else:
        wall_rect(c, origin, scale, 10.2, 0.5, 0.33, 9.5)
        wall_rect(c, origin, scale, 0.5, 10, 10.03, 0.33)
        wall_rect(c, origin, scale, 0.5, 13.5, 13.83, 0.33)
        wall_rect(c, origin, scale, 7.5, 13.5, 0.33, 6)
        wall_rect(c, origin, scale, 14, 13.5, 0.33, 6)
        opening(c, origin, scale, 0, 3, 3.5, vertical=True, label="W02 EERO")
        opening(c, origin, scale, 16, 0, 5, label="W03")
        opening(c, origin, scale, 23.5, 1.5, 6, vertical=True, label="D04")
        opening(c, origin, scale, 23.5, 15, 3.5, vertical=True, label="W04")
        room_label(c, origin, scale, 5.2, 5.2, "BEDROOM", "9'-8\" x 9'-6\" / 92 sf")
        room_label(c, origin, scale, 3.8, 11.8, "CLOSET", "7'-0\" x 3'-2\"")
        room_label(c, origin, scale, 3.8, 16.5, "LAUNDRY / STORAGE", "low-eave zone")
        room_label(c, origin, scale, 10.8, 17.2, "BATH", "stacked over powder")
        room_label(c, origin, scale, 17, 10.8, "KITCHEN", "6'-10\" island")
        room_label(c, origin, scale, 18, 5.0, "LIVING", "entry from south landing")
        room_label(c, origin, scale, 18.8, 16.3, "DINING", "seated low-eave zone")
        # island and east tall cabinet run
        wall_rect(c, origin, scale, 11.6, 9.1, 6.8, 3, GRAY_5)
        wall_rect(c, origin, scale, 21, 8.4, 2.5, 7, GRAY_5)
        wall_rect(c, origin, scale, 7.9, 13.9, 3, 3, GRAY_5)
        c.circle(*plan_xy(origin, scale, 11.8, 15.0), 0.55 * scale, fill=0, stroke=1)

    # primary dimensions
    x1, y1 = plan_xy(origin, scale, 0, -5.2)
    x2, _ = plan_xy(origin, scale, 24, -5.2)
    dim_line(c, x1, y1, x2, y1, "24'-0\"")
    x1, y1 = plan_xy(origin, scale, -1.2, 0)
    _, y2 = plan_xy(origin, scale, -1.2, 20)
    dim_line(c, x1, y1, x1, y2, "20'-0\"")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(INK)
    c.drawString(origin[0], origin[1] + 20 * scale + 12, "NORTH / PROPERTY LINE 5 FT BEYOND WALL")


def draw_north_arrow(c: canvas.Canvas, x: float, y: float) -> None:
    c.setStrokeColor(INK)
    c.setFillColor(INK)
    c.setLineWidth(1)
    c.line(x, y, x, y + 36)
    c.line(x, y + 36, x - 5, y + 25)
    c.line(x, y + 36, x + 5, y + 25)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x, y + 42, "N")


def draw_site(c: canvas.Canvas, x: float, y: float, scale: float) -> None:
    # Coordinates use the repo site convention: x east from alley, y north.
    lot_w, lot_h = 148, 45
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.rect(x, y, lot_w * scale, lot_h * scale, fill=0, stroke=1)
    # setbacks
    c.setDash(4, 3)
    c.setStrokeColor(GRAY_3)
    c.line(x + 5 * scale, y, x + 5 * scale, y + lot_h * scale)
    c.line(x + 123 * scale, y, x + 123 * scale, y + lot_h * scale)
    c.line(x, y + 5 * scale, x + lot_w * scale, y + 5 * scale)
    c.line(x, y + 40 * scale, x + lot_w * scale, y + 40 * scale)
    c.setDash()
    # existing house simplified
    c.setFillColor(GRAY_5)
    c.setStrokeColor(GRAY_2)
    c.rect(x + 84 * scale, y + 9 * scale, 39 * scale, 27 * scale, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(INK)
    c.drawCentredString(x + 103.5 * scale, y + 23 * scale, "EXISTING HOUSE")
    # ADU and access
    c.setFillColor(white)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.rect(x + 5 * scale, y + 20 * scale, 24 * scale, 20 * scale, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x + 17 * scale, y + 31 * scale, "OPTION F ADU")
    c.setFont("Helvetica", 6)
    c.drawCentredString(x + 17 * scale, y + 28.5 * scale, "20 x 24 / 2 STORY")
    c.setDash(3, 2)
    c.rect(x + 5.5 * scale, y + 16 * scale, 27 * scale, 4 * scale, fill=0, stroke=1)
    c.rect(x + 29 * scale, y + 20 * scale, 4 * scale, 19.5 * scale, fill=0, stroke=1)
    c.setDash()
    # replacement shed
    c.setFillColor(GRAY_4)
    c.rect(x + 8 * scale, y + 5 * scale, 18 * scale, 6 * scale, fill=1, stroke=1)
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(x + 17 * scale, y + 7.5 * scale, "18 x 6 SHED")
    # utility concept lines
    c.setStrokeColor(GRAY_2)
    c.setDash(7, 3)
    c.line(x + 29 * scale, y + 30 * scale, x + 84 * scale, y + 30 * scale)
    c.setDash(2, 2)
    c.line(x + 29 * scale, y + 27.5 * scale, x + 84 * scale, y + 20 * scale)
    c.setDash()
    c.setFont("Helvetica", 5.5)
    c.drawString(x + 42 * scale, y + 30.5 * scale, "ELEC / WATER - ROUTE TBD")
    c.drawString(x + 43 * scale, y + 24.5 * scale, "SANITARY - VERIFY INVERT / FALL")
    # labels
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x - 40, y + 22 * scale, "ALLEY")
    c.drawString(x + lot_w * scale + 8, y + 22 * scale, "W 29TH ST")
    draw_north_arrow(c, x + 10, y + lot_h * scale + 18)
    dim_line(c, x, y - 12, x + lot_w * scale, y - 12, "148'-0\"")
    dim_line(c, x - 12, y, x - 12, y + lot_h * scale, "45'-0\"")


def draw_elevation(
    c: canvas.Canvas, x: float, y: float, width_ft: float, name: str, gable: bool, features: str
) -> None:
    s = 10.2
    w = width_ft * s
    c.setStrokeColor(INK)
    c.setFillColor(white)
    c.setLineWidth(0.8)
    c.line(x - 15, y, x + w + 15, y)
    c.rect(x, y, w, 16 * s, fill=0, stroke=1)
    c.line(x, y + 9.25 * s, x + w, y + 9.25 * s)
    if gable:
        c.line(x, y + 16 * s, x + w / 2, y + 20 * s)
        c.line(x + w / 2, y + 20 * s, x + w, y + 16 * s)
    else:
        c.line(x, y + 16 * s, x + w, y + 16 * s)
    # schematic openings
    if "garage" in features:
        c.rect(x + 2 * s, y, 9.67 * s, 7 * s, fill=0, stroke=1)
        c.rect(x + 4 * s, y + 11 * s, 4 * s, 3.5 * s, fill=0, stroke=1)
    if "sliders" in features:
        c.rect(x + 3 * s, y, 6 * s, 7 * s, fill=0, stroke=1)
        c.rect(x + 3 * s, y + 9.25 * s, 6 * s, 6.5 * s, fill=0, stroke=1)
    if "stair" in features:
        c.line(x + 1 * s, y, x + 12 * s, y + 9.25 * s)
        for i in range(8):
            xx = x + (1 + i * 1.35) * s
            yy = y + i * 1.15 * s
            c.line(xx, yy, xx + 2.5 * s, yy)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x, y - 13, name)
    c.setFont("Helvetica", 5.8)
    c.drawRightString(x + w, y - 13, 'SCHEMATIC 1/8" = 1\'-0"')


def draw_section(c: canvas.Canvas, x: float, y: float, longitudinal=False) -> None:
    s = 15
    span = 24 if longitudinal else 20
    w = span * s
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(x - 10, y, x + w + 10, y)
    # footing/stem/slab
    c.rect(x, y - 10, w, 10, fill=0, stroke=1)
    c.line(x, y + 9.25 * s, x + w, y + 9.25 * s)
    c.line(x, y + 16 * s, x + w, y + 16 * s)
    if longitudinal:
        c.line(x, y + 20 * s, x + w, y + 20 * s)
    else:
        c.line(x, y + 16 * s, x + w / 2, y + 20 * s)
        c.line(x + w / 2, y + 20 * s, x + w, y + 16 * s)
        # sloped ceiling min-height bands
        c.setDash(3, 2)
        c.line(x + 1.4 * s, y + 16.6 * s, x + 18.6 * s, y + 16.6 * s)
        c.setDash()
    c.setFont("Helvetica", 6)
    c.drawString(x + 4, y + 4.5 * s, "UNCONDITIONED GARAGE / FLEX")
    c.drawString(x + 4, y + 12.5 * s, "CONDITIONED ADU - SLOPED CEILING")
    dim_line(c, x + w + 15, y, x + w + 15, y + 9.25 * s, "+9'-3\" T.O. SUBFLOOR")
    dim_line(c, x + w + 30, y, x + w + 30, y + 20 * s, "19'-10\" MAX BASIS")


def table(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    widths: list[float],
    rows: list[list[str]],
    *,
    row_h=20,
    header=True,
    size=6.4,
) -> None:
    total = sum(widths)
    y = y_top
    for r, row in enumerate(rows):
        c.setFillColor(GRAY_1 if header and r == 0 else (GRAY_5 if r % 2 else white))
        c.setStrokeColor(GRAY_3)
        c.rect(x, y - row_h, total, row_h, fill=1, stroke=1)
        xx = x
        for i, cell in enumerate(row):
            if i:
                c.line(xx, y, xx, y - row_h)
            c.setFillColor(white if header and r == 0 else INK)
            c.setFont("Helvetica-Bold" if header and r == 0 else "Helvetica", size)
            lines = wrap(cell, "Helvetica", size, widths[i] - 8)[:2]
            for j, line in enumerate(lines):
                c.drawString(xx + 4, y - 8 - j * (size + 1), line)
            xx += widths[i]
        y -= row_h


def cover(c: canvas.Canvas) -> None:
    sheet(c, 0)
    c.setFillColor(GRAY_1)
    c.rect(28, 500, 420, 220, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 27)
    c.drawString(52, 665, "OPTION F DETACHED ADU")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(52, 635, "CONSTRUCTION / ENGINEERING BASIS SET")
    c.setFont("Helvetica", 10)
    c.drawString(52, 604, "112 W 29TH ST, RICHMOND, VA 23225")
    c.drawString(52, 586, "PIN S0001130005  |  ZONE R-5  |  20 FT x 24 FT")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(52, 540, "SCHEMATIC - NOT FOR CONSTRUCTION")
    c.setFont("Helvetica", 7.5)
    for i, line in enumerate(
        wrap(
            "Prepared from owner sketches, field measurements, assessor documents, repo CAD/model geometry, and Option F coordination. Licensed architect/engineer must verify and complete before permit or construction.",
            "Helvetica",
            7.5,
            360,
        )
    ):
        c.drawString(52, 520 - i * 10, line)

    image_path = ROOT / "renderings" / "option-f-yard-photoreal.png"
    if image_path.exists():
        with Image.open(image_path) as img:
            gray = img.convert("L")
            c.drawImage(
                ImageReader(gray),
                470,
                410,
                width=720,
                height=320,
                preserveAspectRatio=True,
                anchor="c",
            )
    c.setFillColor(GRAY_2)
    c.setFont("Helvetica-Oblique", 6.5)
    c.drawString(470, 400, "DESIGN INTENT RENDERING - DOES NOT CONTROL CONSTRUCTION")

    note_box(
        c,
        28,
        380,
        420,
        286,
        "BASIS AND LIMITS",
        [
            "Enclosed building: 24 ft east-west x 20 ft north-south; two stories; 480 sf gross upper ADU. Exterior stair and east patios remain unenclosed.",
            "Selected Option F: full-depth south garage, stacked north-center wet core, northeast owner flex room, west bedroom, east living/kitchen, south stair, and east patios.",
            "No survey, utility locate, geotechnical report, drainage design, truss package, engineered lumber calculations, REScheck, HVAC Manual J/S/D, electrical load calculation, or sealed structural design was available.",
            "Do not scale drawings. Dimensions are design-basis values. Field verify property lines, grades, utilities, existing house geometry, and all product rough openings.",
            "North and west roof edges are flush at setback walls in this basis. Any eave/rake projection requires Zoning confirmation or inward relocation of building.",
            "This set coordinates decisions and exposes missing work. It is not permission to build and carries no professional seal.",
        ],
    )
    table(
        c,
        470,
        380,
        [70, 285, 105, 205],
        [
            ["SHEET", "TITLE", "STATUS", "PRIMARY COMPLETION NEED"],
        ]
        + [[n, t, "BASIS", "Architect/engineer verification"] for n, t in SHEET_TITLES],
        row_h=23,
        size=6.2,
    )


def code_sheet(c: canvas.Canvas) -> None:
    sheet(c, 1)
    code_rows = [
        ["ITEM", "DESIGN BASIS", "SOURCE / ACTION"],
        [
            "Governing residential code",
            "2021 Virginia Residential Code; effective Jan. 18, 2024",
            "Confirm with Richmond at permit intake",
        ],
        [
            "Risk / use",
            "Detached accessory dwelling over private garage; Risk Category II",
            "Final classification by code official",
        ],
        [
            "Wind",
            "115 mph basic design wind speed, Risk Category II",
            "Richmond structural criteria",
        ],
        ["Ground snow", "20 psf", "Richmond structural criteria"],
        ["Seismic", "Design Category B", "Richmond structural criteria"],
        ["Frost", "18 in minimum", "Bottom of exterior footing below frost depth"],
        [
            "Soil",
            "1,500 psf assumed only for preliminary sizing",
            "Geotechnical/soil report and field verification required",
        ],
        [
            "Energy",
            "Climate Zone 4A working basis; prescriptive path or REScheck",
            "Confirm jurisdictional climate data and final assemblies",
        ],
        [
            "Garage separation",
            "5/8 in Type X at garage ceiling below habitable rooms; protected supports",
            "VRC R302.6; final listed assembly",
        ],
        [
            "Bedroom EERO",
            "5.7 sf net clear; min 20 in width, 24 in height; sill max 44 in",
            "VRC R310; verify selected product",
        ],
        [
            "Stair",
            "36 in clear; 14 risers at approx. 7-15/16 in; 13 treads at 10 in basis",
            "Field-set from final floor elevation; VRC R311",
        ],
        [
            "Guards",
            "36 in landings; 34-38 in stair handrail; openings under 4 in",
            "VRC R312; verify graspability/load design",
        ],
    ]
    table(c, 28, 735, [145, 370, 255], code_rows, row_h=31, size=6.6)
    note_box(
        c,
        820,
        735,
        370,
        302,
        "ZONING BASIS - WRITTEN CONFIRMATION NEEDED",
        [
            "R-5 lot recorded as 45 ft x 148 ft. Working yards: 5 ft side, 5 ft rear, 25 ft front. Current site drawing places ADU walls at north and alley-side minimums.",
            "Detached ADU floor area cannot exceed greater of one-third main dwelling or 500 sf. Upper floor is 480 sf gross. Obtain written ruling for lower owner flex room and powder room exclusions.",
            "Accessory building height basis is 20 ft maximum. Proposed ridge is 19 ft 10 in from average adjacent grade; survey final grade and roof finish before approval.",
            "ADU access must satisfy Public Works and Fire. Confirm hydrant within 250 ft, alley access, address visibility, and any WISP needs.",
            "Verify lot coverage, easements, historic-district status, tree impacts, and whether replacement shed is reviewed in same zoning application.",
        ],
    )
    note_box(
        c,
        820,
        412,
        370,
        317,
        "PERMIT / DEFERRED SUBMITTAL MATRIX",
        [
            "Black-and-white PDF; architectural plans at minimum 1/8 in = 1 ft. Submit site, foundation, framing, floor plans, elevations, sections, insulation, and rated assemblies.",
            "Separate trade permits: electrical, plumbing, mechanical, and gas if used. This sheet coordinates scope but is not a trade permit application.",
            "Deferred engineered items: roof trusses/rafters, floor trusses or I-joists, LVL/PSL headers, portal frame/hold-downs, exterior stair/deck framing, and any unusual foundation condition.",
            "New-home checklist calls for soil report, braced-wall information, truss package, structural reports as applicable, and REScheck or equivalent envelope data.",
            "Before excavation: boundary/topographic survey, utility locate (Virginia 811), sanitary invert, water capacity/meter decision, electrical service/load study, drainage path, and erosion/stormwater screening.",
        ],
    )
    c.setFont("Helvetica", 6.2)
    c.setFillColor(GRAY_2)
    sources = [
        "Sources checked 2026-08-03: rva.gov/planning-development-review/permits-and-inspections",
        "rva.gov/planning-development-review/accessory-dwelling-units",
        "rva.gov/sites/default/files/2025-02/Building Plan Requirements Residential 2021 VRC Updated.pdf",
        "codes.iccsafe.org/content/VARC2021P1/",
    ]
    y = 85
    for source in sources:
        c.drawString(28, y, source)
        y -= 9


def site_sheet(c: canvas.Canvas) -> None:
    sheet(c, 2)
    draw_site(c, 95, 390, 6.5)
    note_box(
        c,
        28,
        350,
        370,
        260,
        "SITE / GRADING NOTES",
        [
            "Survey controls. Do not establish building from fences, aerials, or this diagram. Licensed surveyor to stake walls and verify setbacks before footing excavation.",
            "Maintain positive drainage away from new foundation. Working target: 6 in fall within first 10 ft where feasible; civil designer to adapt to lot and prevent discharge onto neighbors or alley.",
            "Roof drainage: gutters both eaves, sealed downspouts to approved splash blocks or infiltration system. No discharge across stair, alley, or neighboring property.",
            "Limit disturbed area; install stabilized construction entrance, inlet protection if applicable, and perimeter controls required by Water Resources.",
            "Protect trees and existing house foundation. Arborist to review roots within excavation zone before final siting.",
        ],
    )
    note_box(
        c,
        420,
        350,
        370,
        260,
        "UTILITY BASIS",
        [
            "Water: new 1 in service from approved connection basis; size by developed length and fixture units. Confirm meter/backflow policy with DPU.",
            "Sanitary: 4 in building sewer at code slope where gravity route is feasible. Camera/locate existing line and verify invert before foundation design.",
            "Electrical: feeder from existing service to detached-building panel; electrician to perform dwelling/service load calculation and grounding design.",
            "Communications: separate conduit with pull string. Maintain separation from power and other utilities.",
            "No gas planned. All-electric basis uses heat pump HVAC, heat-pump water heater, induction range, and electric dryer.",
        ],
    )
    note_box(
        c,
        812,
        350,
        378,
        260,
        "SITE DIMENSIONS TO VERIFY",
        [
            "Lot: 45 ft x 148 ft; main house east wall approx. 25 ft from front line; field/survey confirmation governs.",
            "ADU enclosed walls: west x=5 ft; east x=29 ft; south y=20 ft; north y=40 ft in repo coordinates.",
            "Replacement shed: 18 ft x 6 ft maximum outside envelope, 8 ft from alley and 5 ft side setback. Keep roof, gutters, and foundation within envelope.",
            "Stair/access band: approximately x=5.5 to 32.5 ft and y=16 to 20 ft; 5 ft clear to replacement shed basis.",
            "Existing shed removal must be reconciled with assessor's historical detached-garage record before demolition permit scope is finalized.",
        ],
    )


def floor_sheet(c: canvas.Canvas, index: int, level: int) -> None:
    sheet(c, index)
    origin = (95, 245)
    draw_level_plan(c, level, origin, 20)
    if level == 1:
        notes = [
            "Garage floor: 4 in concrete slab over compacted granular base and 10 mil vapor retarder; slope only where approved and coordinate overhead-door threshold.",
            "Separate garage from upper dwelling with listed floor/ceiling assembly using minimum 5/8 in Type X gypsum at garage ceiling. Protect supporting walls/columns and seal penetrations.",
            "Door from garage to protected hall: self-closing/self-latching 20-minute or 1-3/8 in solid wood/steel as accepted; no direct opening into sleeping room.",
            "Mechanical/storage zone is unconditioned unless final energy design encloses equipment. HPWH condensate and pan drain require approved termination.",
            "Owner flex-room zoning classification controls finishes, heating/cooling, and whether lower area counts toward ADU cap. Do not construct as sleeping room.",
            "Overhead door final size: 9 ft 8 in rough planning width. Engineer portal frame/header and manufacturer to provide wind-rated door for 115 mph basis.",
        ]
        schedules = [
            ["ROOM", "FINISH / BASIS", "CEILING"],
            ["Garage/shop", "sealed concrete / painted gypsum", "8'-6\" nominal"],
            ["Mech/storage", "sealed concrete / durable wall finish", "8'-6\" nominal"],
            ["Powder/hall", "tile or resilient / moisture-resistant finish", "8'-0\" min"],
            ["Owner flex", "resilient / gypsum; classification pending", "8'-0\" min"],
        ]
    else:
        notes = [
            "Upper gross floor area: 480 sf. Net interior basis: approximately 437 sf. Final zoning area calculation uses exterior-face definition and approved exclusions.",
            "Sloped ceiling follows roof. Maintain not less than 7 ft over required area and not less than 5 ft at any included floor area; final truss/rafter geometry controls.",
            "Bedroom EERO W02: select casement with at least 5.7 sf net clear, 20 in clear width, 24 in clear height, and sill not over 44 in above floor.",
            "Safety glazing at doors, adjacent glazing, bath/shower, and hazardous locations per VRC R308. Confirm each product and permanently label.",
            "Kitchen island requires receptacle layout per adopted NEC, plumbing/vent coordination, and 42 in preferred clear work aisle. Verify appliance installation clearances.",
            "Apartment entry is side-hinged D05 from connected south landing; large east slider D04 is secondary patio access, not sole conventional entry.",
        ]
        schedules = [
            ["ROOM", "AREA / BASIS", "CEILING"],
            ["Bedroom", "92 sf clear; queen + storage", "sloped, 7 ft compliance zone"],
            ["Bath", "stacked wet core", "sloped, fixtures near ridge"],
            ["Kitchen/living/dining", "open plan", "sloped to 20 ft ridge basis"],
            ["Laundry/storage", "low-eave service zone", "sloped; verify equipment clearance"],
        ]
    note_box(c, 670, 735, 520, 360, "PLAN NOTES", notes, size=7.5)
    table(c, 670, 350, [120, 235, 145], schedules, row_h=38, size=7)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(95, 92, "PLAN SCALE: 1/4 IN = 1 FT WHEN PRINTED 100% ON 11 x 17")
    c.setFont("Helvetica", 6.5)
    c.drawString(
        95,
        80,
        "DO NOT SCALE ELECTRONIC VIEW. DIMENSIONS TO FACE OF STUD UNLESS NOTED; EXTERIOR DIMENSIONS TO FACE OF SHEATHING.",
    )


def roof_sheet(c: canvas.Canvas) -> None:
    sheet(c, 5)
    x, y, s = 70, 315, 18
    c.setStrokeColor(INK)
    c.rect(x, y, 24 * s, 20 * s, fill=0, stroke=1)
    c.line(x, y + 10 * s, x + 24 * s, y + 10 * s)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x + 12 * s, y + 10 * s + 5, "RIDGE - E/W - 19'-10\" MAX BASIS")
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(x + 12 * s, y + 15 * s, "5:12 NORTH ROOF PLANE")
    c.drawCentredString(x + 12 * s, y + 5 * s, "5:12 SOUTH ROOF PLANE")
    c.setDash(3, 2)
    c.line(x + 2 * s, y, x + 2 * s, y + 20 * s)
    c.line(x + 22 * s, y, x + 22 * s, y + 20 * s)
    c.setDash()
    c.drawString(
        x + 4,
        y - 18,
        "NORTH/WEST EDGES FLUSH AT SETBACK BASIS; SOUTH/EAST 12 IN OVERHANG SUBJECT TO ZONING",
    )
    draw_north_arrow(c, x - 25, y + 20 * s - 45)

    note_box(
        c,
        545,
        735,
        300,
        370,
        "ROOF / ATTIC NOTES",
        [
            "Final system: engineered raised-heel roof trusses or engineer-designed rafters at 24 in o.c. maximum; 20 psf ground snow and 115 mph wind basis.",
            "Supplier to coordinate sloped interior ceiling, room partitions, gable-end openings, mechanical penetrations, energy R-value, and maximum 19 ft 10 in ridge.",
            "Provide continuous load path, uplift connectors at every truss/rafter, gable bracing, blocking, and sheathing nailing per sealed truss/structural package.",
            "Asphalt shingles over code-compliant underlayment and 1/2 in minimum roof sheathing basis; final thickness/fastening by span and wind design.",
            "Ventilation strategy by final energy/envelope designer. Do not combine vented and unvented assemblies; avoid soffit vents at setback edges if fire-separation rules prohibit them.",
            "Gutters and downspouts coordinated with site drainage. Ice barrier, drip edge, flashing, crickets, and penetration boots per adopted code and manufacturer.",
        ],
    )
    door_rows = [
        ["MARK", "SIZE BASIS", "TYPE / NOTES"],
        ["D01", "9'-8\" x 7'-0\"", "wind-rated sectional overhead; engineered portal/header"],
        ["D02", "3'-0\" x 6'-8\"", "garage/hall protected, self-closing"],
        ["D03", "6'-0\" x 6'-8\"", "level-1 east slider; safety glazing"],
        ["D04", "6'-0\" x 6'-8\"", "level-2 east slider; safety glazing"],
        ["D05", "3'-0\" x 6'-8\"", "upper apartment entry; outswing/inswing verify"],
    ]
    window_rows = [
        ["MARK", "SIZE BASIS", "TYPE / PERFORMANCE"],
        ["W01", "3'-0\" x 3'-0\"", "garage awning/fixed; tempered if hazardous"],
        ["W02", "3'-6\" x 5'-0\"", "bedroom casement; EERO product data required"],
        ["W03", "5'-0\" x 3'-6\"", "south living; safety glazing check"],
        ["W04", "3'-6\" x 4'-0\"", "east dining; operable/fixed per ventilation"],
        ["ALL", "manufacturer RO", "U <= 0.30 working basis; SHGC <= 0.40"],
    ]
    table(c, 870, 735, [55, 95, 210], door_rows, row_h=36, size=6.7)
    table(c, 870, 475, [55, 95, 210], window_rows, row_h=36, size=6.7)


def elevations_sheet(c: canvas.Canvas) -> None:
    sheet(c, 6)
    draw_elevation(c, 55, 410, 20, "WEST / ALLEY ELEVATION", True, "garage")
    draw_elevation(c, 350, 410, 20, "EAST / YARD ELEVATION", True, "sliders")
    draw_elevation(c, 660, 410, 24, "SOUTH ELEVATION", False, "stair")
    draw_elevation(c, 955, 410, 24, "NORTH ELEVATION", False, "")
    note_box(
        c,
        28,
        360,
        1162,
        270,
        "ELEVATION / EXTERIOR NOTES",
        [
            "Vertical datum: 0'-0\" top of level-1 slab; +9'-3\" top of upper subfloor working basis; +16'-0\" eave/plate basis; +19'-10\" maximum ridge basis. Survey average adjacent grade before finalizing height.",
            "Exterior wall basis: fiber-cement lap siding over drained/ventilated rainscreen, continuous water-resistive barrier, taped structural sheathing, 2x6 framing, cavity insulation, smart vapor retarder where required, and gypsum interior finish.",
            "North and west walls sit at working minimum yards. Keep north wall without openings; show flush north eave and flush west rake until Zoning confirms projections or building is relocated inward.",
            "Exterior wood exposed to weather shall be naturally durable or preservative treated. Provide corrosion-resistant fasteners/connectors compatible with treatment and flashing.",
            "Patio/landing guards shown diagrammatically. Final design must resist prescribed guard loads, reject a 4 in sphere, and include graspable stair handrail 34-38 in above nosings.",
            "Finish palette: muted green-gray lap siding, light trim/guards, dark red-brown doors/windows, dark roof. Final colors do not affect code but historic/design review may apply.",
        ],
        size=7.4,
    )


def sections_sheet(c: canvas.Canvas) -> None:
    sheet(c, 7)
    draw_section(c, 55, 355, longitudinal=False)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(55, 335, "SECTION A - TRANSVERSE / SLOPED CEILING / 1/4 IN = 1 FT")
    draw_section(c, 525, 355, longitudinal=True)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(525, 335, "SECTION B - LONGITUDINAL / 1/4 IN = 1 FT")
    # wall section diagram
    x, y = 980, 355
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(x, y, 90, 330, fill=0, stroke=1)
    c.line(x + 15, y, x + 15, y + 330)
    c.line(x + 35, y, x + 35, y + 330)
    c.line(x + 70, y, x + 70, y + 330)
    labels = [
        (660, "FIBER-CEMENT SIDING + RAINSCREEN"),
        (625, "WRB / FLASHED OPENINGS"),
        (590, "7/16 IN STRUCTURAL SHEATHING"),
        (545, "2x6 STUDS @ 16 IN O.C. / R-20+5ci BASIS"),
        (500, "1/2 IN GYPSUM; AIR-SEAL CONTINUITY"),
        (445, "RIM / FLOOR TRUSS - R-30 FLOOR BASIS"),
        (395, "5/8 IN TYPE X GARAGE CEILING"),
    ]
    c.setFont("Helvetica", 5.7)
    for yy, label in labels:
        c.line(x + 45, yy, x + 100, yy)
        c.drawString(x + 104, yy - 2, label)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x, y - 18, "TYPICAL WALL / FLOOR EDGE - NTS")
    note_box(
        c,
        28,
        305,
        565,
        215,
        "ENVELOPE BASIS",
        [
            "Working prescriptive targets for Climate Zone 4A: U-0.30 windows, R-60 roof/ceiling, R-20+5ci wood walls, R-30 floor over unconditioned garage. Final REScheck/approved alternative governs.",
            "Sloped roof without attic may use approved reduced cavity R-value only where code permits; exterior continuous insulation or raised framing likely needed to preserve headroom and condensation control.",
            "Continuous air barrier around conditioned upper level. Seal rim, top plates, penetrations, bath/laundry, and transition to rated garage ceiling. Blower-door target per adopted energy code.",
            "No shared garage return air. Ducts/air handlers serving dwelling remain inside conditioned envelope where practical.",
        ],
    )
    note_box(
        c,
        615,
        305,
        575,
        215,
        "FOUNDATION / FIRE SECTION BASIS",
        [
            "Continuous footing bottom at least 18 in below finished grade and on undisturbed competent soil. Preliminary footing size is not final without soil and load verification.",
            "Termite treatment/protection, capillary break, sill sealer, pressure-treated sill, anchor bolts, and flashing per adopted code and site conditions.",
            "Garage ceiling below dwelling: listed assembly with 5/8 in Type X minimum at garage side; protect bearing elements and penetrations. Do not install unlisted recessed fixtures in rated membrane.",
            "Smoke alarms inside/outside sleeping area and on each story; CO alarms outside sleeping area and on garage-adjacent story. Interconnect with battery backup.",
        ],
    )


def structural_sheet(c: canvas.Canvas) -> None:
    sheet(c, 8)
    # foundation plan
    ox, oy, s = 55, 390, 14
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.rect(ox, oy, 24 * s, 20 * s, fill=0, stroke=1)
    c.setLineWidth(0.6)
    c.rect(ox + 8, oy + 8, 24 * s - 16, 20 * s - 16, fill=0, stroke=1)
    for xx in (ox + 6 * s, ox + 12 * s, ox + 18 * s):
        c.circle(xx, oy - 4 * s, 6, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(ox, oy + 20 * s + 12, "FOUNDATION PLAN - 1/4 IN = 1 FT")
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(ox + 12 * s, oy + 10 * s, "4 IN SLAB / PERIMETER STEM + FOOTING BASIS")
    c.drawCentredString(
        ox + 12 * s, oy - 4 * s - 12, "STAIR / LANDING PIERS - ENGINEER SIZE / FROST DEPTH"
    )
    # framing plan
    fx, fy = 455, 390
    c.setLineWidth(1)
    c.rect(fx, fy, 24 * s, 20 * s, fill=0, stroke=1)
    for i in range(1, 24):
        xx = fx + i * s
        c.setStrokeColor(GRAY_4)
        c.line(xx, fy, xx, fy + 20 * s)
    c.setStrokeColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(fx, fy + 20 * s + 12, "LEVEL 2 FLOOR FRAMING - 1/4 IN = 1 FT")
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(fx + 12 * s, fy + 10 * s, "20 FT SPAN ENGINEERED FLOOR TRUSSES / I-JOISTS")
    c.drawCentredString(fx + 12 * s, fy + 8.8 * s, "SPAN N-S; OPEN-WEB PREFERRED FOR MEP")
    # roof framing
    rx, ry = 855, 390
    c.setStrokeColor(INK)
    c.rect(rx, ry, 24 * s, 20 * s, fill=0, stroke=1)
    c.line(rx, ry + 10 * s, rx + 24 * s, ry + 10 * s)
    for i in range(0, 25, 2):
        xx = rx + i * s
        c.setStrokeColor(GRAY_4)
        c.line(xx, ry, xx, ry + 20 * s)
    c.setStrokeColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(rx, ry + 20 * s + 12, "ROOF FRAMING - 1/4 IN = 1 FT")
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(
        rx + 12 * s, ry + 10 * s + 5, "ENGINEERED SCISSOR / PARALLEL-CHORD TRUSS BASIS"
    )

    structural_rows = [
        ["ELEMENT", "PRELIMINARY BASIS ONLY", "FINAL REQUIREMENT"],
        [
            "Exterior footing",
            "16 in wide x 8 in thick continuous; (2) #4 cont.",
            "Engineer/geotech verify soil, loads, steps, reinforcement",
        ],
        [
            "Stem wall",
            "8 in concrete/CMU; #4 vertical at 48 in o.c. basis",
            "Final height/reinforcing and drainage by site condition",
        ],
        [
            "Slab",
            "4 in, 3,500 psi; fiber or WWF basis; 10 mil vapor retarder",
            "Jointing, thickening, garage slope, termite treatment",
        ],
        [
            "Floor",
            "11-7/8 in minimum engineered open-web/I-joist at 16 in o.c.",
            "Sealed supplier layout, reactions, holes, blocking",
        ],
        [
            "Garage header",
            "(3) 1-3/4 x 11-7/8 LVL placeholder",
            "Sealed calculation and portal-frame/hold-down design",
        ],
        [
            "East sliders",
            "(2) 1-3/4 x 9-1/2 LVL placeholder",
            "Sealed calculation; point loads carried to foundation",
        ],
        [
            "Roof",
            "engineered trusses at 24 in o.c. max; 5:12 exterior",
            "Sealed truss package, bracing, reactions, uplift",
        ],
        [
            "Stair/patio",
            "6x6 posts; built-up beams; 2x8 joists placeholder",
            "Engineer/member tables, lateral, guards, footing sizes",
        ],
        [
            "Wall bracing",
            "7/16 structural sheathing continuous; portal at garage",
            "Braced-wall calculation, nailing, hold-down schedule",
        ],
    ]
    table(c, 28, 340, [135, 395, 395], structural_rows, row_h=26, size=6.4)
    note_box(
        c,
        975,
        340,
        215,
        250,
        "STRUCTURAL HOLD POINTS",
        [
            "No structural size on this sheet is approved for procurement or construction.",
            "Engineer to establish dead loads including finishes, counters, tile, deck, and MEP.",
            "Carry concentrated header/truss loads to footing with posts and squash blocks.",
            "Coordinate all penetrations before fabrication. No field cuts in engineered members without written approval.",
            "Provide continuous load path roof-to-foundation for 115 mph wind.",
        ],
        size=6.6,
    )


def mep_sheet(c: canvas.Canvas) -> None:
    sheet(c, 9)
    # riser diagram
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    x, y = 55, 410
    c.rect(x, y, 310, 270, fill=0, stroke=1)
    c.line(x, y + 130, x + 310, y + 130)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x + 8, y + 247, "LEVEL 2 - BATH / LAUNDRY / KITCHEN")
    c.drawString(x + 8, y + 113, "LEVEL 1 - POWDER / MECH / GARAGE")
    c.setFont("Helvetica", 6)
    c.drawString(x + 20, y + 205, "BATH GROUP")
    c.drawString(x + 120, y + 205, "W/D")
    c.drawString(x + 205, y + 205, "KITCHEN ISLAND")
    c.line(x + 55, y + 195, x + 55, y + 35)
    c.line(x + 140, y + 195, x + 140, y + 35)
    c.line(x + 250, y + 195, x + 250, y + 35)
    c.line(x + 55, y + 45, x + 280, y + 45)
    c.drawString(x + 20, y + 20, "4 IN BUILDING DRAIN -> VERIFY GRAVITY INVERT")
    c.drawString(x + 180, y + 85, "HPWH / MANIFOLD")
    c.drawString(x + 20, y + 85, "LOWER POWDER")
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x, y - 15, "PLUMBING / DWV RISER - DIAGRAMMATIC")

    # electrical single line
    ex = 405
    c.rect(ex, y, 330, 270, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(ex + 10, y + 247, "ELECTRICAL SINGLE-LINE BASIS")
    boxes = [(ex + 20, "EXISTING SERVICE"), (ex + 125, "FEEDER / DISC"), (ex + 235, "ADU PANEL")]
    for bx, label in boxes:
        c.rect(bx, y + 150, 75, 45, fill=0, stroke=1)
        c.setFont("Helvetica", 5.8)
        c.drawCentredString(bx + 37.5, y + 170, label)
    c.line(ex + 95, y + 172, ex + 125, y + 172)
    c.line(ex + 200, y + 172, ex + 235, y + 172)
    c.setFont("Helvetica", 6)
    c.drawString(ex + 20, y + 120, "125 A PANEL WORKING BASIS - FINAL LOAD CALC CONTROLS")
    c.drawString(ex + 20, y + 100, "4-WIRE FEEDER; DETACHED-BUILDING DISCONNECT")
    c.drawString(ex + 20, y + 80, "GROUNDING ELECTRODE SYSTEM + ISOLATED NEUTRAL")
    c.drawString(ex + 20, y + 60, "AFCI/GFCI, SURGE, EV/PV READY CONDUIT AS SELECTED")
    c.drawString(ex + 20, y + 40, "NO PROCUREMENT UNTIL SERVICE CAPACITY / FAULT CURRENT VERIFIED")
    c.setFont("Helvetica-Bold", 7)
    c.drawString(ex, y - 15, "ELECTRICAL BASIS - 2020 NEC / VIRGINIA ADOPTION")

    # HVAC zoning
    hx = 775
    c.rect(hx, y, 415, 270, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(hx + 10, y + 247, "MECHANICAL / VENTILATION BASIS")
    mech_notes = [
        "All-electric, cold-climate variable-speed heat pump; 1.0-1.5 ton placeholder only.",
        "Manual J load, Manual S equipment selection, and distribution design required.",
        "Preferred: compact ducted air handler inside conditioned upper core; no garage return air.",
        "Whole-dwelling ventilation sized to adopted code; balanced ERV basis if feasible.",
        "Bath exhaust direct outdoors; range hood direct outdoors and sized/makeup-air coordinated.",
        "Dryer vent shortest route outdoors; listed duct, cleanout access, no concealed screws.",
        "HPWH in sealed/insulated level-1 mechanical closet or ducted per manufacturer; manage noise/condensate.",
    ]
    yy = y + 220
    for i, note in enumerate(mech_notes, 1):
        yy = text_block(c, note, hx + 15, yy, 380, size=6.5, bullet=f"{i}.") - 5

    life_rows = [
        ["SYSTEM", "LOCATIONS / BASIS", "FINAL ACTION"],
        [
            "Smoke alarms",
            "inside bedroom, outside bedroom, each story; interconnected",
            "Electrical plan and adopted R314",
        ],
        [
            "CO alarms",
            "outside bedroom and garage-adjacent story",
            "Adopted R315 / product listing",
        ],
        [
            "Receptacles",
            "dwelling wall spacing; kitchen, bath, laundry, exterior, garage",
            "NEC layout / AFCI-GFCI",
        ],
        [
            "Lighting",
            "stairs/landings, exterior doors, garage, rooms; high efficacy",
            "3-way stair controls / energy code",
        ],
        [
            "Fire separation",
            "garage ceiling/supports, protected door, sealed penetrations",
            "Listed assemblies and inspection",
        ],
        ["Water protection", "pans/leak sensors at HPWH and washer", "Approved drains/shutoffs"],
    ]
    table(c, 28, 350, [110, 430, 300], life_rows, row_h=34, size=6.6)
    note_box(
        c,
        895,
        350,
        295,
        260,
        "MEP COORDINATION HOLDS",
        [
            "Trade designers own final sizing, permits, and installation documents.",
            "Verify existing service, water pressure, sewer route/invert, and utility provider rules before foundation.",
            "Keep plumbing in stacked wet core and route floor penetrations away from engineered member no-cut zones.",
            "Air-seal and firestop every garage separation penetration with listed systems.",
            "Coordinate exterior equipment clearances with property line, windows, stair, drainage, and noise.",
        ],
        size=6.8,
    )


def closeout_sheet(c: canvas.Canvas) -> None:
    sheet(c, 10)
    spec_rows = [
        ["DIVISION", "SCHEMATIC BASIS", "REQUIRED BEFORE CONSTRUCTION"],
        [
            "01 General",
            "Field verify; protect occupied house; maintain egress and utilities",
            "Permit set, contractor scope, schedule, insurance, safety plan",
        ],
        [
            "02 Existing",
            "Remove 12 x 18 field shed; protect trees/fence; reconcile assessor record",
            "Demo permit/zoning, utility locate, hazardous-material review",
        ],
        [
            "03 Concrete",
            "3,500 psi basis; continuous footings/stem; 4 in slab",
            "Geotech/soil verification, engineered foundation, mix/joint plan",
        ],
        [
            "06 Wood",
            "2x6 walls; engineered floor/roof; PT exterior framing",
            "Sealed calculations, shop drawings, connector/fastener schedule",
        ],
        [
            "07 Envelope",
            "WRB, rainscreen, fiber cement, asphalt roof, continuous air barrier",
            "Hygrothermal/energy check, flashing details, product approvals",
        ],
        [
            "08 Openings",
            "wind-rated windows/doors; EERO; safety glazing",
            "Manufacturer data, rough openings, U/SHGC, design-pressure ratings",
        ],
        [
            "09 Finishes",
            "durable garage finish; moisture-resistant wet areas",
            "Owner selections, flame/smoke compliance, substrate coordination",
        ],
        [
            "21 Fire",
            "alarms; garage separation; fireblocking",
            "Listed assemblies, penetration systems, inspection sign-off",
        ],
        [
            "22 Plumbing",
            "stacked wet core; all-electric DHW; gravity sewer basis",
            "Trade permit, fixture-unit sizing, sewer invert, water service",
        ],
        [
            "23 HVAC",
            "heat pump + balanced ventilation basis",
            "Manual J/S/D, ventilation calculation, condensate plan",
        ],
        [
            "26 Electrical",
            "125 A panel placeholder; all-electric loads",
            "Service/load calc, feeder, grounding, circuiting, trade permit",
        ],
        [
            "31 Earthwork",
            "positive drainage; compacted subbase; erosion controls",
            "Survey, grading/drainage plan, RESMP determination",
        ],
    ]
    table(c, 28, 735, [95, 435, 360], spec_rows, row_h=30, size=6.4)
    note_box(
        c,
        945,
        735,
        245,
        390,
        "OWNER DECISIONS",
        [
            "Confirm Option F as final layout and whether lower flex room remains owner-only/non-ADU space.",
            "Choose flush setback-side roof edges or authorize survey/zoning study for inward shift and overhangs.",
            "Confirm exterior stair weather protection, decking material, guard style, and maintenance access.",
            "Confirm all-electric program, EV/PV readiness, induction cooking, dryer type, and HPWH location.",
            "Select window operation while preserving bedroom EERO, natural ventilation, privacy, and safety glazing.",
            "Choose foundation strategy after survey/soil: slab/stem basis versus crawlspace or engineered thickened edge.",
            "Confirm budget and whether replacement shed is same-phase construction.",
        ],
        size=6.8,
    )
    note_box(
        c,
        28,
        320,
        565,
        230,
        "PRE-PERMIT COMPLETION CHECKLIST",
        [
            "Boundary/topographic survey with grades, easements, structures, trees, and utility evidence.",
            "Written Zoning confirmation: ADU area/exclusions, lower flex/powder classification, setbacks/projections, height, lot coverage, shed, access.",
            "Architectural permit drawings with fully dimensioned plans, four elevations, sections, openings, finishes, stair/guard details, and code analysis.",
            "Structural package: soil basis, foundation, floor/roof layouts, headers, portal/lateral design, deck/stair, braced-wall information, calculations and seals where required.",
            "Energy compliance: REScheck or prescriptive schedule; final window values, assemblies, air sealing, ventilation, and equipment efficiencies.",
            "Separate trade designs/permits and utility approvals; confirm Fire/Public Works/Water Resources routing.",
        ],
    )
    note_box(
        c,
        615,
        320,
        575,
        230,
        "CONSTRUCTION / INSPECTION HOLD POINTS",
        [
            "Preconstruction: approved plans on site, survey staking, erosion controls, utility locate, tree protection.",
            "Footing: bearing soil, location, depth, size, reinforcing, and step geometry before concrete.",
            "Foundation/slab: forms/CMU, anchorage, underslab trades, subbase, vapor retarder, reinforcement, termite provisions.",
            "Framing: approved engineered packages, member sizes, nailing, bracing, hold-downs, connectors, fireblocking, rough trades before concealment.",
            "Fire separation/insulation: rated membrane and penetrations; air barrier and R-values before cover.",
            "Final: stairs, guards, alarms, EERO, safety glazing, address, drainage, trade finals, zoning/land-disturbance/public-works finals, certificate of occupancy.",
        ],
    )


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("Option F ADU - Construction and Engineering Basis Set")
    c.setAuthor("Owner coordination basis - generated from adu_adoration project")
    cover(c)
    code_sheet(c)
    site_sheet(c)
    floor_sheet(c, 3, 1)
    floor_sheet(c, 4, 2)
    roof_sheet(c)
    elevations_sheet(c)
    sections_sheet(c)
    structural_sheet(c)
    mep_sheet(c)
    closeout_sheet(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
