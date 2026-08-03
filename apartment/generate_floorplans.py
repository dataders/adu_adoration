"""Generate iteration-ready floor plans for the 1-bed apartment above the ADU garage.

Building envelope (from plan/generate_site_plan.py): 24 ft east-west x 20 ft
north-south, two stories, garage below / apartment above. Drawn north-up to
match the site plan: alley = left (west), yard & main house = right (east),
property line 5 ft off the top (north) edge. The selected replacement shed is
9 ft south of the building shell and 5 ft clear of the exterior stair.

Coordinate system: 1 unit = 1 foot, origin at the SW *exterior* corner of the
building, X = east, Y = north. Exterior walls 6" nominal -> interior clear
23'-0" x 19'-0" = 437 sf net (480 sf gross).

Six schemes compare interior/exterior access and room placement:
  A - interior stair on the blank north wall, LIVING toward the yard (east)
  B - same core, BEDROOM toward the yard (east), kitchen on the west wall
  C - EXTERIOR stair on the east face: no stair inside, biggest apartment
  D - EXTERIOR stair from the alley along the south face; roof-aware layout
  E - PRIMARY DESIGN BASIS from the owner's sketch; two-level program,
      south alley stair, and roof-aware kitchen
  F - RECOMMENDED DEVELOPMENT: full-depth garage, stacked wet core,
      connected landing/east patios, large sliders, corrected glazing

Run:  uv run python3 apartment/generate_floorplans.py
PNGs are rendered with headless chromium if available (rsvg-convert as
fallback). Iterate by editing the option_* functions and re-running.
"""

import os
import shutil
import subprocess

S = 26.0  # px per foot
BW, BH = 24.0, 20.0  # building exterior, ft
EXT = 0.5  # exterior wall thickness, ft
INT = 0.33  # interior wall thickness, ft

FLOOR = "#fdfdfb"
WALL = "#37393d"
FURN_STROKE = "#8d939c"
FURN_FILL = "#f1f2f4"
DIMC = "#7a8290"
NOTEC = "#5c636e"

TINT = {
    "bed": "#eaf1fa",
    "bath": "#e7f6ef",
    "kitchen": "#fdf3e3",
    "living": "#fbeeec",
    "hall": "#f3f0fa",
    "stair": "#eeeeee",
    "garage": "#f2f2ef",
    "mech": "#e9e7f5",
    "flex": "#fdf3e3",
}


class Plan:
    """One floor plan placed at pixel offset (ox, oy) on the sheet."""

    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy
        self.under, self.mid, self.over = [], [], []  # tints/walls/symbols

    def X(self, x):
        return self.ox + x * S

    def Y(self, y):
        return self.oy + (BH - y) * S

    # ---- primitives (x, y = lower-left in feet) ----
    def rect(
        self, x, y, w, h, fill, stroke="none", sw=1.0, rx=0, dash=None, layer=None, opacity=1.0
    ):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        (layer if layer is not None else self.mid).append(
            f'<rect x="{self.X(x):.1f}" y="{self.Y(y + h):.1f}" '
            f'width="{w * S:.1f}" height="{h * S:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} '
            f'opacity="{opacity}"/>'
        )

    def line(self, x1, y1, x2, y2, stroke=FURN_STROKE, sw=1.2, dash=None, layer=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        (layer if layer is not None else self.over).append(
            f'<line x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" '
            f'x2="{self.X(x2):.1f}" y2="{self.Y(y2):.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d} '
            f'stroke-linecap="round"/>'
        )

    def text(self, x, y, s, size=12, weight="normal", fill="#3a3f46", anchor="middle", rotate=None):
        px, py = self.X(x), self.Y(y)
        r = f' transform="rotate({rotate} {px:.1f} {py:.1f})"' if rotate else ""
        self.over.append(
            f'<text x="{px:.1f}" y="{py:.1f}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'font-family="Helvetica,Arial,sans-serif"{r}>{s}</text>'
        )

    def label(self, x, y, name, sub=None, size=13):
        self.text(x, y, name, size=size, weight="bold")
        if sub:
            self.text(x, y - 0.55, sub, size=9.5, fill="#818893")

    # ---- building shell ----
    def shell(self):
        self.rect(0, 0, BW, BH, WALL, layer=self.mid)
        self.rect(EXT, EXT, BW - 2 * EXT, BH - 2 * EXT, FLOOR, layer=self.mid)

    def tint(self, x, y, w, h, kind):
        self.under.append("")  # keep list non-empty ordering stable
        self.rect(x, y, w, h, TINT[kind], layer=self.under)

    def wall(self, x, y, w, h):
        """Interior wall as a rect (give it INT thickness on one axis)."""
        self.rect(x, y, w, h, WALL, layer=self.mid)

    # ---- openings: cut a white gap in the wall, then draw the symbol ----
    def _cut(self, x, y, w, h):
        self.rect(x, y, w, h, FLOOR, layer=self.over)

    def door(self, x, y, width, wall="h", t=INT, hinge="left", swing=1):
        """Swing door. (x,y)=lower-left of the wall opening. wall='h'|'v'.
        hinge: which end holds the hinge. swing: +1 opens toward +axis."""
        if wall == "h":
            self._cut(x, y, width, t)
            hx = x if hinge == "left" else x + width
            leaf_x = hx
            leaf_y2 = (y + t / 2) + swing * width
            self.line(leaf_x, y + t / 2, leaf_x, leaf_y2, stroke="#4a4e55", sw=1.6)
            ox = x + width if hinge == "left" else x
            self.over.append(self._arc(leaf_x, y + t / 2, ox, y + t / 2, leaf_x, leaf_y2))
        else:
            self._cut(x, y, t, width)
            hy = y if hinge == "left" else y + width
            leaf_x2 = (x + t / 2) + swing * width
            self.line(x + t / 2, hy, leaf_x2, hy, stroke="#4a4e55", sw=1.6)
            oy = y + width if hinge == "left" else y
            self.over.append(self._arc(x + t / 2, hy, x + t / 2, oy, leaf_x2, hy))

    def _arc(self, hx, hy, ax, ay, bx, by):
        r = ((ax - hx) ** 2 + (ay - hy) ** 2) ** 0.5 * S
        return (
            f'<path d="M {self.X(ax):.1f} {self.Y(ay):.1f} '
            f'A {r:.1f} {r:.1f} 0 0 0 {self.X(bx):.1f} {self.Y(by):.1f}" '
            f'fill="none" stroke="#b6bac1" stroke-width="1"/>'
        )

    def slider(self, x, y, width, wall="h", t=INT):
        """Sliding/bypass closet doors."""
        if wall == "h":
            self._cut(x, y, width, t)
            m = y + t / 2
            self.line(x, m + 0.07, x + width * 0.55, m + 0.07, stroke="#4a4e55", sw=1.6)
            self.line(x + width * 0.45, m - 0.07, x + width, m - 0.07, stroke="#4a4e55", sw=1.6)
        else:
            self._cut(x, y, t, width)
            m = x + t / 2
            self.line(m + 0.07, y, m + 0.07, y + width * 0.55, stroke="#4a4e55", sw=1.6)
            self.line(m - 0.07, y + width * 0.45, m - 0.07, y + width, stroke="#4a4e55", sw=1.6)

    def window(self, x, y, width, wall="h", t=EXT):
        if wall == "h":
            self._cut(x, y, width, t)
            for f in (0.25, 0.5, 0.75):
                self.line(x, y + t * f, x + width, y + t * f, stroke="#5b6f8d", sw=1.1)
        else:
            self._cut(x, y, t, width)
            for f in (0.25, 0.5, 0.75):
                self.line(x + t * f, y, x + t * f, y + width, stroke="#5b6f8d", sw=1.1)

    def opening(self, x, y, width, wall="h", t=INT):
        """Cased opening (no door)."""
        if wall == "h":
            self._cut(x, y, width, t)
        else:
            self._cut(x, y, t, width)

    # ---- stairs ----
    def stair(self, x, y, w, h, direction, updown, n=13):
        """Straight flight in rect (x,y,w,h); direction 'e'/'w' = which way
        you FACE walking in the updown direction."""
        self.rect(x, y, w, h, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=self.mid)
        step = w / n
        for i in range(1, n):
            self.line(x + i * step, y, x + i * step, y + h, stroke="#b3b8bf", sw=1)
        cy = y + h / 2
        if direction == "e":
            x1, x2 = x + 0.5, x + w - 0.7
        else:
            x1, x2 = x + w - 0.5, x + 0.7
        self.line(x1, cy, x2, cy, stroke="#6a7180", sw=1.3)
        ah = 0.35 if direction == "e" else -0.35
        self.line(x2, cy, x2 - ah, cy + 0.3, stroke="#6a7180", sw=1.3)
        self.line(x2, cy, x2 - ah, cy - 0.3, stroke="#6a7180", sw=1.3)
        self.text((x1 + x2) / 2, cy + 0.55, updown, size=9, fill="#6a7180")

    # ---- furniture ----
    def furn(self, x, y, w, h, name=None, rx=3, fill=FURN_FILL):
        self.rect(x, y, w, h, fill, stroke=FURN_STROKE, sw=1.1, rx=rx, layer=self.over)
        if name:
            self.text(x + w / 2, y + h / 2 - 0.18, name, size=8.5, fill="#7d838d")

    def bed_q(self, x, y, head="w"):
        """Queen 5'0 x 6'8. head side: w/e/n/s."""
        w, h = (6.67, 5.0) if head in "we" else (5.0, 6.67)
        self.furn(x, y, w, h, rx=4)
        if head == "w":
            self.rect(
                x + 0.25,
                y + 0.35,
                0.85,
                h - 0.7,
                "#fff",
                stroke=FURN_STROKE,
                sw=1,
                rx=3,
                layer=self.over,
            )
            self.line(x + 1.6, y, x + 1.6, y + h)
        elif head == "n":
            self.rect(
                x + 0.35,
                y + h - 1.1,
                w - 0.7,
                0.85,
                "#fff",
                stroke=FURN_STROKE,
                sw=1,
                rx=3,
                layer=self.over,
            )
            self.line(x, y + h - 1.6, x + w, y + h - 1.6)
        self.text(x + w / 2, y + h / 2 - 0.2, "queen", size=8.5, fill="#7d838d")

    def sofa(self, x, y, w, h, back="n"):
        self.furn(x, y, w, h, rx=5)
        if back == "n":
            self.line(x + 0.15, y + h - 0.55, x + w - 0.15, y + h - 0.55)
        elif back == "s":
            self.line(x + 0.15, y + 0.55, x + w - 0.15, y + 0.55)
        elif back == "w":
            self.line(x + 0.55, y + 0.15, x + 0.55, y + h - 0.15)
        else:
            self.line(x + w - 0.55, y + 0.15, x + w - 0.55, y + h - 0.15)
        self.text(x + w / 2, y + h / 2 - 0.2, "sofa", size=8.5, fill="#7d838d")

    def table(self, x, y, w, h, chairs=4):
        self.furn(x, y, w, h, rx=4)
        cw = 1.3
        if chairs >= 2:
            self.furn(x + w * 0.28 - cw / 2, y + h + 0.15, cw, cw, rx=4)
            self.furn(x + w * 0.72 - cw / 2, y - 0.15 - cw, cw, cw, rx=4)
        if chairs >= 4:
            self.furn(x + w * 0.72 - cw / 2, y + h + 0.15, cw, cw, rx=4)
            self.furn(x + w * 0.28 - cw / 2, y - 0.15 - cw, cw, cw, rx=4)

    def counter(self, x, y, w, h):
        self.rect(x, y, w, h, "#faf6ee", stroke=FURN_STROKE, sw=1.1, layer=self.over)

    def sink(self, x, y, w=1.7, h=1.3):
        self.rect(x, y, w, h, "#fff", stroke=FURN_STROKE, sw=1, rx=3, layer=self.over)
        self.text(x + w / 2, y + h / 2 - 0.18, "sink", size=7.5, fill="#8d939c")

    def range_(self, x, y, w=2.5, h=2.17):
        self.rect(x, y, w, h, "#fff", stroke=FURN_STROKE, sw=1, layer=self.over)
        for dx in (0.6, w - 0.6):
            for dy in (0.6, h - 0.6):
                self.over.append(
                    f'<circle cx="{self.X(x + dx):.1f}" '
                    f'cy="{self.Y(y + dy):.1f}" r="{0.32 * S:.1f}" '
                    f'fill="none" stroke="{FURN_STROKE}" stroke-width="1"/>'
                )

    def fridge(self, x, y, w=2.6, h=2.5):
        self.furn(x, y, w, h, "REF", rx=2, fill="#fff")

    def toilet(self, x, y, face="s"):
        if face == "s":
            self.rect(
                x, y + 1.35, 1.6, 0.75, "#fff", stroke=FURN_STROKE, sw=1, rx=2, layer=self.over
            )
            self.over.append(
                f'<ellipse cx="{self.X(x + 0.8):.1f}" '
                f'cy="{self.Y(y + 0.72):.1f}" rx="{0.62 * S:.1f}" '
                f'ry="{0.72 * S:.1f}" fill="#fff" stroke="{FURN_STROKE}" '
                f'stroke-width="1"/>'
            )

    def vanity(self, x, y, w=2.4, h=1.75):
        self.counter(x, y, w, h)
        self.over.append(
            f'<circle cx="{self.X(x + w / 2):.1f}" '
            f'cy="{self.Y(y + h / 2):.1f}" r="{0.5 * S:.1f}" fill="#fff" '
            f'stroke="{FURN_STROKE}" stroke-width="1"/>'
        )

    def shower(self, x, y, w=3.0, h=3.0):
        self.rect(x, y, w, h, "#fff", stroke=FURN_STROKE, sw=1.2, layer=self.over)
        self.line(x, y, x + w, y + h, sw=0.9)
        self.line(x, y + h, x + w, y, sw=0.9)
        self.text(x + w / 2, y + h / 2 - 0.2, "shower", size=7.5, fill="#6e747e")

    def wd(self, x, y):
        self.furn(x, y, 2.3, 2.3, rx=2, fill="#fff")
        self.text(x + 1.15, y + 1.15 - 0.18, "W/D", size=8, fill="#7d838d")

    def car(self, x, y):
        self.rect(x, y, 15.5, 6.2, "#fff", stroke="#b3b8bf", sw=1.3, rx=14, layer=self.over)
        self.text(x + 7.75, y + 3.1 - 0.2, "car (typ. 16' x 6')", size=9, fill="#9aa0a9")

    # ---- annotations around the plan ----
    def dims(self, yb=-1.3, xl=-1.3):
        self.line(0, yb, BW, yb, stroke=DIMC, sw=1)
        for xx in (0, BW):
            self.line(xx, yb - 0.3, xx, yb + 0.3, stroke=DIMC, sw=1)
        self.text(BW / 2, yb - 0.85, "24'-0\"", size=10.5, fill=DIMC)
        self.line(xl, 0, xl, BH, stroke=DIMC, sw=1)
        for yy in (0, BH):
            self.line(xl - 0.3, yy, xl + 0.3, yy, stroke=DIMC, sw=1)
        self.text(xl - 0.55, BH / 2, "20'-0\"", size=10.5, fill=DIMC, rotate=-90)

    def context(self, title, east_x=None, south_text=None, south_y=-2.9):
        self.text(BW / 2, BH + 1.75, title, size=13, weight="bold")
        self.text(
            BW / 2,
            BH + 0.65,
            "north &#8593; &#183; property line 5' &#8212; keep this wall (nearly) window-free",
            size=9,
            fill=NOTEC,
        )
        self.text(
            BW / 2,
            south_y,
            south_text or "south &#183; replacement shed 9' from building &#183; best all-day sun",
            size=9,
            fill=NOTEC,
        )
        self.text(
            -3.4,
            BH / 2,
            "west &#183; alley &#183; garage door below",
            size=9,
            fill=NOTEC,
            rotate=-90,
        )
        self.text(
            east_x if east_x else BW + 2.6,
            BH / 2,
            "east &#183; yard &amp; main house &#183; morning sun",
            size=9,
            fill=NOTEC,
            rotate=90,
        )

    def svg(self):
        return "".join(self.under) + "".join(self.mid) + "".join(self.over)


# --------------------------------------------------------------------------
# Shared pieces
# --------------------------------------------------------------------------


def core_bath(p):
    """NW bath + stacked laundry, x 0.5-6.9 / y 13.5-19.5. ~36 sf."""
    p.tint(0.5, 13.83, 6.4, 5.67, "bath")
    p.wall(0.5, 13.5, 6.73, INT)  # south wall of bath
    p.wall(6.9, 13.5, INT, 6.0)  # east wall of bath
    p.door(6.9, 14.4, 2.4, wall="v", hinge="left", swing=-1)
    p.shower(0.6, 16.4, 3.0, 3.0)
    p.toilet(4.3, 17.2, face="s")
    p.vanity(0.6, 14.05, 2.4, 1.75)
    p.wd(4.55, 13.95)
    p.window(0, 16.6, 2.0, wall="v")  # frosted, to alley
    p.label(3.6, 16.0, "bath + W/D", "6'-4\" x 5'-8\" &#183; 36 sf", size=11)


def core_stair_upper(p):
    """Straight flight down along the north wall, x 10.2-23.5 / y 16-19.5."""
    p.wall(10.2, 16.0, 13.3, INT)
    p.tint(10.53, 16.33, 12.97, 3.17, "stair")
    p.stair(13.4, 16.33, 10.1, 3.17, direction="e", updown="DN", n=13)
    p.text(11.9, 17.7, "top", size=8, fill="#8d939c")
    p.line(10.2, 16.33, 10.2, 19.5, stroke="#6a7180", sw=2.0)  # guard at top


def hall_and_bedroom_wall(p):
    """Hall x 7.23-10.2 between bath and stair top; bedroom wall at y 13.5."""
    p.tint(7.23, 13.83, 2.97, 5.67, "hall")
    p.wall(7.23, 13.5, 2.97, INT)  # hall/bedroom-zone wall at y 13.5
    p.label(8.7, 17.4, "hall", None, size=10)


def title_block(sheet, W, name, sub, notes):
    t = [
        f'<text x="46" y="46" font-size="21" font-weight="bold" '
        f'fill="#23262b" font-family="Helvetica,Arial,sans-serif">{name}</text>',
        f'<text x="46" y="70" font-size="12.5" fill="#5c636e" '
        f'font-family="Helvetica,Arial,sans-serif">{sub}</text>',
        f'<line x1="46" y1="84" x2="{W - 46}" y2="84" stroke="#d5d8dd" stroke-width="1"/>',
    ]
    return t


def notes_block(x, y, lines):
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * 17}" font-size="11.5" fill="#4a4f57" '
            f'font-family="Helvetica,Arial,sans-serif">{ln}</text>'
        )
    return out


def garage_plan(p, with_stair=True, south_stair=False):
    p.shell()
    p.tint(0.5, 0.5, 23.0, 19.0, "garage")
    # north service band: mech + bench (plumbing stacks under the bath)
    p.tint(0.5, 16.0, 9.7 if with_stair else 23.0, 3.5, "mech")
    p.rect(0.7, 17.4, 5.5, 2.0, "#faf6ee", stroke=FURN_STROKE, sw=1, layer=p.over)
    p.text(3.45, 18.2, "workbench", size=8.5, fill="#8d939c")
    p.over.append(
        f'<circle cx="{p.X(7.6):.1f}" cy="{p.Y(18.3):.1f}" '
        f'r="{1.0 * S:.1f}" fill="#fff" stroke="{FURN_STROKE}" '
        f'stroke-width="1.1"/>'
    )
    p.text(7.6, 18.1, "WH", size=8.5, fill="#8d939c")
    p.text(
        4.9,
        16.55,
        "utilities route to west-center bath above"
        if south_stair
        else "plumbing drops from bath above",
        size=8,
        fill="#8d939c",
    )

    if with_stair:
        p.wall(10.2, 16.0, 13.3, INT)
        p.tint(10.53, 16.33, 12.97, 3.17, "stair")
        p.stair(10.53, 16.33, 9.7, 3.17, direction="w", updown="UP", n=13)
        # entry landing at the bottom (east end) + doors
        p.rect(20.23, 16.33, 3.27, 3.17, "#f9f8f4", layer=p.mid)
        p.text(21.85, 18.0, "entry", size=9, fill="#6a7180")
        p.door(23.5, 16.6, 2.8, wall="v", t=EXT, hinge="left", swing=-1)
        p.door(20.6, 16.0, 2.5, wall="h", hinge="left", swing=-1)
        p.text(21.9, 15.2, "to garage", size=7.5, fill="#8d939c")
    else:
        p.door(23.5, 16.6, 2.8, wall="v", t=EXT, hinge="left", swing=-1)
        p.text(21.7, 17.6, "service door", size=8.5, fill="#8d939c")

    # car + overhead door to the alley (west)
    p.car(1.8, 4.0)
    p.rect(0, 2.5, EXT, 11.0, "#fff", stroke=WALL, sw=1.2, layer=p.over)
    p.line(0.25, 2.5, 0.25, 13.5, stroke=WALL, sw=1.5)
    p.text(1.05, 8.0, "10'&#8211;12' overhead door &#8594; alley", size=8.5, fill=NOTEC, rotate=-90)
    # flex / office corner, SE (window light from south + east)
    fx = 18.0 if with_stair else 16.5
    p.rect(fx, 0.5, 23.5 - fx, 8.5, "none", stroke="#c9a25f", sw=1.2, dash="6 4", layer=p.over)
    p.furn(fx + 0.7, 1.0, 2.0, 4.5, "desk")
    p.label((fx + 23.5) / 2, 6.6, "flex / office", "insulate + mini-split later", size=10.5)
    p.window(19.5, 0, 2.5, wall="h")
    p.window(23.5, 3.5, 2.5, wall="v")
    p.label(9.0, 8.8, "garage / shop", "one bay + wall of storage", size=12)
    if south_stair:
        p.stair(0.5, -4.0, 11.0, 4.0, direction="e", updown="UP", n=13)
        p.rect(
            11.5,
            -4.0,
            12.5,
            4.0,
            "none",
            stroke="#c9cdd3",
            sw=1,
            dash="6 4",
            layer=p.mid,
        )
        p.text(17.75, -2.0, "balcony above", size=8.5, fill="#8d939c")
        p.text(5.9, -4.55, "alley entry &#8592; stair rises east", size=9, fill=NOTEC)
        p.dims(yb=-5.7)
    else:
        p.dims()


# --------------------------------------------------------------------------
# Option A - interior stair, living toward the yard
# --------------------------------------------------------------------------


def upper_a(p):
    p.shell()
    core_stair_upper(p)
    core_bath(p)
    hall_and_bedroom_wall(p)

    # bedroom, west (over the garage bay)
    p.tint(0.5, 0.5, 9.7, 13.0, "bed")
    p.wall(10.2, 0.5, INT, 13.0)  # bedroom east wall
    p.door(7.6, 13.5, 2.4, wall="h", hinge="right", swing=-1)
    p.wall(0.5, 11.5, 6.0, INT)  # closet front
    p.slider(1.0, 11.5, 5.0, wall="h")
    p.tint(0.5, 11.83, 6.0, 1.67, "bed")
    p.text(3.5, 12.5, "closet 6'", size=8.5, fill="#8d939c")
    p.bed_q(0.9, 4.4, head="w")
    p.furn(0.9, 9.6, 1.6, 1.6, "nt")
    p.furn(0.9, 2.6, 1.6, 1.6, "nt")
    p.furn(6.6, 0.85, 3.0, 1.6, "dresser")
    p.window(0, 4.0, 2.5, wall="v")
    p.window(0, 8.0, 2.5, wall="v")
    p.window(3.0, 0, 2.5, wall="h")
    p.label(4.0, 1.9, "bedroom", "9'-8\" x 13' &#183; 126 sf", size=13)

    # kitchen along the stair wall + east return
    p.tint(10.53, 13.83, 12.97, 2.17, "kitchen")
    p.counter(13.0, 13.83, 10.5, 2.17)
    p.fridge(13.1, 13.9)
    p.range_(17.2, 13.83)
    p.counter(21.33, 9.5, 2.17, 4.33)
    p.sink(21.6, 11.3)
    p.window(23.5, 10.4, 2.2, wall="v")
    p.text(14.2, 13.1, "kitchen &#183; 10' run + sink return", size=9.5, fill="#818893")

    # living / dining, east + south
    p.tint(10.53, 0.5, 12.97, 13.0, "living")
    p.table(16.0, 8.8, 4.2, 2.8)
    p.sofa(11.0, 3.2, 3.0, 6.5, back="w")
    p.furn(14.6, 4.7, 3.6, 1.8, "coffee")
    p.furn(22.25, 6.6, 1.15, 2.6, "tv")
    p.window(23.5, 3.5, 2.5, wall="v")
    p.window(13.0, 0, 2.5, wall="h")
    p.window(17.5, 0, 2.5, wall="h")
    p.label(15.6, 1.9, "living / dining", "&#8776; 13' x 13' + kitchen", size=13)
    p.dims()


# --------------------------------------------------------------------------
# Option B - same core, bedroom toward the yard
# --------------------------------------------------------------------------


def upper_b(p):
    p.shell()
    core_stair_upper(p)
    core_bath(p)
    hall_and_bedroom_wall(p)

    # bedroom, east (morning light, not over the garage door)
    p.tint(13.5, 0.5, 10.0, 13.0, "bed")
    p.wall(13.5, 0.5, INT, 13.0)  # bedroom west wall
    p.wall(13.83, 13.5, 9.67, INT)  # bedroom north wall
    p.door(13.5, 10.6, 2.4, wall="v", hinge="right", swing=1)
    # wardrobe band between bedroom and stair (also a sound buffer)
    p.tint(13.83, 13.83, 9.67, 2.17, "bed")
    p.opening(15.0, 13.5, 2.6, wall="h")
    p.line(14.2, 15.7, 23.2, 15.7, dash="3 3")
    p.text(18.6, 14.6, "walk-in wardrobe 9' x 2'", size=8.5, fill="#8d939c")
    p.bed_q(16.2, 6.4, head="n")
    p.furn(14.4, 11.2, 1.6, 1.6, "nt")
    p.furn(21.5, 11.2, 1.6, 1.6, "nt")
    p.furn(14.2, 0.9, 3.0, 1.6, "dresser")
    p.window(23.5, 3.2, 2.5, wall="v")
    p.window(23.5, 8.0, 2.5, wall="v")
    p.window(18.0, 0, 2.5, wall="h")
    p.label(18.5, 3.6, "bedroom", "10' x 13' &#183; 130 sf", size=13)

    # kitchen on the west wall (sink window to the alley)
    p.tint(0.5, 0.5, 2.2, 13.0, "kitchen")
    p.counter(0.5, 3.0, 2.2, 10.5)
    p.fridge(0.55, 10.8)
    p.range_(0.5, 7.2, 2.2, 2.5)
    p.sink(0.75, 4.6)
    p.window(0, 4.2, 2.2, wall="v")
    p.label(1.6, 1.9, "kit.", "10' run", size=10)

    # living / dining, center + south
    p.tint(2.7, 0.5, 10.8, 13.0, "living")
    p.table(4.8, 8.9, 4.2, 2.8)
    p.sofa(8.3, 3.4, 3.0, 6.5, back="e")
    p.furn(4.6, 4.9, 3.4, 1.8, "coffee")
    p.furn(4.2, 0.85, 4.2, 1.2, "media")
    p.window(4.5, 0, 2.5, wall="h")
    p.window(9.0, 0, 2.5, wall="h")
    p.label(7.7, 2.7, "living / dining", "&#8776; 11' x 13'", size=13)
    p.dims()


# --------------------------------------------------------------------------
# Option C - exterior stair on the east face, no stair inside
# --------------------------------------------------------------------------


def upper_c(p):
    # exterior stair + landing, drawn outside the east wall
    p.rect(24.4, 15.6, 3.6, 3.9, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=p.mid)
    p.text(26.2, 17.5, "landing", size=8.5, fill="#8d939c")
    p.stair_v = True
    p.rect(24.4, 4.8, 3.6, 10.8, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=p.mid)
    n = 13
    step = 10.8 / n
    for i in range(1, n):
        p.line(24.4, 4.8 + i * step, 28.0, 4.8 + i * step, stroke="#b3b8bf", sw=1)
    p.line(26.2, 5.4, 26.2, 14.9, stroke="#6a7180", sw=1.3)
    p.line(26.2, 5.4, 25.9, 5.75, stroke="#6a7180", sw=1.3)
    p.line(26.2, 5.4, 26.5, 5.75, stroke="#6a7180", sw=1.3)
    p.text(27.1, 9.8, "DN", size=9, fill="#6a7180", rotate=90)
    p.text(26.3, 2.9, "covered exterior stair", size=9, fill=NOTEC)

    p.shell()
    core_bath(p)
    # entry + kitchen along the blank north wall
    p.door(23.5, 16.5, 3.0, wall="v", t=EXT, hinge="right", swing=-1)
    p.tint(6.9, 13.83, 16.6, 5.67, "kitchen")
    p.counter(9.0, 17.33, 8.5, 2.17)
    p.sink(11.0, 17.7)
    p.range_(14.4, 17.33)
    p.fridge(17.6, 17.0)
    p.furn(20.6, 17.6, 2.6, 1.5, "bench")
    p.table(12.0, 13.9, 4.2, 2.6, chairs=0)
    p.furn(12.9, 12.25, 1.3, 1.3, rx=4)
    p.furn(15.0, 12.25, 1.3, 1.3, rx=4)
    p.text(
        18.2, 12.9, "kitchen / dining &#183; 8'-6\" run on the blank wall", size=9.5, fill="#818893"
    )

    # bedroom SW + pantry strip
    p.tint(0.5, 0.5, 9.7, 11.0, "bed")
    p.wall(10.2, 0.5, INT, 11.0)
    p.wall(0.5, 11.5, 10.03, INT)
    p.door(10.2, 8.6, 2.4, wall="v", hinge="right", swing=1)
    p.wall(0.5, 9.5, 6.0, INT)
    p.slider(1.0, 9.5, 5.0, wall="h")
    p.tint(0.5, 9.83, 6.0, 1.67, "bed")
    p.text(3.5, 10.5, "closet 6'", size=8.5, fill="#8d939c")
    p.bed_q(0.9, 4.0, head="w")
    p.furn(0.9, 2.3, 1.6, 1.4, "nt")
    p.furn(7.2, 0.85, 2.8, 1.6, "dresser")
    p.window(0, 3.2, 2.5, wall="v")
    p.window(0, 6.8, 2.5, wall="v")
    p.window(3.2, 0, 2.5, wall="h")
    p.label(4.6, 2.7, "bedroom", "9'-8\" x 11' &#183; 107 sf", size=13)

    # pantry / storage strip between bedroom and bath
    p.tint(0.5, 11.83, 6.4, 1.67, "hall")
    p.wall(6.9, 11.5, INT, 2.0)
    p.opening(6.9, 11.9, 1.4, wall="v")
    p.text(3.6, 12.5, "pantry / storage 6' x 1'-8\"", size=8.5, fill="#8d939c")

    # living, east + south (the payoff: no stair inside)
    p.tint(10.53, 0.5, 12.97, 13.33, "living")
    p.sofa(11.0, 3.0, 3.0, 6.5, back="w")
    p.furn(14.6, 4.4, 3.6, 1.8, "coffee")
    p.furn(22.25, 5.95, 1.15, 2.3, "tv")
    p.window(23.5, 3.3, 2.5, wall="v")
    p.window(23.5, 8.2, 2.5, wall="v")
    p.window(13.0, 0, 2.5, wall="h")
    p.window(17.5, 0, 2.5, wall="h")
    p.label(15.6, 1.9, "living", "&#8776; 13' x 13' + open dining", size=13)
    p.dims()


# --------------------------------------------------------------------------
# Option D - exterior stair from alley along south face; roof-aware layout
# --------------------------------------------------------------------------


def roof_headroom_guide(p):
    """Diagrammatic headroom bands for current E-W ridge / 16' eave massing.

    Exact bands depend on final floor elevation, structure depth, and roof
    assembly. They are deliberately conservative prompts for section design,
    not construction dimensions.
    """
    p.rect(0.5, 0.5, 23.0, 2.5, "#eceff2", opacity=0.72, layer=p.under)
    p.rect(0.5, 17.0, 23.0, 2.5, "#eceff2", opacity=0.72, layer=p.under)
    p.line(0.5, 10.0, 23.5, 10.0, stroke="#9a7b42", sw=1.2, dash="7 4")
    p.text(12.0, 10.35, "E-W ROOF RIDGE / HIGHEST HEADROOM", size=8.5, fill="#8a6b35")
    p.text(15.4, 18.15, "LOW EAVE ZONE &#8212; storage / low fixtures", size=8, fill="#7d838d")


def upper_d(p):
    # Four-foot-deep covered stair starts at the alley (west) and climbs east.
    # Top landing continues as a balcony to the apartment door at the SE corner.
    p.stair(0.5, -4.0, 11.0, 4.0, direction="w", updown="DN", n=13)
    p.rect(11.5, -4.0, 12.5, 4.0, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=p.mid)
    p.text(17.75, -2.0, "covered balcony / top landing", size=8.5, fill="#7d838d")
    p.text(5.9, -4.55, "alley entry &#8592; stair rises east", size=9, fill=NOTEC)

    p.shell()
    roof_headroom_guide(p)

    # Entry from the south balcony. Tall elements stay away from sloping eaves.
    p.door(20.0, 0.0, 3.0, wall="h", t=EXT, hinge="right", swing=1)

    # Bath sits beside the ridge instead of under the north eave. Storage above
    # it occupies the lower north-roof zone.
    p.tint(0.5, 10.0, 6.4, 6.2, "bath")
    p.wall(6.9, 10.0, INT, 6.2)
    p.wall(0.5, 16.2, 6.73, INT)
    p.slider(6.9, 11.0, 2.4, wall="v")
    p.shower(0.7, 10.4, 3.0, 3.0)
    p.toilet(4.45, 10.7, face="s")
    p.vanity(0.7, 13.75, 2.4, 1.75)
    p.wd(4.35, 13.65)
    p.window(0, 12.2, 2.0, wall="v")
    p.label(3.6, 15.8, "bath + W/D", None, size=10.5)
    p.tint(0.5, 16.53, 6.4, 2.97, "hall")
    p.text(3.6, 17.7, "linen / seasonal storage", size=8.5, fill="#8d939c")

    # Compact west bedroom: bed occupies low south-eave zone; standing route
    # and closet sit nearer the ridge.
    p.tint(0.5, 0.5, 9.7, 9.5, "bed")
    p.wall(10.2, 0.5, INT, 9.5)
    p.wall(0.5, 10.0, 10.03, INT)
    p.door(10.2, 7.1, 2.4, wall="v", hinge="right", swing=1)
    p.wall(0.5, 8.0, 6.0, INT)
    p.slider(1.0, 8.0, 5.0, wall="h")
    p.text(3.5, 9.0, "closet 6'", size=8.5, fill="#8d939c")
    p.bed_q(0.9, 1.2, head="w")
    p.furn(0.9, 6.45, 1.4, 1.3, "nt")
    p.furn(7.2, 0.85, 2.8, 1.5, "dresser")
    p.window(0, 3.3, 2.5, wall="v")
    p.label(7.2, 7.4, "bedroom", "9'-8\" x 9'-6\" &#183; 92 sf", size=11.5)

    # Kitchen uses the east gable wall in its high center band. Fridge and wall
    # cabinets no longer sit under a north/south roof slope.
    p.tint(19.6, 5.6, 3.9, 9.5, "kitchen")
    p.counter(21.33, 6.2, 2.17, 8.9)
    p.sink(21.57, 7.0, w=1.7, h=1.3)
    p.range_(21.33, 9.4, w=2.17, h=2.5)
    p.fridge(20.9, 12.15, w=2.5, h=2.6)
    p.window(23.5, 7.0, 2.0, wall="v")
    p.text(20.25, 11.0, "full-height", size=8, fill="#8d939c", rotate=-90)
    p.text(20.95, 11.0, "gable-wall kitchen", size=8.5, fill="#6f6250", rotate=-90)

    # Open living/dining remains on south/east side and receives balcony entry.
    p.tint(10.53, 0.5, 9.07, 15.0, "living")
    p.sofa(11.0, 2.7, 3.0, 6.2, back="w")
    p.furn(14.6, 4.0, 3.4, 1.8, "coffee")
    p.table(13.2, 11.7, 4.2, 2.6)
    p.furn(18.35, 5.3, 1.1, 2.5, "tv")
    p.window(15.0, 0, 2.5, wall="h")
    p.window(23.5, 3.5, 1.8, wall="v")
    p.label(15.5, 2.25, "living / dining", "balcony entry + S/E light", size=12.5)
    p.dims(yb=-5.7)


# --------------------------------------------------------------------------
# Option E - primary design basis from owner sketch; corrected kitchen
# --------------------------------------------------------------------------


def lower_e(p):
    """Owner-sketch program fitted to the 20 x 24 lower-level envelope."""
    p.shell()

    # Preserve the sketch's adjacency: L-shaped garage left; bath north-center;
    # office northeast; sunroom directly below office; patio outside east wall.
    p.tint(0.5, 0.5, 13.5, 13.5, "garage")
    p.tint(0.5, 14.0, 7.0, 5.5, "garage")
    p.tint(7.5, 14.0, 6.5, 5.5, "bath")
    p.tint(14.0, 14.0, 9.5, 5.5, "flex")
    p.tint(14.0, 0.5, 9.5, 13.5, "living")
    p.wall(7.5, 14.0, 6.5, INT)
    p.wall(7.5, 14.0, INT, 5.5)
    p.wall(14.0, 0.5, INT, 19.0)
    p.wall(14.0, 14.0, 9.5, INT)

    # Bathroom sits over the garage edge, as drawn, with its door to garage.
    p.shower(7.9, 16.1, 3.0, 3.0)
    p.toilet(11.25, 16.25, face="s")
    p.vanity(8.0, 14.35, 2.4, 1.45)
    p.door(10.8, 14.0, 2.4, wall="h", hinge="right", swing=-1)
    p.label(10.75, 15.75, "bathroom", "north-center", size=10.5)

    # Office occupies the northeast band and opens down into the sunroom.
    p.door(16.0, 14.0, 2.6, wall="h", hinge="left", swing=1)
    p.furn(15.0, 17.2, 5.6, 1.6, "desk")
    p.furn(21.0, 15.0, 1.8, 1.2, "files")
    p.door(23.5, 15.8, 2.5, wall="v", t=EXT, hinge="right", swing=-1)
    p.label(18.7, 16.55, "office", "above the sunroom", size=10.5)

    # Large sunroom sits directly below office and opens to exterior east patio.
    p.slider(14.0, 8.0, 3.0, wall="v")
    p.sofa(14.7, 1.0, 8.0, 2.5, back="s")
    p.furn(16.0, 5.2, 3.2, 1.8, "coffee")
    p.furn(20.1, 8.0, 2.4, 2.4, "chair")
    p.slider(23.5, 8.1, 4.0, wall="v", t=EXT)
    p.window(23.5, 3.2, 2.5, wall="v")
    p.label(18.8, 12.3, "sunroom", "directly below office", size=11.5)

    # East patio is exterior, not part of the sunroom footprint.
    p.rect(24.0, 0.0, 3.5, 19.5, "#f6f6f3", stroke="#c9cdd3", sw=1, dash="6 4", layer=p.mid)
    for yy in (1.0, 9.25, 18.0):
        p.rect(26.65, yy, 0.55, 0.55, "#dadde1", stroke="#aeb3ba", sw=1, layer=p.over)
    p.text(25.7, 10.0, "PATIO", size=9, fill="#7d838d", rotate=90)

    # Garage remains alley-loaded, but exact sketch proportions shorten its
    # clear vehicle depth; architect must resolve garage vs sunroom width.
    p.rect(1.0, 3.0, 12.0, 6.2, "#fff", stroke="#b3b8bf", sw=1.3, rx=14, layer=p.over)
    p.text(7.0, 6.0, "compact vehicle / storage", size=8.5, fill="#9aa0a9")
    p.rect(0, 2.2, EXT, 9.7, "#fff", stroke=WALL, sw=1.2, layer=p.over)
    p.line(0.25, 2.2, 0.25, 11.9, stroke=WALL, sw=1.5)
    p.text(1.0, 7.1, "overhead door &#8594; alley", size=8.5, fill=NOTEC, rotate=-90)
    p.label(6.5, 11.0, "garage", "vehicle depth to verify", size=11.5)

    # Exterior stair starts at the west alley and rises east along south wall.
    # After the flight, the raised landing shelters a usable level-1 patio that
    # continues around the southeast corner into the east patio.
    p.stair(0.5, -4.0, 11.0, 4.0, direction="e", updown="UP", n=13)
    p.rect(11.5, -4.0, 16.0, 4.0, "#eef5ed", stroke="#9caf9a", sw=1, dash="6 4", layer=p.mid)
    p.line(24.0, 0.0, 27.5, 0.0, stroke="#f6f6f3", sw=3.2)
    p.text(19.5, -1.55, "COVERED SOUTH PATIO", size=8.7, fill="#668064")
    p.text(19.5, -2.55, "16' x 4' overall &#183; upper landing above", size=7.8, fill="#7b8e79")
    p.text(5.9, -4.55, "alley entry &#8592; stair rises east", size=9, fill=NOTEC)
    p.dims(yb=-5.7)


def upper_e(p):
    """Primary upper plan: owner sketch geometry with roof-aware kitchen."""
    # Patio/balcony stacks directly over the level-1 east patio. South stair
    # reaches it through a narrow top-landing walkway around the SE corner.
    p.rect(24.0, 0.0, 3.5, 19.5, "#f6f6f3", stroke="#c9cdd3", sw=1, dash="6 4", layer=p.mid)
    for yy in (1.0, 9.25, 18.0):
        p.rect(26.65, yy, 0.55, 0.55, "#dadde1", stroke="#aeb3ba", sw=1, layer=p.over)
    p.text(25.7, 10.0, "UPPER PATIO / BALCONY", size=8.5, fill="#7d838d", rotate=90)
    p.stair(0.5, -4.0, 11.0, 4.0, direction="w", updown="DN", n=13)
    p.rect(11.5, -4.0, 16.0, 4.0, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=p.mid)
    p.line(24.0, 0.0, 27.5, 0.0, stroke="#f6f6f3", sw=3.2)
    p.text(19.5, -2.0, "top landing connects directly to upper patio", size=8.5, fill="#7d838d")
    p.text(5.9, -4.55, "alley entry &#8592; stair rises east", size=9, fill=NOTEC)

    p.shell()
    roof_headroom_guide(p)
    p.slider(23.5, 2.0, 5.0, wall="v", t=EXT)
    p.text(22.9, 4.5, "SLIDING GLASS ENTRY", size=8, fill="#5b6f8d", rotate=-90)

    # Bath + laundry and bedroom retain the owner's west-side organization.
    p.tint(0.5, 10.0, 6.4, 6.2, "bath")
    p.wall(6.9, 10.0, INT, 6.2)
    p.wall(0.5, 16.2, 6.73, INT)
    p.slider(6.9, 11.0, 2.4, wall="v")
    p.shower(0.7, 10.4, 3.0, 3.0)
    p.toilet(4.45, 10.7, face="s")
    p.vanity(0.7, 13.75, 2.4, 1.75)
    p.wd(4.35, 13.65)
    p.window(0, 12.2, 2.0, wall="v")
    p.label(3.6, 15.8, "bath + W/D", None, size=10.5)
    p.tint(0.5, 16.53, 6.4, 2.97, "hall")
    p.text(3.6, 17.7, "low-eave linen / storage", size=8.5, fill="#8d939c")

    p.tint(0.5, 0.5, 9.7, 9.5, "bed")
    p.wall(10.2, 0.5, INT, 9.5)
    p.wall(0.5, 10.0, 10.03, INT)
    p.door(10.2, 7.1, 2.4, wall="v", hinge="right", swing=1)
    p.wall(0.5, 8.0, 6.0, INT)
    p.slider(1.0, 8.0, 5.0, wall="h")
    p.text(3.5, 9.0, "closet 6'", size=8.5, fill="#8d939c")
    p.bed_q(0.9, 1.2, head="w")
    p.furn(0.9, 6.45, 1.4, 1.3, "nt")
    p.furn(7.2, 0.85, 2.8, 1.5, "dresser")
    p.window(0, 3.3, 2.5, wall="v")
    p.label(7.2, 7.4, "bedroom", "9'-8\" x 9'-6\" &#183; 92 sf", size=11.5)

    # Corrected kitchen: refrigerator/pantry on full-height east gable;
    # sink/range island lies under the E-W ridge rather than beneath an eave.
    p.tint(11.4, 8.7, 12.1, 6.8, "kitchen")
    p.counter(12.0, 8.9, 7.4, 2.2)
    p.sink(12.45, 9.25, w=1.8, h=1.3)
    p.range_(16.45, 8.9, w=2.3, h=2.2)
    p.counter(21.33, 8.5, 2.17, 6.6)
    p.fridge(20.9, 12.2, w=2.5, h=2.6)
    p.furn(21.45, 9.0, 1.7, 2.4, "pantry")
    p.window(23.5, 9.2, 2.0, wall="v")
    p.text(15.7, 11.7, "ridge-line island &#183; sink + range", size=8.5, fill="#6f6250")
    p.text(20.55, 12.0, "gable appliance wall", size=8.2, fill="#6f6250", rotate=-90)

    # Sketch-like open room: sofa faces a low central TV wall; dining sits NE.
    p.tint(10.53, 0.5, 10.8, 8.2, "living")
    p.sofa(12.0, 1.2, 6.5, 2.7, back="s")
    p.furn(13.4, 4.6, 3.7, 1.7, "coffee")
    p.rect(12.0, 7.35, 6.5, 0.35, "#656970", layer=p.over)
    p.text(15.25, 7.05, "LOW TV WALL", size=8.5, fill="#656970")
    p.table(13.0, 13.0, 4.2, 2.6)
    p.window(15.0, 0, 2.5, wall="h")
    p.window(23.5, 3.5, 1.8, wall="v")
    p.label(15.4, 2.25, "open living / dining", "sliding-glass entry from east patio", size=11.5)
    p.dims(yb=-5.7)


# --------------------------------------------------------------------------
# Option F - recommended development after multidisciplinary review
# --------------------------------------------------------------------------


def option_f_access(p, upper=False):
    """South stair/landing continues around the corner to full east patios."""
    p.stair(0.5, -4.0, 11.0, 4.0, direction="w" if upper else "e", updown="DN" if upper else "UP", n=13)
    p.rect(11.5, -4.0, 16.5, 4.0, "#f6f6f6", stroke="#c9cdd3", sw=1, layer=p.mid)
    p.text(
        19.7,
        -2.0,
        "upper landing connects to east patio" if upper else "covered south patio / landing above",
        size=7.8,
        fill="#7d838d",
    )
    p.rect(24.0, 0.0, 4.0, 19.5, "#f6f6f3", stroke="#c9cdd3", sw=1, dash="6 4", layer=p.mid)
    p.line(24.0, 0.0, 28.0, 0.0, stroke="#f6f6f3", sw=3.2)
    p.text(
        26.0,
        10.0,
        "UPPER EAST PATIO / BALCONY" if upper else "GROUND EAST PATIO",
        size=8.0,
        fill="#7d838d",
        rotate=90,
    )
    p.text(5.9, -4.55, "alley entry &#8592; stair rises east &#183; 14 risers / 13 treads", size=8.5, fill=NOTEC)


def lower_f(p):
    """Full-depth south garage with north service and owner-use band."""
    option_f_access(p, upper=False)
    p.shell()

    # Full-depth garage bay. The car now has 21'+ clear depth instead of 13'-6".
    p.tint(0.5, 0.5, 23.0, 11.0, "garage")
    p.wall(0.5, 11.5, 23.0, INT)
    p.car(3.0, 2.5)
    p.rect(0, 1.3, EXT, 9.7, "#fff", stroke=WALL, sw=1.2, layer=p.over)
    p.line(0.25, 1.3, 0.25, 11.0, stroke=WALL, sw=1.5)
    p.text(1.0, 6.15, "9'-8\" overhead door &#8594; alley", size=8.2, fill=NOTEC, rotate=-90)
    p.window(23.5, 4.0, 3.0, wall="v")
    p.label(12.0, 9.8, "full-depth garage / shop", "&#8776; 23' clear depth &#183; one car + storage", size=11.5)

    # Northwest garage-support zone: equipment remains outside ADU area.
    p.tint(0.5, 11.83, 7.0, 7.67, "mech")
    p.wall(7.5, 11.5, INT, 8.0)
    p.rect(0.8, 17.0, 4.6, 2.0, "#faf6ee", stroke=FURN_STROKE, sw=1, layer=p.over)
    p.text(3.1, 17.8, "workbench / panel", size=8, fill="#8d939c")
    p.furn(5.4, 16.7, 1.6, 2.2, "HPWH", rx=3, fill="#fff")
    p.door(4.5, 11.5, 2.4, wall="h", hinge="right", swing=1)
    p.label(3.8, 15.0, "garage support", "mechanical + storage", size=9.5)

    # Lower bath aligns exactly with upper bath. Short hall prevents bath entry
    # directly from garage and provides a protected transition to owner room.
    p.tint(7.83, 13.83, 6.17, 5.67, "bath")
    p.tint(7.83, 11.83, 6.17, 1.67, "hall")
    p.wall(7.5, 13.5, 6.83, INT)
    p.wall(14.0, 11.5, INT, 8.0)
    p.door(9.5, 11.5, 2.6, wall="h", hinge="right", swing=1)
    p.slider(10.0, 13.5, 2.4, wall="h")
    p.door(14.0, 11.9, 2.4, wall="v", hinge="left", swing=1)
    p.furn(7.9, 16.1, 3.0, 3.0, "storage / coats", rx=2)
    p.toilet(11.4, 16.2, face="s")
    p.vanity(8.0, 13.8, 2.5, 1.65)
    p.label(11.0, 18.5, "powder room", "stacked below level-2 bath", size=9.5)
    p.text(10.9, 12.45, "protected hall", size=7.8, fill="#7d838d")

    # One useful owner/shared room replaces separate office + shallow sunroom.
    p.tint(14.33, 11.83, 9.17, 7.67, "flex")
    p.furn(15.0, 17.2, 5.4, 1.6, "desk")
    p.furn(15.2, 12.5, 5.8, 2.3, "daybed / bench")
    p.slider(23.5, 12.3, 6.0, wall="v", t=EXT)
    p.text(22.9, 15.3, "6' SLIDING DOOR", size=7.4, fill="#5b6f8d", rotate=-90)
    p.label(19.0, 15.6, "owner office / garden room", "zoning classification to confirm", size=9.8)

    p.dims(yb=-5.7)


def upper_f(p):
    """Stacked wet core, conventional entry, workable kitchen, stronger glazing."""
    option_f_access(p, upper=True)
    p.shell()
    p.rect(0.5, 0.5, 23.0, 2.5, "#eceff2", opacity=0.72, layer=p.under)
    p.rect(0.5, 17.0, 23.0, 2.5, "#eceff2", opacity=0.72, layer=p.under)
    p.line(0.5, 10.0, 23.5, 10.0, stroke="#9a7b42", sw=1.2, dash="7 4")
    p.text(15.6, 10.35, "E-W ROOF RIDGE / HIGHEST HEADROOM", size=8.2, fill="#8a6b35")

    # Conventional apartment entry lands near the center of the plan.
    p.door(11.5, 0.0, 3.0, wall="h", t=EXT, hinge="right", swing=1)
    p.text(11.0, 2.8, "coat hooks", size=7.5, fill="#8d939c", rotate=-90)

    # West bedroom; one generous alley casement is sized by architect for EERO.
    p.tint(0.5, 0.5, 9.7, 9.5, "bed")
    p.wall(10.2, 0.5, INT, 9.5)
    p.wall(0.5, 10.0, 10.03, INT)
    p.door(10.2, 7.1, 2.4, wall="v", hinge="right", swing=-1)
    p.bed_q(0.9, 1.2, head="w")
    p.furn(0.9, 6.45, 1.4, 1.3, "nt")
    p.furn(7.2, 0.85, 2.8, 1.5, "dresser")
    p.window(0, 3.0, 3.5, wall="v")
    p.text(0.95, 5.0, "egress casement", size=7.2, fill="#5b6f8d", rotate=-90)
    p.label(7.1, 7.4, "bedroom", "9'-8\" x 9'-6\" &#183; 92 sf", size=11.2)

    # Closet and low storage use the northwest eave band.
    p.tint(0.5, 10.33, 7.0, 3.17, "bed")
    p.wall(0.5, 10.0, 7.0, INT)
    p.wall(0.5, 13.5, 7.0, INT)
    p.slider(1.0, 10.0, 5.5, wall="h")
    p.text(3.75, 11.8, "bedroom closet 7' x 3'-2\"", size=8.2, fill="#8d939c")
    p.tint(0.5, 13.83, 7.0, 5.67, "hall")
    p.wd(5.0, 16.7)
    p.text(3.6, 15.5, "linen / seasonal storage", size=8, fill="#8d939c")
    p.text(3.6, 19.0, "LAUNDRY + SEASONAL STORAGE", size=7.8, weight="bold", fill="#5f6871")

    # Exact vertical stack over lower bath. Standing fixtures stay south,
    # while vanity occupies the lower north-eave side. Laundry moves into the
    # adjacent seasonal-storage room and shares this wet core.
    p.tint(7.83, 13.83, 6.17, 5.67, "bath")
    p.wall(7.5, 13.5, 6.83, INT)
    p.wall(7.5, 13.5, INT, 6.0)
    p.wall(14.0, 13.5, INT, 6.0)
    p.slider(10.0, 13.5, 2.4, wall="h")
    p.shower(7.9, 13.9, 3.0, 3.0)
    p.toilet(11.4, 14.1, face="s")
    p.vanity(11.0, 17.2, 2.6, 1.75)
    p.slider(7.5, 17.0, 2.2, wall="v")
    p.text(10.9, 19.0, "STACKED BATH", size=8.5, weight="bold", fill="#5f6871")

    # Kitchen: sink-only island beside the wet core; range and tall storage on
    # the full-height east gable. All primary work aisles remain near ridge.
    p.tint(10.53, 8.5, 12.97, 5.0, "kitchen")
    p.counter(11.6, 9.1, 6.8, 3.0)
    p.sink(12.1, 9.75, w=2.0, h=1.4)
    p.text(15.1, 10.65, "prep + DW", size=8, fill="#8d939c")
    p.counter(21.0, 8.4, 2.5, 7.0)
    p.range_(21.0, 8.8, w=2.5, h=2.6)
    p.fridge(20.9, 12.0, w=2.6, h=2.6)
    p.furn(21.25, 15.1, 2.0, 2.2, "pantry")
    p.text(20.55, 12.0, "range / fridge / pantry", size=8, fill="#6f6250", rotate=-90)

    # Dining occupies the seated north-eave zone; east window supplies light.
    p.tint(14.33, 13.83, 9.17, 5.67, "living")
    p.table(15.2, 14.0, 4.2, 2.6)
    p.window(23.5, 15.0, 3.5, wall="v")
    p.text(18.5, 18.9, "seated low-eave dining", size=8.0, fill="#8d939c")

    # Living room keeps strongest south/east glazing. Large slider serves the
    # upper east patio reached continuously from the stair landing.
    p.tint(10.53, 0.5, 12.97, 8.0, "living")
    p.sofa(15.2, 1.1, 6.2, 2.7, back="s")
    p.furn(16.3, 4.4, 3.5, 1.7, "coffee")
    p.rect(13.0, 7.2, 6.0, 0.35, "#656970", layer=p.over)
    p.text(16.0, 6.9, "LOW TV WALL", size=8.3, fill="#656970")
    p.slider(23.5, 1.5, 6.0, wall="v", t=EXT)
    p.text(22.9, 4.5, "6' SLIDING DOOR", size=7.4, fill="#5b6f8d", rotate=-90)
    p.window(16.0, 0, 5.0, wall="h")
    p.label(18.2, 3.8, "open living", "large slider to connected east patio", size=11.5)

    p.dims(yb=-5.7)


# --------------------------------------------------------------------------
# Sheet assembly
# --------------------------------------------------------------------------

PLAN_W = int(BW * S)  # 624
LM, GAP, RM = 104, 130, 172
SHEET_W = LM + PLAN_W + GAP + PLAN_W + RM
PLAN_TOP = 156


def make_sheet(
    fname,
    name,
    sub,
    upper_fn,
    notes,
    with_stair=True,
    east_x=None,
    extra_bottom=0,
    upper_south_note=None,
    upper_south_y=-2.9,
    south_stair=False,
    lower_fn=None,
    lower_title="LEVEL 1 &#8212; garage / entry",
    lower_east_x=None,
):
    plan_h = int(BH * S)
    notes_y = PLAN_TOP + plan_h + 120 + extra_bottom
    H = notes_y + 17 * len(notes) + 46
    body = []
    body += title_block(None, SHEET_W, name, sub, notes)

    g = Plan(LM, PLAN_TOP)
    if lower_fn:
        lower_fn(g)
    else:
        garage_plan(g, with_stair=with_stair, south_stair=south_stair)
    g.context(
        lower_title,
        east_x=lower_east_x,
        south_text=upper_south_note if south_stair else None,
        south_y=upper_south_y if south_stair else -2.9,
    )
    body.append(g.svg())

    u = Plan(LM + PLAN_W + GAP, PLAN_TOP)
    upper_fn(u)
    u.context(
        "LEVEL 2 &#8212; apartment &#183; 480 sf gross / 437 sf net",
        east_x=east_x,
        south_text=upper_south_note,
        south_y=upper_south_y,
    )
    body.append(u.svg())

    body += notes_block(46, notes_y, notes)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}" '
        f'height="{H}" viewBox="0 0 {SHEET_W} {H}" '
        f'preserveAspectRatio="xMinYMin meet">'
        f'<rect width="{SHEET_W}" height="{H}" fill="#ffffff"/>' + "".join(body) + "</svg>"
    )
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
    return out, SHEET_W, H


def to_png(svg_path, w, h):
    png = svg_path.replace(".svg", ".png")
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        subprocess.run([rsvg, "-w", str(w * 2), "-h", str(h * 2), svg_path, "-o", png], check=True)
        print(f"wrote {png}")
        return
    for c in (
        "/opt/pw-browsers/chromium/chrome-linux/chrome",
        "/opt/pw-browsers/chromium",
        shutil.which("chromium") or "",
    ):
        if c and os.path.exists(c) and not os.path.isdir(c):
            return to_png_with(c, svg_path, png, w, h)
        if c and os.path.isdir(c):
            for root, _, files in os.walk(c):
                if "chrome" in files:
                    return to_png_with(os.path.join(root, "chrome"), svg_path, png, w, h)
    print(f"(no renderer found - keep {svg_path} as SVG)")


def to_png_with(binary, svg_path, png, w, h):
    subprocess.run(
        [
            binary,
            "--headless",
            "--no-sandbox",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--virtual-time-budget=5000",
            f"--screenshot={png}",
            f"--window-size={w},{h + 40}",
            f"file://{svg_path}",
        ],
        check=True,
        capture_output=True,
    )
    print(f"wrote {png}")


if __name__ == "__main__":
    sheets = [
        (
            "option-a-living-east.svg",
            "Option A &#8212; interior stair &#183; living toward the yard",
            "Stair + bath + laundry on the blank north wall &#183; bedroom west "
            "(alley) &#183; kitchen/living/dining open to the south + east light",
            upper_a,
            True,
            [
                "&#8226; PRO: one weather-tight entry; living + dining get the yard view and the best (S+E) light; bedroom is the private, dim side.",
                "&#8226; PRO: whole north wall is stair/bath/closet &#8212; nothing lost to the no-window rule; single stacked plumbing chase (bath over garage mech corner).",
                "&#8226; CON: interior stair costs &#8776;46 sf on each floor; bedroom sits over the overhead door (door rumble &#8212; use a quiet side-mount opener).",
                "&#8226; CON: kitchen run faces an interior wall (no sink window; sink is on the east return instead).",
            ],
        ),
        (
            "option-b-bedroom-east.svg",
            "Option B &#8212; interior stair &#183; bedroom toward the yard",
            "Same core (stair/bath/laundry north) &#183; bedroom east with morning "
            "light &#183; kitchen on the west wall with an alley-side sink window",
            upper_b,
            True,
            [
                "&#8226; PRO: bedroom gets morning (E) light, is NOT over the overhead door, and the 9' wardrobe band buffers it from stair noise.",
                "&#8226; PRO: kitchen sink gets a real window (west/alley); big storage (wardrobe + bath W/D).",
                "&#8226; CON: living room loses the yard view &#8212; south windows only &#8212; and afternoon-west sun hits the kitchen, not the sofa.",
                "&#8226; CON: groceries cross the whole living room from the stair; dining is darker at breakfast.",
            ],
        ),
        (
            "option-c-exterior-stair.svg",
            "Option C &#8212; exterior stair &#183; maximum apartment",
            "Covered stair on the east face &#183; all 437 sf net stays inside "
            "&#183; kitchen earns its keep on the blank north wall",
            upper_c,
            False,
            [
                "&#8226; PRO: &#8776;46 sf more apartment AND &#8776;46 sf more garage than A/B; kitchen sits on the windowless north wall where nothing else wants to be.",
                "&#8226; PRO: garage stays one clean 23' x 19' volume (shop + car + bigger office corner); apartment and garage are fully separate (good if you ever rent one).",
                "&#8226; CON: you arrive outside &#8212; groceries, rain, ice; the stair + landing add bulk to the yard-facing facade and shade the east windows below.",
                "&#8226; CON: harder aging-in-place story; exterior stairs need real detailing (covered, lit, guard) to not look tacked-on.",
            ],
        ),
        (
            "option-d-south-stair-roof-aware.svg",
            "Option D &#8212; alley stair + south balcony &#183; roof-aware plan",
            "Covered stair rises east along south face &#183; kitchen moves to high gable-end zone "
            "&#183; low eave bands hold bed, seating, and storage",
            upper_d,
            False,
            [
                "&#8226; PRO: direct alley access; straight south stair arrives at a covered SE balcony without consuming apartment or garage area.",
                "&#8226; PRO: fridge + tall kitchen cabinets sit on the east gable end near the E-W ridge, not beneath a north/south roof slope.",
                "&#8226; ROOF CHECK: headroom bands are diagrammatic; final section must verify floor elevation, joist depth, insulation, and 7' ceiling compliance.",
                "&#8226; SITE RESPONSE: selected 18' x 6' replacement shed sits on the south 5' setback, leaving 5' clear before the stair; verify fire + maintenance details.",
            ],
        ),
        (
            "option-e-primary-design-basis.svg",
            "Option E &#8212; PRIMARY DESIGN BASIS &#183; owner sketch corrected",
            "South alley stair + covered lower patio + stacked east patios &#183; garage/bath/office/sunroom below "
            "&#183; west bedroom + roof-aware open kitchen/living above",
            upper_e,
            False,
            [
                "&#8226; DESIGN BASIS: preserves the owner's two-level sketch, west bedroom/bath core, central TV wall, open living room, and stacked east patios.",
                "&#8226; KITCHEN FIX: fridge + pantry move to the full-height east gable; sink/range island sits beneath the E-W ridge, clear of low north/south eaves.",
                "&#8226; LEVEL 1: garage left; bath north-center; office northeast; sunroom below; covered south patio connects around the corner to the east patio.",
                "&#8226; LEVEL 2 ENTRY: south stair and top landing lead to an east patio directly above level 1; apartment entry is a sliding glass door.",
                "&#8226; GARAGE CHECK: exact sketch proportions leave only about 13'-6\" clear depth; enlarge/rebalance footprint or reduce sunroom width for a typical 16' car.",
                "&#8226; AREA/ZONING CHECK: confirm whether enclosed office/sunroom count as ADU living area; upper level alone is 480 sf gross against the working 500 sf cap.",
                "&#8226; ROOF/SITE CHECK: verify section/headroom and the selected 5' shed-to-stair zone for safe fire, drainage, and maintenance clearance.",
            ],
        ),
        (
            "option-f-recommended-development.svg",
            "Option F &#8212; RECOMMENDED DEVELOPMENT &#183; stacked core + real garage",
            (
                "Full-depth south garage &#183; stacked north-center wet core &#183; "
                "owner office/garden room northeast &#183; connected south landing + "
                "full east patios with large sliders"
            ),
            upper_f,
            False,
            [
                "&#8226; GARAGE FIX: one 11'-wide bay now runs nearly the full 24' depth; east window adds shop daylight without sacrificing vehicle length.",
                "&#8226; STACKED CORE: level-2 bath aligns over a level-1 powder room; W/D moves into adjacent low-eave seasonal storage beside the wet core.",
                "&#8226; FIRE / AIR: protected hall replaces the garage-to-sunroom slider; architect to specify rated separation, protected door, and sealed penetrations.",
                "&#8226; KITCHEN FIX: 6'-10\" x 3' sink/prep island replaces the undersized sink+range island; range, fridge, and pantry use the full-height east gable.",
                "&#8226; ENTRY / PATIO: stair landing continues around the SE corner to a full east patio; large sliders serve both living and garden room.",
                "&#8226; WINDOWS: west bedroom casement to meet final EERO clear opening; enlarged south living + east dining glazing; north wall remains solid.",
                "&#8226; ZONING HOLD: owner office/garden room and lower bath are not assumed to be ADU floor area; obtain written classification before permitting.",
                "&#8226; SECTION HOLD: verify 20' height cap, sloped-ceiling headroom, 14-riser stair, guards, structure, drainage, MEP, and all dimensions.",
            ],
        ),
    ]
    for fname, name, sub, fn, with_stair, notes in sheets:
        east_x = BW + 5.6 if fn is upper_c else (31.5 if fn is upper_f else (28.5 if fn is upper_e else None))
        is_south_stair = fn in (upper_d, upper_e, upper_f)
        is_e = fn is upper_e
        is_f = fn is upper_f
        path, w, h = make_sheet(
            fname,
            name,
            sub,
            fn,
            notes,
            with_stair=with_stair,
            east_x=east_x,
            extra_bottom=190 if is_south_stair else 0,
            upper_south_note=(
                "south stair zone &#183; 5' clear to selected 18' x 6' replacement shed"
                if is_south_stair
                else None
            ),
            upper_south_y=-7.1 if is_south_stair else -2.9,
            south_stair=is_south_stair,
            lower_fn=lower_f if is_f else (lower_e if is_e else None),
            lower_title=(
                "LEVEL 1 &#8212; full-depth garage / powder room / owner room"
                if is_f
                else "LEVEL 1 &#8212; garage / bath / office / sunroom"
                if is_e
                else "LEVEL 1 &#8212; garage / entry"
            ),
            lower_east_x=31.5 if is_f else (28.5 if is_e else None),
        )
        to_png(path, w, h)
