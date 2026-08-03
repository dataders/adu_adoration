"""Generate the Option E ADU as an editable FreeCAD model.

Run with FreeCAD's bundled Python runtime, not system Python:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
        model/generate_freecad_adu.py

Coordinates follow apartment/generate_floorplans.py:
origin = southwest exterior corner, X east, Y north, Z up. Source dimensions
are feet; FreeCAD geometry is stored in millimetres.

This is a design-development model, not a construction model. Wall openings,
floor-to-floor height, roof assembly, structural thicknesses, exterior stair,
and code clearances require architect/engineer verification.
"""

from pathlib import Path

import FreeCAD as App  # ty: ignore[unresolved-import]
import Part  # ty: ignore[unresolved-import]

FT = 304.8
IN = 25.4

BW = 24.0
BH = 20.0
EXT = 0.5
INT = 0.33

GROUND_SLAB = 0.5
LEVEL_2 = 9.5
UPPER_FLOOR = 0.75
UPPER_FINISH = LEVEL_2 + UPPER_FLOOR
EAVE = 16.0
RIDGE = 20.0

OUT_DIR = Path(__file__).resolve().parent
FCSTD_PATH = OUT_DIR / "adu-option-e.FCStd"
STEP_PATH = OUT_DIR / "adu-option-e.step"


COLORS = {
    "slab": (0.72, 0.72, 0.70),
    "exterior": (0.74, 0.82, 0.70),
    "interior": (0.92, 0.90, 0.84),
    "roof": (0.28, 0.34, 0.38),
    "glass": (0.35, 0.70, 0.88),
    "door": (0.48, 0.30, 0.17),
    "stair": (0.64, 0.55, 0.42),
    "patio": (0.68, 0.69, 0.65),
    "garage": (0.82, 0.82, 0.78),
    "bath": (0.72, 0.89, 0.82),
    "office": (0.96, 0.86, 0.65),
    "sunroom": (0.96, 0.78, 0.72),
    "bedroom": (0.69, 0.80, 0.94),
    "living": (0.96, 0.74, 0.70),
    "kitchen": (0.96, 0.86, 0.65),
    "storage": (0.80, 0.76, 0.90),
    "cabinet": (0.58, 0.45, 0.31),
    "fixture": (0.92, 0.94, 0.95),
}


def mm(value):
    return value * FT


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(mm(dx), mm(dy), mm(dz), App.Vector(mm(x), mm(y), mm(z)))


def safe_name(label):
    return "".join(c if c.isalnum() else "_" for c in label).strip("_")


def feature(group, label, shape, category, level, color, transparency=0, source="Option E"):
    obj = group.newObject("Part::Feature", safe_name(label))
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Category", "ADU").Category = category
    obj.addProperty("App::PropertyString", "Level", "ADU").Level = level
    obj.addProperty("App::PropertyString", "DesignSource", "ADU").DesignSource = source
    obj.addProperty("App::PropertyColor", "DisplayColor", "ADU").DisplayColor = color
    obj.addProperty(
        "App::PropertyInteger", "DisplayTransparency", "ADU"
    ).DisplayTransparency = transparency
    # ViewObject is unavailable in FreeCADCmd. Retained display properties are
    # applied below when generator runs with GUI support, and remain available
    # for the companion styling macro after a headless build.
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = tuple(max(0.0, c - 0.25) for c in color)
        obj.ViewObject.Transparency = transparency
    return obj


def subtract_openings(shape, axis, origin, z, thickness, openings):
    """Cut openings from a horizontal (x) or vertical (y) wall.

    opening = (offset along wall, width, sill, height), all in feet.
    """
    ox, oy = origin
    for offset, width, sill, height in openings:
        if axis == "x":
            cutter = box(ox + offset, oy - 0.05, z + sill, width, thickness + 0.1, height)
        else:
            cutter = box(ox - 0.05, oy + offset, z + sill, thickness + 0.1, width, height)
        shape = shape.cut(cutter)
    return shape


def wall_x(group, label, x, y, length, thickness, z, height, openings=(), exterior=False, level=""):
    shape = box(x, y, z, length, thickness, height)
    shape = subtract_openings(shape, "x", (x, y), z, thickness, openings)
    return feature(
        group,
        label,
        shape,
        "Exterior wall" if exterior else "Interior wall",
        level,
        COLORS["exterior" if exterior else "interior"],
    )


def wall_y(group, label, x, y, length, thickness, z, height, openings=(), exterior=False, level=""):
    shape = box(x, y, z, thickness, length, height)
    shape = subtract_openings(shape, "y", (x, y), z, thickness, openings)
    return feature(
        group,
        label,
        shape,
        "Exterior wall" if exterior else "Interior wall",
        level,
        COLORS["exterior" if exterior else "interior"],
    )


def insert_x(group, label, x, y, z, width, height, kind, level, thickness=EXT):
    depth = 1.5 * IN / FT
    shape = box(x, y + (thickness - depth) / 2, z, width, depth, height)
    return feature(
        group,
        label,
        shape,
        "Window" if kind == "glass" else "Door",
        level,
        COLORS[kind],
        55 if kind == "glass" else 10,
    )


def insert_y(group, label, x, y, z, width, height, kind, level, thickness=EXT):
    depth = 1.5 * IN / FT
    shape = box(x + (thickness - depth) / 2, y, z, depth, width, height)
    return feature(
        group,
        label,
        shape,
        "Window" if kind == "glass" else "Door",
        level,
        COLORS[kind],
        55 if kind == "glass" else 10,
    )


def room(group, label, x, y, z, dx, dy, color_key, level):
    obj = feature(
        group, label, box(x, y, z, dx, dy, 0.04), "Room zone", level, COLORS[color_key], 58
    )
    obj.addProperty("App::PropertyArea", "ApproxArea", "ADU")
    obj.ApproxArea = f"{dx * dy * 0.092903:.3f} m^2"
    obj.addProperty(
        "App::PropertyString", "PlanDimensions", "ADU"
    ).PlanDimensions = f"{dx:g} ft x {dy:g} ft"
    return obj


def build_shell(doc, level1, level2):
    feature(
        level1,
        "Level 1 slab 20x24",
        box(0, 0, 0, BW, BH, GROUND_SLAB),
        "Floor slab",
        "Level 1",
        COLORS["slab"],
    )
    feature(
        level2,
        "Level 2 floor assembly 20x24",
        box(0, 0, LEVEL_2, BW, BH, UPPER_FLOOR),
        "Floor slab",
        "Level 2",
        COLORS["slab"],
    )

    lower_z = GROUND_SLAB
    lower_h = LEVEL_2 - GROUND_SLAB
    wall_x(
        level1,
        "L1 south exterior wall",
        0,
        0,
        BW,
        EXT,
        lower_z,
        lower_h,
        exterior=True,
        level="Level 1",
    )
    wall_x(
        level1,
        "L1 north exterior wall",
        0,
        BH - EXT,
        BW,
        EXT,
        lower_z,
        lower_h,
        exterior=True,
        level="Level 1",
    )
    wall_y(
        level1,
        "L1 west exterior wall with garage door",
        0,
        0,
        BH,
        EXT,
        lower_z,
        lower_h,
        openings=[(2.2, 9.7, 0.0, 7.5)],
        exterior=True,
        level="Level 1",
    )
    wall_y(
        level1,
        "L1 east exterior wall",
        BW - EXT,
        0,
        BH,
        EXT,
        lower_z,
        lower_h,
        openings=[(3.2, 2.5, 3.0, 3.5), (8.1, 4.0, 0.0, 7.0), (15.8, 2.5, 0.0, 6.8)],
        exterior=True,
        level="Level 1",
    )

    upper_z = UPPER_FINISH
    upper_h = EAVE - UPPER_FINISH
    wall_x(
        level2,
        "L2 south exterior wall",
        0,
        0,
        BW,
        EXT,
        upper_z,
        upper_h,
        openings=[(15.0, 2.5, 2.4, 2.5)],
        exterior=True,
        level="Level 2",
    )
    wall_x(
        level2,
        "L2 north blank exterior wall",
        0,
        BH - EXT,
        BW,
        EXT,
        upper_z,
        upper_h,
        exterior=True,
        level="Level 2",
    )
    wall_y(
        level2,
        "L2 west exterior wall",
        0,
        0,
        BH,
        EXT,
        upper_z,
        upper_h,
        openings=[(3.3, 2.5, 2.3, 3.2), (12.2, 2.0, 2.8, 2.5)],
        exterior=True,
        level="Level 2",
    )
    wall_y(
        level2,
        "L2 east exterior wall",
        BW - EXT,
        0,
        BH,
        EXT,
        upper_z,
        upper_h,
        openings=[(2.0, 5.0, 0.0, 6.3), (9.2, 2.0, 2.4, 2.5)],
        exterior=True,
        level="Level 2",
    )


def build_lower_plan(level1):
    z = GROUND_SLAB
    h = LEVEL_2 - GROUND_SLAB

    wall_y(
        level1,
        "L1 garage to east rooms",
        14.0,
        0.5,
        19.0,
        INT,
        z,
        h,
        [(7.5, 3.0, 0, 7)],
        level="Level 1",
    )
    wall_x(
        level1,
        "L1 bathroom south wall",
        7.5,
        14.0,
        6.5,
        INT,
        z,
        h,
        [(3.3, 2.4, 0, 6.8)],
        level="Level 1",
    )
    wall_y(level1, "L1 bathroom west wall", 7.5, 14.0, 5.5, INT, z, h, level="Level 1")
    wall_x(
        level1,
        "L1 office south wall",
        14.0,
        14.0,
        9.5,
        INT,
        z,
        h,
        [(2.0, 2.6, 0, 6.8)],
        level="Level 1",
    )

    room(
        level1,
        "Garage and storage zone",
        0.55,
        0.55,
        GROUND_SLAB + 0.02,
        13.4,
        13.4,
        "garage",
        "Level 1",
    )
    room(
        level1,
        "Garage north return",
        0.55,
        14.05,
        GROUND_SLAB + 0.02,
        6.9,
        5.4,
        "garage",
        "Level 1",
    )
    room(level1, "Level 1 bathroom", 7.83, 14.33, GROUND_SLAB + 0.02, 5.84, 5.12, "bath", "Level 1")
    room(level1, "Office", 14.33, 14.33, GROUND_SLAB + 0.02, 9.12, 5.12, "office", "Level 1")
    room(level1, "Sunroom", 14.33, 0.55, GROUND_SLAB + 0.02, 9.12, 13.4, "sunroom", "Level 1")

    # Bathroom fixtures and office desk make top/axon views legible.
    feature(
        level1,
        "L1 shower",
        box(7.9, 16.1, GROUND_SLAB, 3.0, 3.0, 0.15),
        "Fixture",
        "Level 1",
        COLORS["fixture"],
    )
    feature(
        level1,
        "L1 vanity",
        box(8.0, 14.35, GROUND_SLAB, 2.4, 1.45, 2.8),
        "Fixture",
        "Level 1",
        COLORS["cabinet"],
    )
    feature(
        level1,
        "Office desk",
        box(15.0, 17.2, GROUND_SLAB, 5.6, 1.6, 2.5),
        "Furniture",
        "Level 1",
        COLORS["cabinet"],
    )

    insert_y(level1, "Garage overhead door", 0, 2.2, GROUND_SLAB, 9.7, 7.5, "door", "Level 1")
    insert_y(
        level1,
        "Sunroom east window",
        BW - EXT,
        3.2,
        GROUND_SLAB + 3.0,
        2.5,
        3.5,
        "glass",
        "Level 1",
    )
    insert_y(
        level1, "Sunroom east slider", BW - EXT, 8.1, GROUND_SLAB, 4.0, 7.0, "glass", "Level 1"
    )
    insert_y(level1, "Office east door", BW - EXT, 15.8, GROUND_SLAB, 2.5, 6.8, "door", "Level 1")


def build_upper_plan(level2):
    z = UPPER_FINISH
    h = EAVE - UPPER_FINISH

    wall_y(
        level2,
        "L2 bedroom east wall",
        10.2,
        0.5,
        9.5,
        INT,
        z,
        h,
        [(6.6, 2.4, 0, 6.8)],
        level="Level 2",
    )
    wall_x(level2, "L2 bedroom north wall", 0.5, 10.0, 10.03, INT, z, h, level="Level 2")
    wall_y(
        level2,
        "L2 bath east wall",
        6.9,
        10.0,
        6.2,
        INT,
        z,
        h,
        [(1.0, 2.4, 0, 6.8)],
        level="Level 2",
    )
    wall_x(level2, "L2 bath storage wall", 0.5, 16.2, 6.73, INT, z, h, level="Level 2")
    wall_x(
        level2,
        "L2 bedroom closet wall",
        0.5,
        8.0,
        6.0,
        INT,
        z,
        h,
        [(0.5, 5.0, 0, 6.8)],
        level="Level 2",
    )
    wall_x(level2, "Low TV wall", 12.0, 7.35, 6.5, 0.35, z, 4.0, level="Level 2")

    room(level2, "Bedroom", 0.55, 0.55, UPPER_FINISH + 0.02, 9.6, 9.4, "bedroom", "Level 2")
    room(
        level2,
        "Bathroom and laundry",
        0.55,
        10.33,
        UPPER_FINISH + 0.02,
        6.3,
        5.82,
        "bath",
        "Level 2",
    )
    room(
        level2,
        "Low eave linen storage",
        0.55,
        16.53,
        UPPER_FINISH + 0.02,
        6.3,
        2.92,
        "storage",
        "Level 2",
    )
    room(
        level2,
        "Open living and dining",
        10.55,
        0.55,
        UPPER_FINISH + 0.02,
        12.9,
        8.1,
        "living",
        "Level 2",
    )
    room(
        level2,
        "Kitchen and dining",
        10.55,
        8.7,
        UPPER_FINISH + 0.02,
        12.9,
        6.8,
        "kitchen",
        "Level 2",
    )

    feature(
        level2,
        "Kitchen ridge island",
        box(12.0, 8.9, UPPER_FINISH, 7.4, 2.2, 3.0),
        "Cabinetry",
        "Level 2",
        COLORS["cabinet"],
    )
    feature(
        level2,
        "East gable appliance run",
        box(21.33, 8.5, UPPER_FINISH, 2.17, 6.6, 3.0),
        "Cabinetry",
        "Level 2",
        COLORS["cabinet"],
    )
    feature(
        level2,
        "Refrigerator",
        box(20.9, 12.2, UPPER_FINISH, 2.5, 2.6, 6.5),
        "Appliance",
        "Level 2",
        (0.72, 0.74, 0.75),
    )
    feature(
        level2,
        "Pantry",
        box(21.45, 9.0, UPPER_FINISH, 1.7, 2.4, 6.5),
        "Cabinetry",
        "Level 2",
        COLORS["cabinet"],
    )
    feature(
        level2,
        "L2 shower",
        box(0.7, 10.4, UPPER_FINISH, 3.0, 3.0, 0.15),
        "Fixture",
        "Level 2",
        COLORS["fixture"],
    )
    feature(
        level2,
        "L2 vanity",
        box(0.7, 13.75, UPPER_FINISH, 2.4, 1.75, 2.8),
        "Fixture",
        "Level 2",
        COLORS["cabinet"],
    )

    insert_x(
        level2, "South living window", 15.0, 0, UPPER_FINISH + 2.4, 2.5, 2.5, "glass", "Level 2"
    )
    insert_y(
        level2, "West bedroom window", 0, 3.3, UPPER_FINISH + 2.3, 2.5, 3.2, "glass", "Level 2"
    )
    insert_y(
        level2, "West bathroom window", 0, 12.2, UPPER_FINISH + 2.8, 2.0, 2.5, "glass", "Level 2"
    )
    insert_y(
        level2,
        "East sliding glass entry",
        BW - EXT,
        2.0,
        UPPER_FINISH,
        5.0,
        6.3,
        "glass",
        "Level 2",
    )
    insert_y(
        level2,
        "East kitchen window",
        BW - EXT,
        9.2,
        UPPER_FINISH + 2.4,
        2.0,
        2.5,
        "glass",
        "Level 2",
    )


def build_exterior_access(exterior):
    # Lower patio and stacked upper balcony at east; covered south landing.
    feature(
        exterior,
        "Ground east patio",
        box(24.0, 0.0, 0, 3.5, 19.5, 0.25),
        "Patio",
        "Level 1",
        COLORS["patio"],
    )
    feature(
        exterior,
        "Ground south covered patio",
        box(11.5, -4.0, 0, 16.0, 4.0, 0.25),
        "Patio",
        "Level 1",
        COLORS["patio"],
    )
    feature(
        exterior,
        "Upper south landing",
        box(11.5, -4.0, LEVEL_2, 16.0, 4.0, 0.35),
        "Landing",
        "Level 2",
        COLORS["stair"],
    )
    feature(
        exterior,
        "Upper east balcony",
        box(24.0, 0.0, LEVEL_2, 3.5, 19.5, 0.35),
        "Balcony",
        "Level 2",
        COLORS["stair"],
    )

    n = 13
    run = 11.0 / n
    rise = LEVEL_2 / n
    for i in range(n):
        shape = box(0.5 + i * run, -4.0, 0, run + 0.03, 4.0, (i + 1) * rise)
        feature(
            exterior,
            f"Exterior stair step {i + 1:02d}",
            shape,
            "Exterior stair",
            "Exterior",
            COLORS["stair"],
        )

    # Simple guard/handrail massing, 42 in above walking surfaces.
    rail_h = 3.5
    post = 0.12
    for x in (11.5, 19.5, 27.38):
        feature(
            exterior,
            f"South landing guard post {x:g}",
            box(x, -4.0, LEVEL_2, post, post, rail_h),
            "Guard",
            "Exterior",
            COLORS["stair"],
        )
    feature(
        exterior,
        "South landing guard rail",
        box(11.5, -4.0, LEVEL_2 + rail_h - 0.12, 16.0, 0.12, 0.12),
        "Guard",
        "Exterior",
        COLORS["stair"],
    )
    feature(
        exterior,
        "East balcony guard rail",
        box(27.38, 0.0, LEVEL_2 + rail_h - 0.12, 0.12, 19.5, 0.12),
        "Guard",
        "Exterior",
        COLORS["stair"],
    )


def build_roof(roof):
    t = 0.35
    south_profile = Part.makePolygon(
        [
            App.Vector(0, mm(0), mm(EAVE)),
            App.Vector(0, mm(10), mm(RIDGE)),
            App.Vector(0, mm(10), mm(RIDGE - t)),
            App.Vector(0, mm(0), mm(EAVE - t)),
            App.Vector(0, mm(0), mm(EAVE)),
        ]
    )
    north_profile = Part.makePolygon(
        [
            App.Vector(0, mm(10), mm(RIDGE)),
            App.Vector(0, mm(20), mm(EAVE)),
            App.Vector(0, mm(20), mm(EAVE - t)),
            App.Vector(0, mm(10), mm(RIDGE - t)),
            App.Vector(0, mm(10), mm(RIDGE)),
        ]
    )
    feature(
        roof,
        "South roof plane",
        Part.Face(south_profile).extrude(App.Vector(mm(BW), 0, 0)),
        "Roof",
        "Roof",
        COLORS["roof"],
    )
    feature(
        roof,
        "North roof plane",
        Part.Face(north_profile).extrude(App.Vector(mm(BW), 0, 0)),
        "Roof",
        "Roof",
        COLORS["roof"],
    )


def add_project_metadata(doc):
    info = doc.addObject("App::FeaturePython", "ProjectInformation")
    info.Label = "ADU Option E - project information"
    fields = {
        "Status": "Design-development model; not for construction",
        "Footprint": "24 ft east-west x 20 ft north-south (480 sf gross)",
        "Level2": "9.5 ft working floor-to-floor assumption",
        "Height": "16 ft eave / 20 ft ridge",
        "CoordinateSystem": "Origin SW; X east; Y north; Z up; internal units mm",
        "PlanSource": "apartment/option-e-primary-design-basis.svg",
        "SiteSource": "plan/site-plan.dxf",
        "Verification": "Architect to verify structure, sections, headroom, stair, egress, fire separation, and zoning",
    }
    for name, value in fields.items():
        info.addProperty("App::PropertyString", name, "Project")
        setattr(info, name, value)


def main():
    if "ADU_Option_E" in App.listDocuments():
        App.closeDocument("ADU_Option_E")
    doc = App.newDocument("ADU_Option_E")
    add_project_metadata(doc)

    level1 = doc.addObject("App::Part", "Level_1")
    level1.Label = "Level 1 - garage / bath / office / sunroom"
    level2 = doc.addObject("App::Part", "Level_2")
    level2.Label = "Level 2 - apartment"
    exterior = doc.addObject("App::Part", "Exterior_Access")
    exterior.Label = "Exterior stair / patios / balcony"
    roof = doc.addObject("App::Part", "Roof")
    roof.Label = "E-W gable roof - section to verify"

    build_shell(doc, level1, level2)
    build_lower_plan(level1)
    build_upper_plan(level2)
    build_exterior_access(exterior)
    build_roof(roof)

    doc.recompute()
    step_objects = [
        obj
        for obj in doc.Objects
        if "Category" in obj.PropertiesList and hasattr(obj, "Shape") and not obj.Shape.isNull()
    ]
    invalid = [obj.Label for obj in step_objects if not obj.Shape.isValid()]
    if invalid:
        raise RuntimeError(f"invalid FreeCAD shapes: {invalid}")
    if len(step_objects) != 72:
        raise RuntimeError(f"expected 72 model objects, found {len(step_objects)}")

    bounds = Part.makeCompound([obj.Shape for obj in step_objects]).BoundBox
    actual_bounds = tuple(
        round(v / FT, 2)
        for v in (bounds.XMin, bounds.YMin, bounds.ZMin, bounds.XMax, bounds.YMax, bounds.ZMax)
    )
    expected_bounds = (0.0, -4.0, 0.0, 27.5, 20.0, 20.0)
    if actual_bounds != expected_bounds:
        raise RuntimeError(f"unexpected model bounds {actual_bounds}; expected {expected_bounds}")

    doc.saveAs(str(FCSTD_PATH))
    Part.export(step_objects, str(STEP_PATH))

    print(f"wrote {FCSTD_PATH}")
    print(f"wrote {STEP_PATH}")
    print(f"objects: {len(doc.Objects)}; solids/surfaces exported: {len(step_objects)}")
    print(
        "bounds_ft: "
        f"{actual_bounds[0]:.2f},{actual_bounds[1]:.2f},{actual_bounds[2]:.2f} to "
        f"{actual_bounds[3]:.2f},{actual_bounds[4]:.2f},{actual_bounds[5]:.2f}"
    )
    App.closeDocument(doc.Name)


if __name__ == "__main__":
    main()
