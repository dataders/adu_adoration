# ADU planning — 112 W 29th St, Richmond VA

Brainstorming and site-planning for a detached accessory dwelling unit (ADU) in the
backyard of **112 W 29th St** (PID 43615 / PIN S0001130005), Richmond, VA 23225.

## Lot & existing conditions
*(confirmed from the City/DataScout property record — see `documents/`)*
- Lot: **45 ft × 148 ft** (~6,660 sf / 0.153 ac), zoned **R-5** (single-family). Subdivision: Fonticello Park, L9 PT7 B41.
- House: **1,303 sf, one story**, built **1931** ("1 Sty Oldest" style), gable roof, green wood siding,
  3 bed / 2 bath, heat pump, hardwood floors. Plus a **138 sf wood deck (SW)** and **87 sf open front porch (NE)**.
- Orientation: house faces the **street on the east (front)**; an **alley runs along the west (rear)**.
- Outbuilding: the current **12 × 18 shed** in the southwest corner conflicts with Option E access and is
  designated for removal. Selected replacement is a **low-profile 18 × 6 shed (108 sf)**, 8 ft off the alley
  with the south edge of its maximum envelope on the 5-ft side setback. The assessor record logs the old structure as a 360 sf
  detached garage (18×20); field-verify removal scope and records during permitting.
- 2026 assessment: land $87,000 + improvements $324,000 = **$411,000**.

## Current design direction
A **20 × 24 ft, ≤20 ft tall, two-story detached ADU** — garage/office below, ~480 sf 1-bed above —
at the rear, garage door facing the alley, just north of the shed.

**Recommended development concept: Option F.** It retains Option E's 20 × 24 envelope, west bedroom,
south alley stair, and east-facing living space, but corrects the main coordination problems found in
multidisciplinary review: a full-depth south garage bay; vertically stacked north-center bathrooms;
a separate garage-support/mechanical zone; one northeast owner office/garden room; a conventional
apartment entry on a connected south landing; full-length stacked east patios; and large east sliders
on both floors. Laundry occupies the upper low-eave seasonal-storage room, and the lower bath is a
powder room. See
[`apartment/option-f-recommended-development.png`](apartment/option-f-recommended-development.png) and
[`plan/site-plan-option-f-architect.pdf`](plan/site-plan-option-f-architect.pdf).
Plan-informed interior views are available for the
[`first-floor garage and service wall`](renderings/option-f-first-floor-interior.png) and the
[`second-floor apartment`](renderings/option-f-second-floor-interior-corrected.png).

The current owner-coordination deliverable is the **11-sheet schematic construction and engineering
basis set** at [`output/pdf/adu-option-f-construction-engineering-basis.pdf`](output/pdf/adu-option-f-construction-engineering-basis.pdf).
It coordinates code/zoning, site and utilities, dimensioned plans, roof/opening schedules, elevations,
sections, envelope, preliminary structural framing, MEP/life safety, and permit closeout. Regenerate it
with `uv run --with reportlab --with pillow python3 plan/generate_construction_basis_set.py`. It is
explicitly not sealed or for construction; survey, soil, zoning rulings, engineered products, energy
compliance, utility verification, and trade designs remain required.

**Owner-sketch baseline: Option E.** It translates the owner's two-level sketch into the
20 × 24 enclosed envelope: garage/bath/office/sunroom below; bedroom/bath-laundry/open living above;
4-ft-deep exterior stair/landing from the alley along the south side to 3-ft-6-in-deep stacked east
patios. Apartment entry is a sliding glass door from the upper patio. Refrigerator and pantry sit
on the full-height east gable,
with the sink/range island beneath the E–W ridge. See [`apartment/`](apartment/).
The 4-ft-deep upper landing wraps around the southeast corner to the patio's outer edge, creating a
full 3-ft-6-in-wide open connection into the upper patio rather than stopping at the ADU wall. After
the 11-ft stair flight, the raised landing also shelters a 16 × 4 ft covered level-1 south patio
(12 ft 6 in × 4 ft directly along the south wall) that connects around the corner to the east patio.

**Selected site response:** remove the current 12 × 18 shed and replace it with a low-profile 18 × 6
shed on the southern 5-ft setback. Its north edge sits 5 ft south of the Option E stair, creating a
usable circulation, drainage, and maintenance strip while preserving 108 sf of storage. Treat 18 × 6
as the maximum outer envelope; roof edges, gutters, and foundations must remain inside it. Including
exterior circulation, Option E extends from 5 ft to 32.5 ft off the alley and from 16 ft to 40 ft
north-south, while the enclosed building remains 24 × 20 ft.

By-right in R-5 (5 ft side + 5 ft rear setbacks; 20 ft accessory height cap; accessory footprint ≤ house
footprint; ADU living area ≤ greater of 500 sf or 1/3 of the house = 500 sf cap). A 24×24 was ruled out —
576 sf upstairs exceeds the 500 sf cap for this 1,303 sf house.

## Confirmed by field measurement (2026-06-28)
- **Front setback: 25 ft** — main east wall to the front (east) property line (inside edge of the sidewalk).
- **Front porch projects ~2 ft** east of the house wall.
- Resulting **deck-to-shed clear distance ≈ 40 ft** — the earlier ~17 ft figure was a mismeasurement.

## Open questions
- **North side setback:** current plan places the ADU at the **5-ft R-5 minimum**; no north-setback
  variance is assumed.
- **Shed records:** reconcile removal of the field-measured 12 × 18 shed with the assessor's 360 sf
  detached-garage record.

## Repo layout
- [`apartment/`](apartment/) — floor-plan studies for the 1-bed apartment (level 2) and garage
  (level 1): five furnished layout options (A–E) as SVG/PNG sheets, the decision framework,
  and `generate_floorplans.py` to iterate them.
- [`model/`](model/) — 3D massing model of the whole lot (house + shed + proposed ADU):
  - **`site-model-3d.html`** — coordinated Option F interactive whole-site viewer
    (orbit/zoom/pan, layer toggles, preset views).
  - **`site-model.obj`** (+ `.mtl`) — coordinated Option F whole-site OBJ (feet, Y-up).
  - **`adu-option-f.step` / `.brep`** — current neutral CAD building model.
  - **`adu-option-f.glb` / `.obj`** — current real-time/mesh building model.
  - **`adu-option-f-manifest.json`** — version, datums, sources, bounds, and named objects.
  - `option_f_geometry.py` — canonical Option F geometry contract.
  - `generate_option_f_model.py` and `generate_3d_model.py` — regenerate current model artifacts.
  - Option E FreeCAD/Sweet Home artifacts remain historical comparison files; see
    [`model/README.md`](model/README.md) for the boundary.
- [`plan/`](plan/) — the site plan in several formats:
  - **`site-plan-option-f.dxf` / `site-plan-option-f-architect.pdf`** — recommended Option F site response
    and current architect handoff, with south stair/landing connected around the southeast corner to stacked east patios.
  - **`site-plan.dxf` / `site-plan-architect.pdf`** — historical Option E site study retained for comparison.
  - `site-plan.svg` / `site-plan.png` — the quick colored diagram. Render with
    `rsvg-convert -w 1920 -h 880 site-plan.svg -o site-plan.png` (cairosvg has no cairo lib here).
  - `generate_site_plan.py` — regenerates the DXF + PDF:
    `uv run --no-project --with ezdxf --with matplotlib python3 plan/generate_site_plan.py`.
    Edit `FRONT_SETBACK` at the top once the front-yard measurement is confirmed.
- [`images/`](images/) — all reference imagery (hand sketches, assessor sketch, satellite shots). See its README.
- [`documents/`](documents/) — source PDFs (hand-drawn site plans, assessor sketch, DataScout property report).
- [`inspiration/`](inspiration/) — reference photos of styles we like for the ADU exterior.
- [`renderings/`](renderings/) — Option F exterior and interior concept imagery, including the
  first-floor garage/service-wall view and corrected second-floor apartment view.
- [`sync/`](sync/) — one-way sync that mirrors a **public Pinterest board** into `inspiration/`
  from the board's RSS feed (no login/API token). Save your board URL to `sync/board.txt`, then
  `python3 sync/pinterest_pull.py`. See its README for limits (pull-only, no delete-sync) and how
  to upgrade to full bidirectional via the Pinterest API.

## Validate plans and model artifacts

Run the same architecture checks used by CI:

```sh
./bin/check-plans
```

The command audits the Option F DXF and access geometry, checks the coordinated
artifact manifest and model datums, loads all 79 STEP solids with OpenCascade,
checks the GLB container, and parses committed PDF/PNG outputs. CI additionally
installs the official Khronos glTF Validator and requires zero errors and zero
warnings. These checks enforce documented Option F schematic invariants; they
do not certify zoning, building-code compliance, or constructability.

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
