"""Canonical Option F geometry contract shared by model generators and checks.

Coordinates are feet. Origin is southwest exterior building corner; X east,
Y north, Z up. This is schematic design geometry, not permit geometry.
"""

DESIGN = "Option F"
VERSION = "2026-08-03-option-f-basis-v1"

BUILDING_WIDTH = 24.0
BUILDING_DEPTH = 20.0
EXTERIOR_WALL = 0.5
INTERIOR_WALL = 0.33
GROUND_SLAB_TOP = 0.5
UPPER_SUBFLOOR_TOP = 9.25
UPPER_FLOOR_THICKNESS = 0.75
UPPER_FLOOR_BOTTOM = UPPER_SUBFLOOR_TOP - UPPER_FLOOR_THICKNESS
EAVE_HEIGHT = 16.0
RIDGE_HEIGHT = 19.833333

PATIO_DEPTH = 4.0
PATIO_NORTH = 19.5
STAIR_WEST = 0.5
STAIR_EAST = 11.5
LANDING_EAST = BUILDING_WIDTH + PATIO_DEPTH
STAIR_SOUTH = -4.0
STAIR_RISERS = 14
STAIR_TREADS = 13
GUARD_HEIGHT = 3.0

# (offset along wall, width, sill, height)
OPENINGS = {
    "l1_south": (),
    "l1_north": (),
    "l1_west": ((1.3, 9.7, 0.0, 7.5),),
    "l1_east": ((4.0, 3.0, 3.0, 3.5), (12.3, 6.0, 0.0, 6.667)),
    "l2_south": ((11.5, 3.0, 0.0, 6.667), (16.0, 5.0, 2.3, 3.5)),
    "l2_north": (),
    "l2_west": ((3.0, 3.5, 2.3, 3.5),),
    "l2_east": ((1.5, 6.0, 0.0, 6.667), (15.0, 3.5, 2.3, 3.5)),
}

ROOMS = {
    "L1 garage/shop": (0.5, 0.5, 23.0, 11.0),
    "L1 garage support": (0.5, 11.83, 7.0, 7.67),
    "L1 protected hall": (7.83, 11.83, 6.17, 1.67),
    "L1 powder room": (7.83, 13.83, 6.17, 5.67),
    "L1 owner office/garden room": (14.33, 11.83, 9.17, 7.67),
    "L2 bedroom": (0.5, 0.5, 9.7, 9.5),
    "L2 bedroom closet": (0.5, 10.33, 7.0, 3.17),
    "L2 laundry/seasonal storage": (0.5, 13.83, 7.0, 5.67),
    "L2 stacked bath": (7.83, 13.83, 6.17, 5.67),
    "L2 open living/kitchen/dining": (10.53, 0.5, 12.97, 19.0),
}
