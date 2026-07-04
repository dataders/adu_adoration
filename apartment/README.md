# Apartment layout — the 1-bed above the garage

How to plan (and keep iterating) the ~480 sf apartment on level 2 of the
20 × 24 ADU. Three worked schemes live here as full sheets (garage level +
apartment level, furnished, annotated):

| sheet | stair | bedroom | living | headline trade |
|---|---|---|---|---|
| [`option-a-living-east`](option-a-living-east.png) | interior, north wall | west (alley) | east + south | living gets the yard view; bedroom sits over the garage door |
| [`option-b-bedroom-east`](option-b-bedroom-east.png) | interior, north wall | east (yard) | center + south | quiet bright bedroom; living loses the yard view |
| [`option-c-exterior-stair`](option-c-exterior-stair.png) | **exterior**, east face | west (alley) | east + south | ~46 sf more apartment *and* garage; you arrive outside |

Regenerate after editing: `python3 apartment/generate_floorplans.py`
(pure-stdlib Python → SVG; PNGs render via the local headless chromium,
or `rsvg-convert` if present).

## The fixed constraints (get these in your head first)

Everything below falls out of the site plan and zoning already confirmed in
the repo README:

1. **Envelope: 24' E-W × 20' N-S.** With 2×6 exterior walls the interior is
   ~23' × 19' = **437 sf net** (480 sf gross — under the 500 sf R-5 cap, so
   there is no bonus square footage to find; only better arrangements).
2. **The north wall is only 3' off the property line.** The building code
   (IRC/VA R302.1) sharply limits window area in a wall 3–5 ft from a lot
   line — treat the north wall as **blank**. This is a gift, not a problem:
   every apartment needs one blank wall for the stair, bath, kitchen run,
   and closets. Put all of them there and you lose nothing.
3. **Light and view: south + east.** South face looks over the low shed and
   gets all-day sun; east faces your yard and the back of the main house
   (morning sun, and the "who's home" sightline). West = alley, fine for
   secondary windows. So **living spaces want the SE corner**.
4. **The garage door is on the west (alley) face, below.** Whatever room is
   above it hears it. A bedroom there wants a quiet side-mount opener.
5. **≤ 20 ft total height** (R-5 accessory cap) means the upper floor will
   likely have a low-ish plate or some sloped ceiling. Put low-headroom
   zones over things that don't need standing height at the edges: the bed,
   the tub, closets — not the kitchen counter.

## The three decisions that ARE the layout

Iterating a plan this small is really just re-answering three questions.

**Decision 1 — stair inside or outside?** This is the big one: a straight
interior stair costs ~46 sf on *each* floor (a 3'×13' slot plus landing).
Inside (A/B): one weather-tight entry, feels like a house, easier
aging-in-place; costs you a chunk of the garage and the apartment.
Outside (C): the apartment keeps all 437 sf and the garage stays a clean
23'×19' shop, and the two units are fully independent (matters if you ever
rent either one) — but you carry groceries up in the rain and the stair
adds bulk to the yard facade. If inside, the stair goes on the north wall,
full stop — it's the only room-sized thing that never needs a window.

**Decision 2 — where's the wet core?** Bath + laundry + kitchen want to
share plumbing drops, and the drops land in the garage (easy to box out —
another reason this is cheap to get right). All three schemes stack one
**NW bath (6'-4" × 5'-8" with shower + stacked W/D)** over a garage
mech/workbench corner. Kitchen then sits as close as it can: on the stair
wall (A), the west wall (B), or the blank north wall (C — the best answer
*if* the stair isn't there).

**Decision 3 — bedroom west or east?** Whoever gets east gets the morning
sun and the yard; the other room gets the alley side. A gives the yard to
the sofa and dining table (where you spend waking hours — the conventional
answer). B gives it to the bed (quieter, not over the garage door, and the
wardrobe band buffers stair noise — the better answer if you're
noise-sensitive or a morning person). There is no free lunch; pick whose
daylight matters more.

## Sanity numbers to check every iteration against

- Bedroom: ≥ 70 sf, no dimension under 7' (IRC R304); needs an egress
  window (≥ 5.7 sf clear opening, R310) — fine on the west or south.
- Queen bed = 5'-0" × 6'-8"; want ~2' walkway on each open side. A 9'-8"
  wide bedroom holds a queen + nightstands with room to spare.
- Stair: 3'-0" wide min; Virginia allows 8¼" risers / 9" treads, so a
  ~9'-6" floor-to-floor needs ~14 risers ≈ 10'-4" of run + a 3' landing.
- Kitchen: 36" aisle min (42" nicer); a 10' run + short return comfortably
  holds fridge / sink / range / dishwasher.
- Bath: 36" × 36" shower, 30" width at the toilet, ~22" clear in front of
  the vanity. The 36 sf bath here is tight-but-normal ADU scale.
- Ceilings: habitable rooms want 7'-0"+ (sloped-ceiling allowances exist,
  R305) — this is where the 20 ft height cap bites; resolve it with the
  architect early.

*(Code cites are Virginia Residential Code / IRC as research pointers, not
legal advice — confirm with Richmond building review.)*

## How to iterate

1. Look at a sheet and argue with it ("dining should be by the south
   window", "swap the sofa and table"). Every wall, door, window and piece
   of furniture is a couple of lines in `generate_floorplans.py` —
   coordinates are in feet from the SW corner, X east, Y north.
2. Edit, re-run, re-look. The furniture is the test: if the queen bed,
   sofa, and a 4-seat table don't fit with walkways, the scheme fails no
   matter how nice the diagram looks.
3. When a favorite emerges, that sheet plus `plan/site-plan.dxf` is exactly
   what to hand the architect — they'll redo it properly, but you'll be
   arguing about *your* plan instead of their first guess.

Open questions to resolve next: floor-to-floor height vs the 20 ft cap
(drives stair length and ceiling slopes); mini-split head locations;
whether the flex/office corner of the garage gets conditioned from day one.
