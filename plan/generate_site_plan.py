"""Generate an architect-ready site plan (DXF + PDF) for the 112 W 29th St ADU.

Coordinate system: 1 drawing unit = 1 foot. X = East (toward street),
Y = North. Origin (0,0) = southwest (alley + south line) lot corner.
West (X=0) = alley/rear, East (X=148) = street/front. North = +Y (up).

Run:  uv run --no-project --with ezdxf --with matplotlib python3 plan/generate_site_plan.py
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment

DATE = "2026-06-28"
FRONT_SETBACK = 16.0  # main east wall to front lot line — FIELD-VERIFY

doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.FT
msp = doc.modelspace()

# ---- layers (ACI colors) ----
doc.layers.add("LOT-BOUNDARY", color=250)   # dark; ACI 7 renders white-on-white in preview
doc.layers.add("EXISTING-HOUSE", color=8)
doc.layers.add("EXISTING-HOUSE-DETAIL", color=9, linetype="DASHED")
doc.layers.add("EXISTING-SHED", color=8)
doc.layers.add("PROPOSED-ADU", color=5)
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
    d = msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, dimstyle="FT",
                            dxfattribs={"layer": layer})
    d.render()


# ---- lot 45 x 148 ----
poly([(0, 0), (148, 0), (148, 45), (0, 45)], "LOT-BOUNDARY")

# ---- existing house (porch NE, deck SW); east wall at FRONT_SETBACK ----
ew = 148 - FRONT_SETBACK          # main east wall x  (=132 @ 16')
hw = ew - 48                       # heated west face  (48' deep)
rd = hw + 13                       # rear/main division
# silhouette outline
poly([
    (ew + 7, 36),   # porch NE  (porch projects 7' east)
    (hw, 36),       # north edge
    (hw, 24),       # west face down to deck
    (hw - 9, 24),   # deck NW (projects 9' west)
    (hw - 9, 9),    # deck SW
    (hw, 9),        # deck SE / heated SW
    (ew, 9),        # heated SE
    (ew, 23.6),     # up east wall to porch
    (ew + 7, 23.6), # porch SE
], "EXISTING-HOUSE")
line((rd, 9), (rd, 36), "EXISTING-HOUSE-DETAIL")        # main/rear
line((ew, 23.6), (ew, 36), "EXISTING-HOUSE-DETAIL")     # porch/main
line((hw, 9), (hw, 24), "EXISTING-HOUSE-DETAIL")        # deck/house

# ---- existing shed 12x18, SW corner: 8' off alley, 6' off south ----
poly([(8, 6), (26, 6), (26, 18), (8, 18)], "EXISTING-SHED")

# ---- proposed ADU 20x24: 5' off alley, 3' off north line ----
poly([(5, 22), (29, 22), (29, 42), (5, 42)], "PROPOSED-ADU")
poly([(5, 26), (6.5, 26), (6.5, 38), (5, 38)], "PROPOSED-ADU")  # garage door @ alley

# ---- R-5 required yards (dashed reference) ----
line((0, 5), (148, 5), "R5-SETBACK")      # side 5'
line((0, 40), (148, 40), "R5-SETBACK")    # side 5'
line((5, 0), (5, 45), "R5-SETBACK")       # rear 5'
line((123, 0), (123, 45), "R5-SETBACK")   # front 25'

# ---- dimensions ----
dimen((0, 0), (148, 0), -9)               # lot length
dimen((0, 0), (0, 45), -9)                # lot width
dimen((8, 6), (26, 6), -3)                # shed 18 deep
dimen((8, 6), (8, 18), -3)                # shed 12 wide
dimen((0, 6), (8, 6), 3)                  # shed 8' off alley (uses x=0 alley)
dimen((5, 42), (29, 42), 4)               # ADU 24 deep
dimen((29, 22), (29, 42), 5)              # ADU 20 wide
dimen((0, 30), (5, 30), 3)                # ADU 5' off alley
dimen((29, 45), (29, 42), 6)              # ADU 3' off north
dimen((ew, 9), (148, 9), -4)              # front setback (verify)

# ---- labels ----
label("EXISTING HOUSE  1-STORY  1,303 SF", (rd + 17), 22, 2.0, align=TextEntityAlignment.MIDDLE_CENTER)
label("(built 1931)", (rd + 17), 18.5, 1.5, layer="TEXT")
label("PORCH", ew + 3.5, 30, 1.3)
label("DECK", hw - 4.5, 16, 1.3)
label("EXISTING\nSHED 12x18", 17, 12, 1.5)
label("PROPOSED ADU", 17, 38, 2.0, layer="PROPOSED-ADU")
label("20 x 24  -  2 STORY", 17, 35, 1.6, layer="PROPOSED-ADU")
label("GARAGE BELOW / 1-BED ABOVE", 17, 32, 1.4, layer="PROPOSED-ADU")
label("GARAGE DOOR -> ALLEY", 17, 29, 1.3, layer="PROPOSED-ADU")
label("ALLEY (REAR)", -5, 22.5, 1.8, align=TextEntityAlignment.MIDDLE_CENTER)
label("W 29TH ST (FRONT)", 154, 22.5, 1.8, align=TextEntityAlignment.MIDDLE_CENTER)
label("R-5 REQ'D YARD (5' SIDE / 5' REAR / 25' FRONT)", 74, 47, 1.4, layer="R5-SETBACK")
label("ADU N. SETBACK 3' < R-5 MIN 5' - VARIANCE REQUIRED", 60, 43.4, 1.3, layer="R5-SETBACK")
label("FRONT SETBACK - FIELD-VERIFY", ew + 9, 6, 1.3, layer="DIMENSIONS",
      align=TextEntityAlignment.MIDDLE_LEFT)

# ---- north arrow (north = +Y) ----
ax, ay = 6, 52
line((ax, ay), (ax, ay + 6), "NORTH-ARROW")
poly([(ax - 1.2, ay + 4.5), (ax, ay + 6), (ax + 1.2, ay + 4.5)], "NORTH-ARROW")
label("N", ax, ay + 8, 2.2, layer="NORTH-ARROW")

# ---- graphic scale bar (0-10-20-30 ft) ----
sx, sy = 40, -16
for i in range(3):
    fill = i % 2
    msp.add_lwpolyline([(sx + i * 10, sy), (sx + (i + 1) * 10, sy),
                        (sx + (i + 1) * 10, sy + 1.2), (sx + i * 10, sy + 1.2)],
                       close=True, dxfattribs={"layer": "TEXT"})
for i, t in enumerate(["0", "10", "20", "30 FT"]):
    label(t, sx + i * 10, sy - 2.2, 1.3, align=TextEntityAlignment.MIDDLE_CENTER)

# ---- title block ----
label("ADU SITE PLAN  -  112 W 29TH ST, RICHMOND VA 23225", 74, -24, 2.6,
      align=TextEntityAlignment.MIDDLE_CENTER)
label("PIN S0001130005  -  ZONE R-5  -  LOT 45' x 148' (6,660 SF)  -  1 UNIT = 1 FOOT  -  " + DATE,
      74, -28, 1.6, align=TextEntityAlignment.MIDDLE_CENTER)
label("PRELIMINARY - NOT FOR CONSTRUCTION - DIMENSIONS APPROX, FIELD-VERIFY",
      74, -31.5, 1.6, layer="R5-SETBACK", align=TextEntityAlignment.MIDDLE_CENTER)

doc.saveas("plan/site-plan.dxf")
print("wrote plan/site-plan.dxf")

# ---- PDF export via matplotlib backend ----
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_aspect("equal")
    ax.axis("off")
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(msp, finalize=True)
    fig.savefig("plan/site-plan-architect.pdf", dpi=200, facecolor="white")
    print("wrote plan/site-plan-architect.pdf")
except Exception as e:
    print("PDF export skipped:", e)
