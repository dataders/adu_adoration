# Apartment layout — the 1-bed above the garage

How to plan (and keep iterating) the ~480 sf apartment on level 2 of the
20 × 24 ADU. Five worked schemes live here as full sheets (garage level +
apartment level, furnished, annotated):

| sheet | stair | bedroom | living | headline trade |
|---|---|---|---|---|
| **[`option-e-primary-design-basis`](option-e-primary-design-basis.png)** | **exterior**, south face from alley | west (alley) | center + east | **PRIMARY:** owner's two-level sketch, corrected roof-aware kitchen, programmed lower level |
| [`option-a-living-east`](option-a-living-east.png) | interior, north wall | west (alley) | east + south | living gets the yard view; bedroom sits over the garage door |
| [`option-b-bedroom-east`](option-b-bedroom-east.png) | interior, north wall | east (yard) | center + south | quiet bright bedroom; living loses the yard view |
| [`option-c-exterior-stair`](option-c-exterior-stair.png) | **exterior**, east face | west (alley) | east + south | ~46 sf more apartment *and* garage; you arrive outside |
| [`option-d-south-stair-roof-aware`](option-d-south-stair-roof-aware.png) | **exterior**, south face from alley | west (alley) | center + east | direct alley stair; kitchen moves to full-height gable zone; shed must move |

Regenerate after editing: `uv run python3 apartment/generate_floorplans.py`
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

   **Roof warning:** A–C are plan studies, not section-verified layouts. Current
   massing uses an E–W ridge with 16' eaves and a 20' ridge, so ceiling height
   falls toward the north and south walls. At the working 9'-6" floor-to-floor
   assumption, the roof exterior is only about 6'-6" above the upper floor at
   the eaves before subtracting roof structure and finishes, so a full-height
   refrigerator cannot sit against those walls. Option D responds by moving the tall
   kitchen to the east gable-end wall near the ridge and pulling standing bath
   fixtures into the central high-headroom band. Option E adopts the same roof
   logic while preserving the owner's preferred two-level organization. Final floor/roof section still
   controls; changing roof overhang alone does not create interior headroom.

## Primary design basis — Option E

Option E starts from the [owner's preferred two-level sketch](../images/12-handdrawn-two-level-design-basis.jpg),
not from Option D. It preserves the sketch's core ideas:

- garage left, bathroom north-center, office northeast, sunroom directly below it,
  and an exterior east patio on level 1;
- west bedroom, west bath/laundry, open living room, central TV wall, and balcony on level 2;
- exterior stair beginning at the west alley, rising east along the south wall,
  and reaching an upper east patio stacked directly above the level-1 patio;
- sliding-glass apartment entrance from that upper east patio.

One deliberate correction: kitchen is no longer a tall cabinet run under the sloping north eave.
Refrigerator and pantry move to the full-height east gable wall; sink and range move to an island
beneath the E–W ridge. This is a design basis, not a construction plan. Architect must verify roof
section/headroom, structure, egress, stair geometry, plumbing, fire separation, and whether enclosed
level-1 office/sunroom area changes zoning treatment or the 500 sf ADU living-area calculation.
The sketch's room proportions also leave only about 13'-6" of clear garage depth inside the current
20 × 24 footprint; architect must rebalance garage/sunroom widths or enlarge/reorient the footprint
to fit a typical 16' vehicle.

## The three decisions that ARE the layout

Iterating a plan this small is really just re-answering three questions.

**Decision 1 — stair inside or outside?** This is the big one: a straight
interior stair costs ~46 sf on *each* floor (a 3'×13' slot plus landing).
Inside (A/B): one weather-tight entry, feels like a house, easier
aging-in-place; costs you a chunk of the garage and the apartment.
Outside (C/D/E): the apartment keeps all 437 sf; C leaves the garage open,
while D/E place the stair on the south face and E programs the lower level.
Exterior access means you carry groceries up in the rain, and the stair adds
bulk to the yard facade. If inside, the stair goes on the north wall,
full stop — it's the only room-sized thing that never needs a window.

**Decision 2 — where's the wet core?** Bath + laundry + kitchen want to
share plumbing drops, and the drops land in the garage (easy to box out —
another reason this is cheap to get right). A–C stack one **NW bath
(6'-4" × 5'-8" with shower + stacked W/D)** over a garage mech/workbench
corner. D/E move standing bath fixtures toward the ridge for roof headroom;
E also places a bathroom below. Kitchens vary by scheme, but Option E's
east-gable appliance wall plus ridge-line island is the primary direction.

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
