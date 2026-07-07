# ADU planning — 112 W 29th St, Richmond VA

Brainstorming and site-planning for a detached accessory dwelling unit (ADU) in the
backyard of **112 W 29th St** (PID 43615 / PIN S0001130005), Richmond, VA 23225.

## Lot & existing conditions
*(confirmed from the City/DataScout property record — see `documents/`)*
- Lot: **45 ft × 148 ft** (~6,660 sf / 0.153 ac), zoned **R-5** (single-family). Subdivision: Fonticello Park, L9 PT7 B41.
- House: **1,303 sf, one story**, built **1931** ("1 Sty Oldest" style), gable roof, green wood siding,
  3 bed / 2 bath, heat pump, hardwood floors. Plus a **138 sf wood deck (SW)** and **87 sf open front porch (NE)**.
- Orientation: house faces the **street on the east (front)**; an **alley runs along the west (rear)**.
- Outbuilding: the owner uses a **12 × 18 shed** fixed in the **southwest corner**, 8 ft off the alley, 6 ft off
  the south line. ⚠️ The assessor record logs this as a **360 sf detached garage (18×20)** — the owner says that
  measurement is wrong; we use 12 × 18, but the larger figure would tighten the lot-coverage and footprint math.
- 2026 assessment: land $87,000 + improvements $324,000 = **$411,000**.

## Current design direction — "balcony-entry scheme" (v2, 2026-07-04)
A **24 × 20 ft, two-story detached ADU**, front gable facing the alley (ridge E–W, 12:12),
eave 15 ft / ridge 25 ft → **20 ft height midpoint = at the accessory cap**. From the owners' sketch:
- **No interior stair** — an **exterior stair along the S wall** rises to a **covered 6×20 east balcony**,
  the unit's sole entry (frees ~55 sf vs an interior stair).
- **Downstairs:** garage (11×20, carriage door to alley) + office + open sunroom + bath;
  big sliders/patio doors east to a grade-level patio.
- **Upstairs (the ADU):** 480 sf gross ≤ 500 cap ✓ — bed + bath + stacked W/D on the west gable end,
  open kitchen/living east. **Kitchen sits on the "TV wall"** (tall interior partition) because the
  N and S walls are 4.5-ft knee walls in this orientation; base-only cabinets OK along the N knee wall.
- Plans: `plan/floor-plans-balcony-scheme.{svg,png}` · 3D: `renderings/massing-3d-interactive.html`
  (live: https://claude.ai/code/artifact/6271afac-2200-4cf2-b6f8-3acbd972b580)

By-right in R-5 (5 ft side + 5 ft rear setbacks; 20 ft accessory height cap measured to the
eave–ridge midpoint; accessory footprint ≤ house footprint; ADU living area ≤ greater of 500 sf or
1/3 of the house = 500 sf cap). A 24×24 was ruled out — 576 sf upstairs exceeds the 500 sf cap for
this 1,303 sf house.

## Confirmed by field measurement (2026-06-28)
- **Front setback: 25 ft** — main east wall to the front (east) property line (inside edge of the sidewalk).
- **Front porch projects ~2 ft** east of the house wall.
- Resulting **deck-to-shed clear distance ≈ 40 ft** — the earlier ~17 ft figure was a mismeasurement.

## Open questions
- **North side setback:** current plan shows 3 ft, which is **below the R-5 by-right minimum of 5 ft** and
  would require a Board of Zoning Appeals variance. The by-right alternative is an 18-ft-wide ADU at 5 ft.
- **Shed footprint:** 12 × 18 (owner) vs 360 sf detached garage (assessor record).
- **Does the downstairs count toward the 500 sf ADU cap?** Intent: downstairs (office/sunroom/bath,
  no kitchen, no interior connection) = accessory space for the *main* house; upstairs alone is the
  dwelling unit (480 sf). If zoning counts all conditioned space, the scheme totals ~940 sf → ask Mercer.
- **S-stair clearance:** the exterior stair projects ~4 ft south — check the gap to the shed / shift bldg N.
- **Code Refresh watch (draft 3 due mid-July 2026):** ADU cap may rise 500→1,000 sf, **but** draft 2
  bars ADUs *taller than the primary dwelling* — a risk for this 25-ft-ridge scheme behind a 1-story
  house (measure the house ridge). Also proposed: 2-unit/2-building lot caps (house + shed + ADU = 3?).
  State law SB 531 (eff. 2027-07-01) mandates by-right ADUs, but cities with pre-2026 ADU ordinances
  (Richmond, 2023) are likely exempt.

## Repo layout
- [`apartment/`](apartment/) — floor-plan studies for the 1-bed apartment (level 2) and garage
  (level 1): three furnished layout options (A/B/C) as SVG/PNG sheets, the decision framework,
  and `generate_floorplans.py` to iterate them.
- [`model/`](model/) — 3D massing model of the whole lot (house + shed + proposed ADU):
  - **`site-model-3d.html`** — interactive 3D viewer, open directly in a browser
    (orbit/zoom/pan, layer toggles, preset views).
  - **`site-model.obj`** (+ `.mtl`) — true-scale OBJ (feet, Y-up) for SketchUp / Blender.
  - `generate_3d_model.py` — regenerates both: `python3 model/generate_3d_model.py` (no deps).
- [`plan/`](plan/) — the site plan in several formats:
  - **`site-plan.dxf`** — true-scale CAD file (1 unit = 1 ft, layered: lot / house / shed / ADU /
    R-5 setbacks / dims / text). This is the file to hand an architect — opens in AutoCAD, Revit,
    SketchUp, etc.
  - **`site-plan-architect.pdf`** — printable/markup version of the DXF (north arrow, scale bar, title block).
  - `site-plan.svg` / `site-plan.png` — the quick colored diagram. Render with
    `rsvg-convert -w 1920 -h 880 site-plan.svg -o site-plan.png` (cairosvg has no cairo lib here).
  - `generate_site_plan.py` — regenerates the DXF + PDF:
    `uv run --no-project --with ezdxf --with matplotlib python3 plan/generate_site_plan.py`.
    Edit `FRONT_SETBACK` at the top once the front-yard measurement is confirmed.
- [`images/`](images/) — all reference imagery (hand sketches, assessor sketch, satellite shots). See its README.
- [`documents/`](documents/) — source PDFs (hand-drawn site plans, assessor sketch, DataScout property report).
- [`inspiration/`](inspiration/) — reference photos of styles we like for the ADU exterior.
- [`sync/`](sync/) — one-way sync that mirrors a **public Pinterest board** into `inspiration/`
  from the board's RSS feed (no login/API token). Save your board URL to `sync/board.txt`, then
  `python3 sync/pinterest_pull.py`. See its README for limits (pull-only, no delete-sync) and how
  to upgrade to full bidirectional via the Pinterest API.

## Resources & sources

**Property records**
- actDataScout — Richmond, VA real property: https://www.actdatascout.com/RealProperty/Virginia/Richmond
  (looked up by **PIN `S0001130005`**; PID 43615). Full report saved in `documents/`.

**Richmond zoning — source of truth is Municode Ch. 30, NOT HubSpot-hosted PDFs (those are outdated)**
- Zoning ordinance (Code of Ordinances, Chapter 30): https://library.municode.com/va/richmond/codes/code_of_ordinances
- R-5 district — Art. IV, Div. 6: https://library.municode.com/va/richmond/codes/code_of_ordinances?nodeId=CH30ZO_ARTIVDIRE_DIV6SIMIREDI
- Accessory buildings — Art. VI, Div. 9: https://library.municode.com/va/richmond/codes/code_of_ordinances?nodeId=CH30ZO_ARTVISURE_DIV9ACBU
- City of Richmond ADU page: https://www.rva.gov/planning-development-review/accessory-dwelling-units
- "Code Refresh" zoning rewrite (still in draft as of mid-2026): https://www.rva.gov/planning-development-review/code-refresh
- Board of Zoning Appeals (variances): https://www.rva.gov/planning-development-review/board-zoning-appeals

**Key code sections relied on**
- §30-410.4/.5/.6/.7 — R-5 lot area & width, yards (front 25 / side 5 / rear 5), lot coverage 35%, height 35 ft
- §30-620.1 — lots of record & narrow-lot (<50 ft) side-yard relief (10% of width, min 3 ft)
- §30-680.1 — accessory-building yard relief applies only to buildings **≤12 ft** tall
- §30-680.4 — **20 ft** accessory height cap; all accessory footprint ≤ main-building footprint

**Contacts**
- Richmond Zoning Administration: 804-646-6340 · ADU planning (Brian Mercer): 804-646-6704

*Zoning notes here are research, not legal advice — confirm specifics with Zoning Administration.*
