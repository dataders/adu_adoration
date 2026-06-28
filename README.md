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

## Current design direction
A **20 × 24 ft, ≤20 ft tall, two-story detached ADU** — garage/office below, ~480 sf 1-bed above —
at the rear, garage door facing the alley, just north of the shed.

By-right in R-5 (5 ft side + 5 ft rear setbacks; 20 ft accessory height cap; accessory footprint ≤ house
footprint; ADU living area ≤ greater of 500 sf or 1/3 of the house = 500 sf cap). A 24×24 was ruled out —
576 sf upstairs exceeds the 500 sf cap for this 1,303 sf house.

## Open questions (need owner confirmation / field measurement)
- **Front setback:** owner stated 16 ft, but satellite imagery suggests ~25–35 ft with a large backyard.
  This drives the deck-to-shed distance (drawn ~49 ft; owner noted ~17 ft — unreconciled).
- **North side setback:** current sketch shows 3 ft, which is **below the R-5 by-right minimum of 5 ft** and
  would require a Board of Zoning Appeals variance. The by-right alternative is an 18-ft-wide ADU at 5 ft.
- **Shed footprint:** 12 × 18 (owner) vs 360 sf detached garage (assessor).

## Repo layout
- [`plan/`](plan/) — working site-plan diagram (`site-plan.svg` + rendered `site-plan.png`).
  Render with `rsvg-convert -w 1920 -h 880 site-plan.svg -o site-plan.png` (cairosvg has no cairo lib here).
- [`images/`](images/) — all reference imagery (hand sketches, assessor sketch, satellite shots). See its README.
- [`documents/`](documents/) — source PDFs (hand-drawn site plans, assessor sketch, DataScout property report).

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
