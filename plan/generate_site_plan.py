"""Generate an architect-ready site plan (DXF + PDF) for the 112 W 29th St ADU.

Coordinate system: 1 drawing unit = 1 foot. X = East (toward street),
Y = North. Origin (0,0) = southwest (alley + south line) lot corner.
West (X=0) = alley/rear, East (X=148) = street/front. North = +Y (up).

Run Option E:  uv run --no-project --with ezdxf --with matplotlib python3 plan/generate_site_plan.py
Run Option F:  uv run --no-project --with ezdxf --with matplotlib python3 plan/generate_site_plan.py --option F
"""

import argparse

import ezdxf
import ezdxf.units
from ezdxf.enums import TextEntityAlignment

parser = argparse.ArgumentParser()
parser.add_argument("--option", choices=("E", "F"), default="E")
args = parser.parse_args()
OPTION = args.option
OUTPUT_STEM = "site-plan" if OPTION == "E" else "site-plan-option-f"

DATE = "2026-08-03" if OPTION == "F" else "2026-08-02"
FRONT_SETBACK = 25.0  # MEASURED: main east wall to front (east) lot line (inside of sidewalk)
PORCH_PROJECTION = 2.0  # MEASURED: front porch protrudes ~2 ft east of the house wall

# Enclosed footprint remains 24' E-W x 20' N-S. Option E retains the continuous
# south/east balcony. Option F keeps a 4'-wide south landing connected around
# the southeast corner to 4'-deep stacked east patios. Both leave 5' clear to
# the selected shed.
ADU_WEST, ADU_SOUTH = 5.0, 20.0
ADU_DEPTH, ADU_WIDTH = 24.0, 20.0
STAIR_WEST, STAIR_EAST, STAIR_SOUTH = 5.5, 16.5, 16.0
LANDING_EAST = 32.5  # wraps around SE corner to patio outer edge
PATIO_WEST, PATIO_EAST = 29.0, 32.5
PATIO_SOUTH, PATIO_NORTH = 20.0, 39.5
F_LANDING_EAST = 33.0
F_PATIO_WEST, F_PATIO_EAST = 29.0, 33.0
F_PATIO_SOUTH, F_PATIO_NORTH = 20.0, 39.5
SHED_WEST, SHED_SOUTH = 8.0, 5.0
SHED_DEPTH, SHED_WIDTH = 18.0, 6.0
SHED_EAST = SHED_WEST + SHED_DEPTH
SHED_NORTH = SHED_SOUTH + SHED_WIDTH

doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.FT
msp = doc.modelspace()

# ---- layers (ACI colors) ----
doc.layers.add("LOT-BOUNDARY", color=250)  # dark; ACI 7 renders white-on-white in preview
doc.layers.add("EXISTING-HOUSE", color=8)
doc.layers.add("EXISTING-HOUSE-DETAIL", color=9, linetype="DASHED")
doc.layers.add("EXISTING-SHED-REMOVE", color=1, linetype="DASHED")
doc.layers.add("PROPOSED-SHED", color=3)
doc.layers.add("PROPOSED-ADU", color=5)
doc.layers.add("PROPOSED-ADU-ACCESS", color=4)
doc.layers.add("R5-SETBACK", color=1, linetype="DASHED")
doc.layers.add("DIMENSIONS", color=3)
doc.layers.add("TEXT", color=250)
doc.layers.add("NORTH-ARROW", color=250)

# ---- dimension style (feet-scaled) ----
dim = doc.dimstyles.new("FT")
dim.dxf.dimtxt = 1.8
dim.dxf.dimasz = 1.2
dim.dxf.dimexe = 0.6
dim.dxf.dimexo = 0.6
dim.dxf.dimgap = 0.5
dim.dxf.dimdec = 0
dim.dxf.dimlfac = 1.0


def poly(points, layer, closed=True):
    msp.add_lwpolyline(points, close=closed, dxfattribs={"layer": layer})


def line(a, b, layer):
    msp.add_line(a, b, dxfattribs={"layer": layer})


def label(text, x, y, h=2.0, layer="TEXT", align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(text, height=h, dxfattribs={"layer": layer}).set_placement((x, y), align=align)


def dimen(p1, p2, dist, layer="DIMENSIONS"):
    d = msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, dimstyle="FT", dxfattribs={"layer": layer})
    d.render()


# ---- lot 45 x 148 ----
poly([(0, 0), (148, 0), (148, 45), (0, 45)], "LOT-BOUNDARY")

# ---- existing house (porch NE, deck SW); east wall at FRONT_SETBACK ----
ew = 148 - FRONT_SETBACK  # main east wall x  (=132 @ 16')
hw = ew - 48  # heated west face  (48' deep)
rd = hw + 13  # rear/main division
# silhouette outline
pp = PORCH_PROJECTION
poly(
    [
        (ew + pp, 36),  # porch NE  (porch projects east of the wall)
        (hw, 36),  # north edge
        (hw, 24),  # west face down to deck
        (hw - 9, 24),  # deck NW (projects 9' west)
        (hw - 9, 9),  # deck SW
        (hw, 9),  # deck SE / heated SW
        (ew, 9),  # heated SE
        (ew, 23.6),  # up east wall to porch
        (ew + pp, 23.6),  # porch SE
    ],
    "EXISTING-HOUSE",
)
line((rd, 9), (rd, 36), "EXISTING-HOUSE-DETAIL")  # main/rear
line((ew, 23.6), (ew, 36), "EXISTING-HOUSE-DETAIL")  # porch/main
line((hw, 9), (hw, 24), "EXISTING-HOUSE-DETAIL")  # deck/house

# ---- shed replacement: old 12x18 removed; new low-profile 18x6 ----
poly([(8, 6), (26, 6), (26, 18), (8, 18)], "EXISTING-SHED-REMOVE")
poly(
    [
        (SHED_WEST, SHED_SOUTH),
        (SHED_EAST, SHED_SOUTH),
        (SHED_EAST, SHED_NORTH),
        (SHED_WEST, SHED_NORTH),
    ],
    "PROPOSED-SHED",
)

# ---- proposed ADU: Option E enclosed footprint + exterior circulation ----
adu_east = ADU_WEST + ADU_DEPTH
adu_north = ADU_SOUTH + ADU_WIDTH
poly(
    [(ADU_WEST, ADU_SOUTH), (adu_east, ADU_SOUTH), (adu_east, adu_north), (ADU_WEST, adu_north)],
    "PROPOSED-ADU",
)
poly([(ADU_WEST, 24), (6.5, 24), (6.5, 36), (ADU_WEST, 36)], "PROPOSED-ADU")

# South exterior stair begins at the alley and rises east. Its raised landing
# shelters a 16' x 4' level-1 patio and continues to the stacked east patio.
poly(
    [
        (STAIR_WEST, STAIR_SOUTH),
        (STAIR_EAST, STAIR_SOUTH),
        (STAIR_EAST, ADU_SOUTH),
        (STAIR_WEST, ADU_SOUTH),
    ],
    "PROPOSED-ADU-ACCESS",
)
for i in range(1, 13):
    x = STAIR_WEST + (STAIR_EAST - STAIR_WEST) * i / 13
    line((x, STAIR_SOUTH), (x, ADU_SOUTH), "PROPOSED-ADU-ACCESS")
if OPTION == "E":
    # Landing wraps around the southeast corner to the continuous east patio.
    poly(
        [
            (STAIR_EAST, STAIR_SOUTH),
            (LANDING_EAST, STAIR_SOUTH),
            (LANDING_EAST, ADU_SOUTH),
        ],
        "PROPOSED-ADU-ACCESS",
        closed=False,
    )
    line((STAIR_EAST, ADU_SOUTH), (PATIO_WEST, ADU_SOUTH), "PROPOSED-ADU-ACCESS")
    poly(
        [
            (PATIO_WEST, PATIO_SOUTH),
            (PATIO_WEST, PATIO_NORTH),
            (PATIO_EAST, PATIO_NORTH),
            (PATIO_EAST, PATIO_SOUTH),
        ],
        "PROPOSED-ADU-ACCESS",
        closed=False,
    )
else:
    # Recommended Option F: landing continues around the southeast corner to
    # full east patios serving large sliders on both floors.
    poly(
        [
            (STAIR_EAST, STAIR_SOUTH),
            (F_LANDING_EAST, STAIR_SOUTH),
            (F_LANDING_EAST, ADU_SOUTH),
        ],
        "PROPOSED-ADU-ACCESS",
        closed=False,
    )
    line((STAIR_EAST, ADU_SOUTH), (F_PATIO_WEST, ADU_SOUTH), "PROPOSED-ADU-ACCESS")
    poly(
        [
            (F_PATIO_WEST, F_PATIO_SOUTH),
            (F_PATIO_WEST, F_PATIO_NORTH),
            (F_PATIO_EAST, F_PATIO_NORTH),
            (F_PATIO_EAST, F_PATIO_SOUTH),
        ],
        "PROPOSED-ADU-ACCESS",
        closed=False,
    )

# ---- R-5 required yards (dashed reference) ----
line((0, 5), (148, 5), "R5-SETBACK")  # side 5'
line((0, 40), (148, 40), "R5-SETBACK")  # side 5'
line((5, 0), (5, 45), "R5-SETBACK")  # rear 5'
line((123, 0), (123, 45), "R5-SETBACK")  # front 25'

# ---- dimensions ----
dimen((0, 0), (148, 0), -9)  # lot length
dimen((0, 0), (0, 45), -9)  # lot width
dimen((SHED_WEST, SHED_SOUTH), (SHED_EAST, SHED_SOUTH), -3)  # shed 18 deep
dimen((SHED_WEST, SHED_SOUTH), (SHED_WEST, SHED_NORTH), -3)  # shed 6 wide
dimen((0, SHED_SOUTH), (SHED_WEST, SHED_SOUTH), 3)  # shed 8' off alley
dimen((12, SHED_NORTH), (12, STAIR_SOUTH), -3)  # shed-to-stair clearance
dimen((ADU_WEST, adu_north), (adu_east, adu_north), 4)  # enclosed ADU 24 deep
dimen((adu_east, ADU_SOUTH), (adu_east, adu_north), 5)  # enclosed ADU 20 wide
dimen((0, 30), (ADU_WEST, 30), 3)  # ADU 5' off alley
dimen((adu_east, 45), (adu_east, adu_north), 6)  # ADU 5' off north
dimen((STAIR_WEST, STAIR_SOUTH), (STAIR_WEST, ADU_SOUTH), -3)  # stair depth
if OPTION == "E":
    dimen((PATIO_WEST, 32), (PATIO_EAST, 32), 3)  # patio depth
else:
    dimen((F_PATIO_WEST, 32), (F_PATIO_EAST, 32), 3)
dimen((ew, 9), (148, 9), -4)  # front setback (measured 25')
dimen((SHED_EAST, SHED_SOUTH), (hw - 9, SHED_SOUTH), 3)  # deck-to-shed clearance

# ---- labels ----
label(
    "EXISTING HOUSE  1-STORY  1,303 SF", (rd + 17), 22, 2.0, align=TextEntityAlignment.MIDDLE_CENTER
)
label("(built 1931)", (rd + 17), 18.5, 1.5, layer="TEXT")
label("PORCH", ew + 3.5, 30, 1.3)
label("DECK", hw - 4.5, 16, 1.3)
label("EXISTING 12x18 SHED - REMOVE", 17, 12.7, 0.9, layer="EXISTING-SHED-REMOVE")
label("REPLACEMENT SHED", 17, 8.8, 1.2, layer="PROPOSED-SHED")
label("18 x 6  -  108 SF - LOW PROFILE", 17, 6.7, 0.9, layer="PROPOSED-SHED")
label(f"OPTION {OPTION} ADU", 17, 36, 1.8, layer="PROPOSED-ADU")
label("20 x 24  -  2 STORY", 17, 33, 1.6, layer="PROPOSED-ADU")
label(
    "FULL-DEPTH GARAGE / CORE BELOW" if OPTION == "F" else "GARAGE / PROGRAM BELOW",
    15.5 if OPTION == "F" else 17,
    30,
    1.0 if OPTION == "F" else 1.1,
    layer="PROPOSED-ADU",
)
label("1-BED ABOVE", 17, 27.5, 1.2, layer="PROPOSED-ADU")
label(
    "STAIR ENTRY FROM ALLEY" if OPTION == "F" else "DOOR -> ALLEY",
    17,
    25,
    1.0,
    layer="PROPOSED-ADU",
)

# Put access notes in open yard rather than crowding the 4' bands.
if OPTION == "E":
    line((23, 18), (35, 18), "PROPOSED-ADU-ACCESS")
    label(
        "OPTION E: 11' STAIR + 16' x 4' COVERED PATIO / UPPER LANDING + 3'-6\" EAST PATIOS",
        36,
        18,
        1.0,
        layer="PROPOSED-ADU-ACCESS",
        align=TextEntityAlignment.MIDDLE_LEFT,
    )
    label(
        "COVERED PATIO BELOW - OPEN CONNECTION ABOVE", 30.75, 17, 0.75, layer="PROPOSED-ADU-ACCESS"
    )
else:
    line((32, 26), (42, 26), "PROPOSED-ADU-ACCESS")
    label(
        "OPTION F: 11' STAIR + 16'-6\" x 4' CONNECTED LANDING + 4' x 19'-6\" EAST PATIOS",
        43,
        26,
        1.0,
        layer="PROPOSED-ADU-ACCESS",
        align=TextEntityAlignment.MIDDLE_LEFT,
    )
    label(
        "14 RISERS / 13 TREADS - FINAL SECTION TO VERIFY",
        43,
        24.6,
        0.8,
        layer="PROPOSED-ADU-ACCESS",
        align=TextEntityAlignment.MIDDLE_LEFT,
    )
label("5' CLEAR", 30, 14.0, 0.85, layer="PROPOSED-SHED")
label("ALLEY (REAR)", -5, 22.5, 1.8, align=TextEntityAlignment.MIDDLE_CENTER)
label("W 29TH ST (FRONT)", 154, 22.5, 1.8, align=TextEntityAlignment.MIDDLE_CENTER)
label("R-5 REQ'D YARD (5' SIDE / 5' REAR / 25' FRONT)", 74, 47, 1.4, layer="R5-SETBACK")
label("ADU N. SETBACK 5' - R-5 MIN MET", 72, 43.4, 1.3, layer="DIMENSIONS")
label(
    "FRONT SETBACK 25' (MEASURED)",
    ew + 11,
    6,
    1.3,
    layer="DIMENSIONS",
    align=TextEntityAlignment.MIDDLE_LEFT,
)
label("DECK-TO-SHED", (26 + hw - 9) / 2, 4, 1.2, layer="DIMENSIONS")

# ---- north arrow (north = +Y) ----
ax, ay = 6, 52
line((ax, ay), (ax, ay + 6), "NORTH-ARROW")
poly([(ax - 1.2, ay + 4.5), (ax, ay + 6), (ax + 1.2, ay + 4.5)], "NORTH-ARROW")
label("N", ax, ay + 8, 2.2, layer="NORTH-ARROW")

# ---- graphic scale bar (0-10-20-30 ft) ----
sx, sy = 40, -16
for i in range(3):
    fill = i % 2
    msp.add_lwpolyline(
        [
            (sx + i * 10, sy),
            (sx + (i + 1) * 10, sy),
            (sx + (i + 1) * 10, sy + 1.2),
            (sx + i * 10, sy + 1.2),
        ],
        close=True,
        dxfattribs={"layer": "TEXT"},
    )
for i, t in enumerate(["0", "10", "20", "30 FT"]):
    label(t, sx + i * 10, sy - 2.2, 1.3, align=TextEntityAlignment.MIDDLE_CENTER)

# ---- title block ----
label(
    "ADU SITE PLAN  -  112 W 29TH ST, RICHMOND VA 23225",
    74,
    -24,
    2.6,
    align=TextEntityAlignment.MIDDLE_CENTER,
)
label(
    "PIN S0001130005  -  ZONE R-5  -  LOT 45' x 148' (6,660 SF)  -  1 UNIT = 1 FOOT  -  " + DATE,
    74,
    -28,
    1.6,
    align=TextEntityAlignment.MIDDLE_CENTER,
)
label(
    "PRELIMINARY - NOT FOR CONSTRUCTION - DIMENSIONS APPROX, FIELD-VERIFY",
    74,
    -31.5,
    1.6,
    layer="R5-SETBACK",
    align=TextEntityAlignment.MIDDLE_CENTER,
)

DXF_PATH = f"plan/{OUTPUT_STEM}.dxf"
PDF_PATH = f"plan/{OUTPUT_STEM}-architect.pdf"
PNG_PATH = f"plan/{OUTPUT_STEM}.png"
doc.saveas(DXF_PATH)
print(f"wrote {DXF_PATH}")

# ---- PDF export via matplotlib backend ----
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes((0.02, 0.02, 0.96, 0.96))
    ax.set_aspect("equal")
    ax.axis("off")
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(msp, finalize=True)
    fig.savefig(PDF_PATH, dpi=200, facecolor="white")
    fig.savefig(PNG_PATH, dpi=200, facecolor="white")
    print(f"wrote {PDF_PATH}")
    print(f"wrote {PNG_PATH}")
except Exception as e:
    print("PDF export skipped:", e)
