"""Generate a 3D massing model of the 112 W 29th St lot: existing house,
existing shed, and the proposed 20x24 ADU.

Same coordinate system as plan/generate_site_plan.py: 1 unit = 1 foot,
X = East (toward street), Y = North, Z = up. Origin = SW lot corner
(alley + south line). Lot is 45 (N-S) x 148 (E-W).

Outputs (all written next to this script):
  site-model.obj / site-model.mtl  -- true-scale 3D model (Y-up, feet) for
                                      SketchUp / Blender / any OBJ viewer
  site-model-3d.html               -- self-contained interactive viewer
                                      (orbit / zoom / pan, layer toggles);
                                      no internet needed, open in a browser

Run:  python3 model/generate_3d_model.py   (stdlib only, no deps)
"""

import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-07-03"

# ---------------- site geometry (matches plan/generate_site_plan.py) --------
LOT_L, LOT_W = 148.0, 45.0
FRONT_SETBACK = 25.0  # measured 2026-06-28
PORCH_PROJECTION = 2.0
EW = LOT_L - FRONT_SETBACK  # house main east wall  = 123
HW = EW - 48  # house west face       = 75  (48' deep)
HS, HN = 9.0, 36.0  # house south / north walls (27' wide)
DECK = (HW - 9, HS, HW, 24.0)  # 9x15 deck, SW
PORCH = (EW, 23.6, EW + PORCH_PROJECTION, HN)  # open porch, NE
SHED = (8.0, 6.0, 26.0, 18.0)  # 12x18, SW corner
ADU = (5.0, 22.0, 29.0, 42.0)  # 20x24, 5' off alley / 3' off north line

# heights (ft) -- massing estimates, field-verify before design work
HOUSE_EAVE, HOUSE_RIDGE = 10.0, 20.0  # 1-story 1931, gable ridge E-W
SHED_EAVE, SHED_RIDGE = 7.5, 10.8  # corrugated metal, ridge E-W
ADU_EAVE, ADU_RIDGE = 16.0, 20.0  # 2-story at the R-5 20' cap

SUN = (0.45, -0.5, 0.74)  # unit vector toward the sun (SE, high)
SHADOW_K = 0.7  # aesthetic shadow-length factor

# ---------------- palette ---------------------------------------------------
GRASS = "#7f9c5e"
GRASS_N = "#78905c"
GRAVEL = "#b3ab9c"
ASPHALT = "#85888b"
CONCRETE = "#cac6bb"
H_WALL = "#7e926b"
H_ROOF = "#6a5140"
H_TRIM = "#ece6d4"
H_DOOR = "#7a3b2e"
DECK_C = "#a87e52"
RAIL_C = "#96703f"
PORCH_F = "#b9b3a4"
S_WALL = "#c3c7cb"
S_ROOF = "#b7bcc1"
S_DOOR = "#a5453a"
A_WALL = "#75834f"
A_ROOF = "#4c4a45"
A_TRIM = "#ebe4cf"
A_GDOOR = "#e9e2cc"
A_DOOR = "#a5453a"
A_WTRIM = "#8f3b32"
GLASS = "#b7c9d3"
NBR_W = "#b9b4a8"
NBR_R = "#8f8a80"

faces = []  # {c,g,p,[a],[layer]}
lines = []  # {c,g,p,[dash]}
labels = []  # {t,g,p,[s]}


def F(pts, c, g, layer="solid", a=None, parent=None):
    f = {"c": c, "g": g, "p": [[round(v, 2) for v in p] for p in pts]}
    if layer != "solid":
        f["l"] = layer
    if a is not None:
        f["a"] = a
    if parent is not None:
        # inset quad (door/window) drawn right after its host wall face,
        # sidestepping painter's-algorithm ties on coplanar geometry
        faces[parent].setdefault("ch", []).append(f)
        return parent
    faces.append(f)
    return len(faces) - 1


def box(x0, y0, x1, y1, z0, z1, c, g, skip=("bottom",), top=None):
    if "bottom" not in skip:
        F([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], c, g)
    if "top" not in skip:
        F([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top or c, g)
    if "s" not in skip:
        F([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], c, g)
    if "n" not in skip:
        F([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], c, g)
    if "w" not in skip:
        F([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], c, g)
    if "e" not in skip:
        F([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], c, g)


def gable(x0, x1, y0, y1, ze, zr, cw, cr, g, oe=1.2, og=0.8):
    """Gabled volume, ridge running E-W (along X). Returns wall face ids."""
    ym = (y0 + y1) / 2
    ids = {}
    ids["s"] = F([(x0, y0, 0), (x1, y0, 0), (x1, y0, ze), (x0, y0, ze)], cw, g)
    ids["n"] = F([(x1, y1, 0), (x0, y1, 0), (x0, y1, ze), (x1, y1, ze)], cw, g)
    ids["w"] = F([(x0, y1, 0), (x0, y0, 0), (x0, y0, ze), (x0, ym, zr), (x0, y1, ze)], cw, g)
    ids["e"] = F([(x1, y0, 0), (x1, y1, 0), (x1, y1, ze), (x1, ym, zr), (x1, y0, ze)], cw, g)
    slope = (zr - ze) / (ym - y0)
    zeo = ze - slope * oe
    # roof slopes, split into strips along the ridge for cleaner depth sorting
    ns = 4
    for i in range(ns):
        a = x0 - og + (x1 - x0 + 2 * og) * i / ns
        b = x0 - og + (x1 - x0 + 2 * og) * (i + 1) / ns
        F([(a, y0 - oe, zeo), (b, y0 - oe, zeo), (b, ym, zr), (a, ym, zr)], cr, g)  # S
        F([(b, y1 + oe, zeo), (a, y1 + oe, zeo), (a, ym, zr), (b, ym, zr)], cr, g)  # N
    return ids


def wquad(plane, k, d, u0, u1, z0, z1, off, c, g, parent):
    """Vertical quad on wall plane ('x' const or 'y' const), pushed out by off."""
    if plane == "x":
        x = k + off * d
        F([(x, u0, z0), (x, u1, z0), (x, u1, z1), (x, u0, z1)], c, g, parent=parent)
    else:
        y = k + off * d
        F([(u0, y, z0), (u1, y, z0), (u1, y, z1), (u0, y, z1)], c, g, parent=parent)


def window(plane, k, d, u0, u1, z0, z1, g, parent, trim=H_TRIM, glass=GLASS):
    wquad(plane, k, d, u0 - 0.18, u1 + 0.18, z0 - 0.18, z1 + 0.18, 0.05, trim, g, parent)
    wquad(plane, k, d, u0, u1, z0, z1, 0.09, glass, g, parent)


def hull(pts):
    pts = sorted(set(pts))

    def half(seq):
        h = []
        for p in seq:
            while (
                len(h) >= 2
                and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1])
                - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])
                <= 0
            ):
                h.pop()
            h.append(p)
        return h[:-1]

    return half(pts) + half(pts[::-1])


def shadow(x0, y0, x1, y1, h, g):
    dx, dy = -SUN[0] / SUN[2] * h * SHADOW_K, -SUN[1] / SUN[2] * h * SHADOW_K
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = corners + [(x + dx, y + dy) for x, y in corners]
    F([(x, y, 0.035) for x, y in hull(pts)], "#1c2616", g, layer="decal", a=0.16)


# ---------------- ground ----------------------------------------------------
F(
    [(-30, -30, -0.02), (178, -30, -0.02), (178, 75, -0.02), (-30, 75, -0.02)],
    GRASS_N,
    "site",
    layer="ground",
)  # context
F(
    [(0, 0, 0), (LOT_L, 0, 0), (LOT_L, LOT_W, 0), (0, LOT_W, 0)], GRASS, "site", layer="ground"
)  # lot
F(
    [(-14, -30, 0.01), (0, -30, 0.01), (0, 75, 0.01), (-14, 75, 0.01)],
    GRAVEL,
    "site",
    layer="ground",
)  # alley
F(
    [(148, -30, 0.01), (152.5, -30, 0.01), (152.5, 75, 0.01), (148, 75, 0.01)],
    CONCRETE,
    "site",
    layer="ground",
)  # sidewalk
F(
    [(157, -30, 0.01), (178, -30, 0.01), (178, 75, 0.01), (157, 75, 0.01)],
    ASPHALT,
    "site",
    layer="ground",
)  # street

# lot boundary + R-5 setback reference lines
lines.append(
    {
        "c": "#2c2c2c",
        "g": "site",
        "p": [[0, 0, 0.06], [148, 0, 0.06], [148, 45, 0.06], [0, 45, 0.06], [0, 0, 0.06]],
    }
)
for seg in ([(0, 5), (148, 5)], [(0, 40), (148, 40)], [(5, 0), (5, 45)], [(123, 0), (123, 45)]):
    lines.append(
        {
            "c": "#c0392b",
            "g": "setback",
            "dash": 1,
            "p": [[seg[0][0], seg[0][1], 0.06], [seg[1][0], seg[1][1], 0.06]],
        }
    )

# ---------------- existing house (1931, green siding, gable E-W) ------------
g = "house"
hf = gable(HW, EW, HS, HN, HOUSE_EAVE, HOUSE_RIDGE, H_WALL, H_ROOF, g)
shadow(HW, HS, EW, HN, 13, g)
# windows / doors
for x0 in (80, 90, 101, 111):
    window("y", HS, -1, x0, x0 + 4, 3.5, 7.5, g, hf["s"])  # south wall
for x0 in (82, 95, 108):
    window("y", HN, 1, x0, x0 + 4, 3.5, 7.5, g, hf["n"])  # north wall
for y0 in (11, 17):
    window("x", EW, 1, y0, y0 + 3.5, 3.5, 7.5, g, hf["e"])  # street wall
wquad("x", EW, 1, 28, 31.4, 1, 8, 0.07, H_DOOR, g, hf["e"])  # front door
wquad("x", HW, -1, 14, 17, 1.6, 8, 0.07, H_DOOR, g, hf["w"])  # deck door
window("x", HW, -1, 19, 22, 3.5, 7.5, g, hf["w"])
# front porch (NE): slab, posts, low shed roof
px0, py0, px1, py1 = PORCH
box(px0, py0, px1 + 0.5, py1, 0, 1.0, PORCH_F, g)
for py in (py0 + 0.6, py1 - 1.0):
    box(px1 + 0.1, py, px1 + 0.5, py + 0.4, 1.0, 8.9, H_TRIM, g)
F(
    [
        (px0 - 0.2, py0 - 0.4, 9.4),
        (px1 + 1.2, py0 - 0.4, 8.5),
        (px1 + 1.2, py1 + 0.4, 8.5),
        (px0 - 0.2, py1 + 0.4, 9.4),
    ],
    H_ROOF,
    g,
)
# deck (SW) with railing
dx0, dy0, dx1, dy1 = DECK
box(dx0, dy0, dx1, dy1, 0, 1.6, DECK_C, g)
shadow(dx0, dy0, dx1, dy1, 2.5, g)
box(dx0 - 0.25, dy0, dx0, dy1, 1.6, 4.4, RAIL_C, g)  # west rail
box(dx0 - 0.25, dy0 - 0.25, dx1, dy0, 1.6, 4.4, RAIL_C, g)  # south rail
box(dx0 - 0.25, dy1, dx1, dy1 + 0.25, 1.6, 4.4, RAIL_C, g)  # north rail

# ---------------- existing shed (12x18 corrugated metal) --------------------
g = "shed"
sx0, sy0, sx1, sy1 = SHED
sf = gable(sx0, sx1, sy0, sy1, SHED_EAVE, SHED_RIDGE, S_WALL, S_ROOF, g, oe=0.7, og=0.5)
shadow(sx0, sy0, sx1, sy1, 9, g)
wquad("x", sx1, 1, 8.8, 15.2, 0, 6.9, 0.07, S_DOOR, g, sf["e"])  # red slider, east end
window("x", sx1, 1, 15.6, 17.2, 3.2, 4.8, g, sf["e"], trim=S_WALL)

# ---------------- proposed ADU (20x24, garage below / 1-bed above) ----------
g = "adu"
ax0, ay0, ax1, ay1 = ADU
af = gable(ax0, ax1, ay0, ay1, ADU_EAVE, ADU_RIDGE, A_WALL, A_ROOF, g)
shadow(ax0, ay0, ax1, ay1, 18, g)
# west (alley) face: garage door + entry + upper windows
wquad("x", ax0, -1, 26.5, 37.5, 0, 8, 0.07, A_GDOOR, g, af["w"])  # garage door
wquad("x", ax0, -1, 27.2, 36.8, 6.7, 7.6, 0.11, GLASS, g, af["w"])  # door lites
wquad("x", ax0, -1, 22.9, 25.9, -0.1, 7.2, 0.05, A_TRIM, g, af["w"])
wquad("x", ax0, -1, 23.2, 25.6, 0, 7, 0.09, A_DOOR, g, af["w"])  # entry door
window("x", ax0, -1, 26.5, 30, 11.5, 15, g, af["w"], trim=A_WTRIM)
window("x", ax0, -1, 34, 37.5, 11.5, 15, g, af["w"], trim=A_WTRIM)
# east (yard) face
wquad("x", ax1, 1, 30, 33, 0, 7, 0.07, A_DOOR, g, af["e"])  # yard door
window("x", ax1, 1, 24.5, 28, 11, 14.5, g, af["e"], trim=A_WTRIM)
window("x", ax1, 1, 35, 38.5, 11, 14.5, g, af["e"], trim=A_WTRIM)
window("x", ax1, 1, 34.5, 38.5, 3, 6.5, g, af["e"], trim=A_WTRIM)  # office window
# south / north faces
for x0 in (9, 17):
    window("y", ay0, -1, x0, x0 + 4, 11, 14.5, g, af["s"], trim=A_WTRIM)
window("y", ay0, -1, 20, 23, 4, 6.5, g, af["s"], trim=A_WTRIM)
window("y", ay1, 1, 12, 16, 11, 14.5, g, af["n"], trim=A_WTRIM)

# ---------------- neighbor massing (approx, from oblique satellite) ---------
g = "context"
gable(96, 126, 53, 74, 17, 26, NBR_W, NBR_R, g)  # 108 (2-story, N)
shadow(96, 53, 126, 74, 20, g)
gable(98, 126, -24, -4, 11, 19, NBR_W, NBR_R, g)  # 114 (S)
shadow(98, -24, 126, -4, 14, g)
box(5, 56, 21, 68, 0, 8.5, "#d8d5cd", g, top="#c4c1b8")  # N-neighbor shed
shadow(5, 56, 21, 68, 8, g)

# ---------------- labels -----------------------------------------------------
labels += [
    {"t": "EXISTING HOUSE · 1931", "g": "labels", "p": [99, 22.5, 24]},
    {"t": "SHED 12×18", "g": "labels", "p": [17, 12, 12.6]},
    {"t": "PROPOSED ADU 20×24", "g": "labels", "p": [17, 32, 24]},
    {"t": "DECK", "g": "labels", "p": [70.5, 16.5, 8], "s": 1},
    {"t": "PORCH", "g": "labels", "p": [124.5, 30, 12.5], "s": 1},
    {"t": "ALLEY", "g": "site", "p": [-7, 22.5, 1.5], "s": 1},
    {"t": "W 29TH ST", "g": "site", "p": [166, 22.5, 1.5], "s": 1},
]

SCENE = {
    "faces": faces,
    "lines": lines,
    "labels": labels,
    "sun": SUN,
    "meta": {"title": "112 W 29th St · lot + ADU 3D model", "date": DATE},
}


# ============================ OBJ / MTL export ===============================
# OBJ is Y-up: (E, N, U) -> (x=E, y=U, z=-N). 1 unit = 1 foot.
def flat(fs):
    for f in fs:
        if f.get("l") == "decal":
            continue
        yield f
        for ch in f.get("ch", ()):
            yield ch


mtl_of, mtls = {}, []
for f in flat(faces):
    c = f["c"]
    if c not in mtl_of:
        mtl_of[c] = "m%d" % len(mtl_of)
        mtls.append(c)

obj = [
    "# 112 W 29th St, Richmond VA -- lot massing model (house / shed / proposed ADU)",
    "# units: feet, Y-up. Generated %s by model/generate_3d_model.py" % DATE,
    "# PRELIMINARY - massing only, heights estimated, field-verify",
    "mtllib site-model.mtl",
]
vi = 1
cur_g, cur_m = None, None
GROUP_NAMES = {
    "site": "Site_Ground",
    "house": "Existing_House",
    "shed": "Existing_Shed",
    "adu": "Proposed_ADU",
    "context": "Neighbors_Approx",
}
for f in flat(faces):
    gname = GROUP_NAMES.get(f["g"], f["g"])
    if gname != cur_g:
        obj.append("g " + gname)
        cur_g = gname
    m = mtl_of[f["c"]]
    if m != cur_m:
        obj.append("usemtl " + m)
        cur_m = m
    idx = []
    for x, y, z in f["p"]:
        obj.append("v %.2f %.2f %.2f" % (x, z, -y))
        idx.append(str(vi))
        vi += 1
    obj.append("f " + " ".join(idx))

with open(os.path.join(OUT_DIR, "site-model.obj"), "w") as fh:
    fh.write("\n".join(obj) + "\n")

mtl_out = ["# materials for site-model.obj"]
for c in mtls:
    r, gg, b = (int(c[i : i + 2], 16) / 255 for i in (1, 3, 5))
    mtl_out += ["newmtl " + mtl_of[c], "Kd %.3f %.3f %.3f" % (r, gg, b), ""]
with open(os.path.join(OUT_DIR, "site-model.mtl"), "w") as fh:
    fh.write("\n".join(mtl_out))
print(
    "wrote model/site-model.obj (+.mtl): %d faces, %d materials"
    % (sum(1 for _ in flat(faces)), len(mtls))
)

# ============================ interactive HTML viewer ========================
BODY = r"""
<title>112 W 29th St - lot + ADU 3D</title>
<style>
  :root { --panel:#ffffffe6; --ink:#20241c; --mut:#5c6152; --edge:#00000022; }
  @media (prefers-color-scheme: dark) {
    :root { --panel:#20241ce6; --ink:#e8e6dc; --mut:#a9ad9e; --edge:#ffffff26; }
  }
  :root[data-theme="dark"] { --panel:#20241ce6; --ink:#e8e6dc; --mut:#a9ad9e; --edge:#ffffff26; }
  :root[data-theme="light"] { --panel:#ffffffe6; --ink:#20241c; --mut:#5c6152; --edge:#00000022; }
  html, body { height:100%; margin:0; overflow:hidden; }
  body { font:14px/1.45 system-ui, sans-serif; }
  #cv { position:fixed; inset:0; width:100%; height:100%; touch-action:none; cursor:grab; }
  .card { position:fixed; background:var(--panel); color:var(--ink); border:1px solid var(--edge);
          border-radius:12px; padding:10px 14px; backdrop-filter:blur(6px); max-width:min(320px, calc(100vw - 32px)); }
  #ui { top:12px; left:12px; }
  #ui h1 { font-size:15px; margin:0 0 2px; }
  #ui .sub { color:var(--mut); font-size:12px; margin-bottom:8px; }
  #ui label { display:flex; gap:7px; align-items:center; font-size:13px; padding:1.5px 0; cursor:pointer; }
  #ui .views { display:flex; flex-wrap:wrap; gap:5px; margin-top:8px; }
  #ui .views button { font:12px system-ui; padding:4px 9px; border-radius:8px; border:1px solid var(--edge);
                      background:transparent; color:var(--ink); cursor:pointer; }
  #ui .views button:hover { background:var(--edge); }
  #ui .hint { color:var(--mut); font-size:11.5px; margin-top:8px; }
  #dims { right:12px; bottom:12px; font-size:12px; color:var(--mut); max-width:min(330px, calc(100vw - 32px)); }
  #dims b { color:var(--ink); }
  #compass { position:fixed; left:16px; bottom:14px; width:54px; height:54px; pointer-events:none; }
  details > summary { cursor:pointer; font-size:12.5px; color:var(--mut); list-style:none; margin-top:6px; }
  @media (max-width:700px){ #dims{display:none;} }
</style>
<canvas id="cv"></canvas>
<div class="card" id="ui">
  <h1>112 W 29th St &mdash; lot 3D</h1>
  <div class="sub">45&times;148 lot &middot; house + shed + proposed ADU</div>
  <label><input type="checkbox" data-g="adu" checked> Proposed ADU (20&times;24, 2-story)</label>
  <label><input type="checkbox" data-g="house" checked> Existing house (1931)</label>
  <label><input type="checkbox" data-g="shed" checked> Existing shed (12&times;18)</label>
  <label><input type="checkbox" data-g="context" checked> Neighbors (approx.)</label>
  <label><input type="checkbox" data-g="setback" checked> R-5 setback lines</label>
  <label><input type="checkbox" data-g="labels" checked> Labels</label>
  <div class="views">
    <button data-v="bird">Bird&rsquo;s eye</button><button data-v="alley">Alley</button>
    <button data-v="yard">Backyard</button><button data-v="street">Street</button>
    <button data-v="top">Top</button>
  </div>
  <div class="hint">drag &middot; orbit &nbsp; | &nbsp; scroll/pinch &middot; zoom &nbsp; | &nbsp; right-drag / shift &middot; pan</div>
</div>
<div class="card" id="dims">
  <b>Lot</b> 45&prime;&times;148&prime; (6,660 sf) &middot; zone R-5 &middot; alley W / street E<br>
  <b>House</b> 1,303 sf 1-story (1931) &middot; front setback 25&prime; measured<br>
  <b>ADU</b> 20&times;24 &middot; &le;20&prime; &middot; garage + ~480 sf 1-bed &middot; 5&prime; off alley,
  3&prime; off N line (<b>variance req&rsquo;d</b>, R-5 min 5&prime;)<br>
  <i>Preliminary massing &mdash; heights estimated, field-verify.</i>
</div>
<canvas id="compass" width="108" height="108"></canvas>
<script>
"use strict";
const SC = __SCENE__;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const cps = document.getElementById('compass'), cpx = cps.getContext('2d');
const vis = {site:1, house:1, shed:1, adu:1, context:1, setback:1, labels:1};
const L = SC.sun;

// precompute world normals + layer buckets
function prep(f){
  const [a,b,c] = f.p, u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]], v=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
  let n=[u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
  const m=Math.hypot(...n)||1; f.n=[n[0]/m,n[1]/m,n[2]/m];
  f.rgb=[1,3,5].map(i=>parseInt(f.c.slice(i,i+2),16));
  (f.ch||[]).forEach(prep);
}
SC.faces.forEach(prep);
const BUCKET = {ground:[], decal:[], solid:[]};
for (const f of SC.faces) BUCKET[f.l||'solid'].push(f);

// camera
const cam = {az:215, el:35, d:190, t:[70,22,2]};
const VIEWS = {
  bird:{az:215, el:35, d:190, t:[70,22,2]},
  alley:{az:181, el:11, d:95, t:[22,31,9]},
  yard:{az:-17, el:9, d:45, t:[17,30,9]},
  street:{az:-4, el:13, d:120, t:[115,22,9]},
  top:{az:-90, el:88, d:215, t:[74,22,0]},
};
let anim=null, dirty=true;
const hv=VIEWS[(location.hash||'').slice(1)];
if(hv) Object.assign(cam, {az:hv.az, el:hv.el, d:hv.d, t:[...hv.t]});

function basis(){
  const az=cam.az*Math.PI/180, el=cam.el*Math.PI/180;
  const pos=[cam.t[0]+cam.d*Math.cos(el)*Math.cos(az),
             cam.t[1]+cam.d*Math.cos(el)*Math.sin(az),
             cam.t[2]+cam.d*Math.sin(el)];
  let f=[cam.t[0]-pos[0],cam.t[1]-pos[1],cam.t[2]-pos[2]];
  const fm=Math.hypot(...f); f=f.map(v=>v/fm);
  let r=[f[1]*1-f[2]*0, f[2]*0-f[0]*1, 0]; // cross(f, up=[0,0,1])
  const rm=Math.hypot(...r)||1; r=r.map(v=>v/rm);
  const u=[r[1]*f[2]-r[2]*f[1], r[2]*f[0]-r[0]*f[2], r[0]*f[1]-r[1]*f[0]];
  return {pos,f,r,u};
}
const NEAR=0.6;
function clipZ(pts){ // Sutherland-Hodgman against z>NEAR (camera space)
  const out=[];
  for(let i=0;i<pts.length;i++){
    const a=pts[i], b=pts[(i+1)%pts.length], ain=a[2]>NEAR, bin=b[2]>NEAR;
    if(ain) out.push(a);
    if(ain!==bin){ const t=(NEAR-a[2])/(b[2]-a[2]);
      out.push([a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1]), NEAR]); }
  }
  return out;
}
let W,H,DPR,FL;
function resize(){
  DPR=Math.min(devicePixelRatio||1,2); W=innerWidth; H=innerHeight;
  cv.width=W*DPR; cv.height=H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0);
  FL=H/(2*Math.tan(28*Math.PI/180)); dirty=true;
}
addEventListener('resize',resize); resize();

function render(){
  const B=basis();
  // sky
  const sky=ctx.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,'#b9cbd8'); sky.addColorStop(0.62,'#dde4e0'); sky.addColorStop(1,'#c8cdbd');
  ctx.fillStyle=sky; ctx.fillRect(0,0,W,H);
  const toCam=p=>{const w=[p[0]-B.pos[0],p[1]-B.pos[1],p[2]-B.pos[2]];
    return [w[0]*B.r[0]+w[1]*B.r[1]+w[2]*B.r[2],
            w[0]*B.u[0]+w[1]*B.u[1]+w[2]*B.u[2],
            w[0]*B.f[0]+w[1]*B.f[1]+w[2]*B.f[2]];};
  const px=c=>[W/2+FL*c[0]/c[2], H/2-FL*c[1]/c[2]];
  function drawFaces(list){
    const items=[];
    for(const f of list){
      if(!vis[f.g]) continue;
      const cs=clipZ(f.p.map(toCam));
      if(cs.length<3) continue;
      let zs=0; for(const c of cs) zs+=c[2];
      items.push({f, cs, z:zs/cs.length});
    }
    items.sort((a,b)=>b.z-a.z);
    const F2=[-0.62, 0.3, 0.35];                 // soft westerly fill light
    function paint(f, cs){
      let sh=1;
      if(f.a===undefined){
        const d=Math.max(0, f.n[0]*L[0]+f.n[1]*L[1]+f.n[2]*L[2]);
        const d2=Math.max(0, f.n[0]*F2[0]+f.n[1]*F2[1]+f.n[2]*F2[2]);
        sh=Math.min(1, 0.55+0.42*d+0.16*d2);
      }
      const [r,g,b]=f.rgb;
      ctx.fillStyle=`rgb(${r*sh|0},${g*sh|0},${b*sh|0})`;
      ctx.globalAlpha=f.a===undefined?1:f.a;
      ctx.beginPath();
      cs.forEach((c,i)=>{const s=px(c); i?ctx.lineTo(s[0],s[1]):ctx.moveTo(s[0],s[1]);});
      ctx.closePath(); ctx.fill();
      if(f.a===undefined){ ctx.strokeStyle=ctx.fillStyle; ctx.lineWidth=0.75; ctx.stroke(); }
      ctx.globalAlpha=1;
    }
    for(const it of items){
      paint(it.f, it.cs);
      for(const ch of it.f.ch||[]){
        const cs=clipZ(ch.p.map(toCam));
        if(cs.length>2) paint(ch, cs);
      }
    }
  }
  drawFaces(BUCKET.ground);
  drawFaces(BUCKET.decal);
  // lines
  for(const ln of SC.lines){
    if(!vis[ln.g]) continue;
    ctx.strokeStyle=ln.c; ctx.lineWidth=1.4;
    ctx.setLineDash(ln.dash?[7,5]:[]);
    ctx.beginPath();
    let started=false;
    for(let i=0;i<ln.p.length-1;i++){
      let a=toCam(ln.p[i]), b=toCam(ln.p[i+1]);
      if(a[2]<=NEAR&&b[2]<=NEAR) continue;
      if(a[2]<=NEAR){const t=(NEAR-a[2])/(b[2]-a[2]);a=[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),NEAR];}
      if(b[2]<=NEAR){const t=(NEAR-b[2])/(a[2]-b[2]);b=[b[0]+t*(a[0]-b[0]),b[1]+t*(a[1]-b[1]),NEAR];}
      const sa=px(a),sb=px(b);
      ctx.moveTo(sa[0],sa[1]); ctx.lineTo(sb[0],sb[1]); started=true;
    }
    if(started) ctx.stroke();
    ctx.setLineDash([]);
  }
  drawFaces(BUCKET.solid);
  // labels
  ctx.textAlign='center'; ctx.textBaseline='middle';
  for(const lb of SC.labels){
    if(!vis[lb.g]||!vis.labels&&lb.g==='labels') continue;
    if(lb.g!=='labels'&&!vis.labels) continue;
    const c=toCam(lb.p); if(c[2]<=NEAR) continue;
    const s=px(c), fs=lb.s?11:12.5;
    ctx.font=(lb.s?'':'600 ')+fs+'px system-ui';
    const w=ctx.measureText(lb.t).width+14;
    ctx.fillStyle='rgba(28,32,24,0.78)';
    ctx.beginPath(); ctx.roundRect(s[0]-w/2, s[1]-11, w, 22, 11); ctx.fill();
    ctx.fillStyle='#f2efe4'; ctx.fillText(lb.t, s[0], s[1]+0.5);
  }
  // compass (screen direction of world north)
  const nx=B.r[1], ny=-B.u[1];
  cpx.setTransform(2,0,0,2,0,0); cpx.clearRect(0,0,54,54);
  cpx.save(); cpx.translate(27,27); cpx.rotate(Math.atan2(ny,nx)+Math.PI/2);
  cpx.fillStyle='rgba(28,32,24,0.72)'; cpx.beginPath(); cpx.arc(0,0,24,0,7); cpx.fill();
  cpx.fillStyle='#e8604c'; cpx.beginPath();
  cpx.moveTo(0,-17); cpx.lineTo(6,4); cpx.lineTo(0,0); cpx.lineTo(-6,4); cpx.closePath(); cpx.fill();
  cpx.fillStyle='#f2efe4'; cpx.font='700 10px system-ui';
  cpx.textAlign='center'; cpx.textBaseline='middle'; cpx.fillText('N',0,12);
  cpx.restore();
}

function tick(){
  if(anim){
    const t=Math.min(1,(performance.now()-anim.t0)/500), e=t*(2-t);
    for(const k of ['az','el','d']) cam[k]=anim.a[k]+(anim.b[k]-anim.a[k])*e;
    cam.t=anim.a.t.map((v,i)=>v+(anim.b.t[i]-v)*e);
    if(t>=1) anim=null;
    dirty=true;
  }
  if(dirty){ render(); dirty=false; }
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

// -------- interaction --------
const ptrs=new Map(); let lastPinch=0;
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);
  ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY,b:e.button,sh:e.shiftKey}); anim=null;});
cv.addEventListener('pointermove',e=>{
  const p=ptrs.get(e.pointerId); if(!p) return;
  const dx=e.clientX-p.x, dy=e.clientY-p.y;
  if(ptrs.size===2){
    const arr=[...ptrs.values()]; p.x=e.clientX; p.y=e.clientY;
    const [a,b]=[...ptrs.values()];
    const dist=Math.hypot(a.x-b.x,a.y-b.y);
    if(lastPinch){ cam.d*=lastPinch/dist; cam.d=Math.max(15,Math.min(600,cam.d)); }
    lastPinch=dist; dirty=true; return;
  }
  p.x=e.clientX; p.y=e.clientY;
  if(p.b===2||p.sh){ // pan
    const B=basis(), s=cam.d/FL;
    cam.t[0]-=(dx*B.r[0]-dy*B.u[0])*s; cam.t[1]-=(dx*B.r[1]-dy*B.u[1])*s;
    cam.t[2]-=(-dy*B.u[2])*s; cam.t[2]=Math.max(0,Math.min(40,cam.t[2]));
  } else {
    cam.az-=dx*0.35; cam.el=Math.max(3,Math.min(89,cam.el+dy*0.3));
  }
  dirty=true;
});
const clear=e=>{ptrs.delete(e.pointerId); if(ptrs.size<2) lastPinch=0;};
cv.addEventListener('pointerup',clear); cv.addEventListener('pointercancel',clear);
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();
  cam.d*=Math.exp(e.deltaY*0.0011); cam.d=Math.max(15,Math.min(600,cam.d)); dirty=true;},{passive:false});
document.querySelectorAll('#ui input').forEach(cb=>cb.addEventListener('change',()=>{
  vis[cb.dataset.g]=cb.checked?1:0; dirty=true;}));
document.querySelectorAll('#ui .views button').forEach(bt=>bt.addEventListener('click',()=>{
  const v=VIEWS[bt.dataset.v];
  anim={t0:performance.now(), a:{az:cam.az,el:cam.el,d:cam.d,t:[...cam.t]},
        b:{az:v.az,el:v.el,d:v.d,t:[...v.t]}};
}));
</script>
"""

html_body = BODY.replace("__SCENE__", json.dumps(SCENE, separators=(",", ":")))
page = (
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "</head>\n<body>" + html_body + "</body>\n</html>\n"
)
with open(os.path.join(OUT_DIR, "site-model-3d.html"), "w") as fh:
    fh.write(page)
print("wrote model/site-model-3d.html")
