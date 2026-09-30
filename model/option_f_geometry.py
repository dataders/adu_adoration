"""Shared Option F revision 2 design geometry. Feet; SW origin, X east, Y north, Z up.

Schematic owner study. This contract coordinates drawings and visualizations;
it is not an assertion of permit, structural, or finished-headroom compliance.
"""

DESIGN = "Option F · revision 2"
VERSION = "2026-09-30-option-f-basis-v2"
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
ROOF_PITCH = (RIDGE_HEIGHT - EAVE_HEIGHT) / (BUILDING_DEPTH / 2)
# Provisional vertical allowance, not a selected roof assembly.
ROOF_INTERIOR_ALLOWANCE = 0.85
PATIO_DEPTH = 4.0
PATIO_NORTH = 19.5
STAIR_WEST = 0.5
STAIR_EAST = 11.5
LANDING_EAST = BUILDING_WIDTH + PATIO_DEPTH
STAIR_SOUTH = -4.0
STAIR_RISERS = 14
STAIR_TREADS = 13
GUARD_HEIGHT = 3.0

# Offset along wall, width, sill above floor, height. No north openings.
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
    "L1 protected hall": (0.5, 11.83, 13.5, 3.25),
    "L1 powder room": (0.5, 15.41, 7.0, 4.09),
    "L1 garage support": (7.83, 15.41, 6.17, 4.09),
    "L1 owner office/garden room": (14.33, 11.83, 9.17, 7.67),
    "L2 bedroom": (0.5, 0.5, 9.7, 9.5),
    "L2 bedroom closet": (0.5, 10.33, 7.0, 3.17),
    "L2 stacked bath": (0.5, 13.83, 7.0, 5.67),
    "L2 laundry cupboard": (8.0, 16.7, 2.6, 2.6),
    "L2 open living/kitchen/dining": (10.53, 0.5, 12.97, 19.0),
}
# axis, fixed wall coordinate, along-wall start/end, (door offset,width,height).
# Interior door apertures are actual cuts in every exported wall.
PARTITIONS = {
    "Level 1": [
        ("Garage separation", "x", 11.5, 0.5, 23.5, ((10.5, 3.0, 6.667),)),
        (
            "Powder and support south",
            "x",
            15.08,
            0.5,
            14.0,
            ((3.5, 2.5, 6.667), (10.5, 2.5, 6.667)),
        ),
        ("Powder east", "y", 7.5, 15.41, 19.5, ()),
        ("Garden room west", "y", 14.0, 11.83, 19.5, ((11.95, 2.8, 6.667),)),
    ],
    "Level 2": [
        ("Bedroom east", "y", 10.2, 0.5, 10.0, ((7.1, 2.4, 6.667),)),
        ("Bedroom north", "x", 10.0, 0.5, 10.53, ((1.0, 5.5, 6.667),)),
        ("Closet east", "y", 7.5, 10.33, 13.5, ()),
        ("Bath south", "x", 13.5, 0.5, 7.83, ()),
        ("Bath east", "y", 7.5, 13.83, 19.5, ((14.0, 2.5, 6.667),)),
        ("Laundry east", "y", 10.83, 16.3, 19.5, ()),
    ],
}
# name, level, type, x,y,width,depth,height; consumed by drawings and furnishing model.
FURNITURE = [
    ("Queen bed", 2, "bed", 0.9, 1.2, 6.667, 5.0, 1.7),
    ("Nightstand", 2, "wood", 0.9, 6.45, 1.4, 1.3, 1.7),
    ("Dresser", 2, "wood", 8.0, 0.85, 2.0, 1.5, 2.7),
    ("Kitchen peninsula", 2, "cabinet", 15.0, 8.5, 8.5, 2.5, 3.0),
    ("East kitchen", 2, "cabinet", 21.0, 11.0, 2.5, 3.0, 3.0),
    ("Refrigerator", 2, "appliance", 21.0, 14.0, 2.5, 2.6, 6.5),
    ("Dining bench", 2, "bench", 14.8, 18.0, 4.7, 1.5, 1.5),
    ("Dining table", 2, "table", 15.0, 15.8, 4.0, 2.5, 2.5),
    ("Dining chair 1", 2, "chair", 15.2, 14.3, 1.4, 1.3, 2.7),
    ("Dining chair 2", 2, "chair", 17.3, 14.3, 1.4, 1.3, 2.7),
    ("Sofa facing west", 2, "sofa", 17.8, 1.5, 2.5, 6.0, 2.6),
    ("Coffee table", 2, "table", 14.5, 3.7, 2.0, 3.0, 1.35),
    ("Shower", 2, "shower", 0.7, 14.1, 3.0, 3.0, 0.15),
    ("Bath vanity", 2, "vanity", 4.4, 17.4, 2.6, 1.7, 2.7),
    ("Upper toilet", 2, "toilet", 5.1, 15.3, 1.4, 2.2, 1.5),
    ("Washer dryer", 2, "laundry", 8.0, 16.7, 2.6, 2.6, 6.2),
    ("Powder vanity", 1, "vanity", 0.8, 17.5, 2.5, 1.6, 2.7),
    ("Lower toilet", 1, "toilet", 5.1, 16.4, 1.4, 2.2, 1.5),
    ("Heat pump water heater", 1, "appliance", 8.1, 17.1, 2.0, 2.0, 5.4),
    ("Garage storage", 1, "wood", 11.0, 18.0, 2.5, 1.3, 5.5),
    ("Garden desk", 1, "table", 15.0, 17.5, 5.0, 1.8, 2.5),
    ("Garden bench", 1, "bench", 17.3, 11.95, 5.8, 2.0, 1.5),
]
CLEARANCES = {
    "lower_hall": 3.25,
    "entry_to_kitchen": 15.0 - 10.53,
    "living_slider_route": 23.5 - 20.3,
    "dining_chair_to_counter": 14.3 - 11.0,
}


def ceiling_height(y):
    """Illustrative finished height with provisional roof allowance (feet)."""
    return EAVE_HEIGHT + ROOF_PITCH * min(y, 20 - y) - UPPER_SUBFLOOR_TOP - ROOF_INTERIOR_ALLOWANCE
