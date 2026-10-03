"""Build coordinated CAD, glTF and render scene from option_f_geometry.py.

Run with uv run --group architecture python model/generate_option_f_model.py.
The same parts feed the browser and Blender. Feet/Z-up in source and OBJ;
standard metres/Y-up in glTF. STEP uses millimetres.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import option_f_geometry as g
import trimesh
from OCP.BRep import BRep_Builder  # ty: ignore[unresolved-import]

# Single lines let ty suppress both absent optional modules and incomplete native stubs.
# isort: off
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace  # ty: ignore[unresolved-import]
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon  # ty: ignore[unresolved-import]
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform  # ty: ignore[unresolved-import]
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox  # ty: ignore[unresolved-import]
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism  # ty: ignore[unresolved-import]

# isort: on
from OCP.BRepTools import BRepTools  # ty: ignore[unresolved-import]
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec  # ty: ignore[unresolved-import]
from OCP.IFSelect import IFSelect_RetDone  # ty: ignore[unresolved-import]
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer  # ty: ignore[unresolved-import]
from OCP.TopoDS import TopoDS_Compound  # ty: ignore[unresolved-import]
from trimesh.visual import ColorVisuals

OUT = Path(__file__).resolve().parent
FT = 304.8
WALL = (153, 163, 139, 255)
INNER = (234, 229, 215, 255)
SLAB = (189, 183, 171, 255)
ROOF = (62, 70, 68, 255)
DECK = (166, 132, 94, 255)
TRIM = (236, 229, 209, 255)
GLASS = (152, 185, 188, 95)
DOOR = (130, 75, 57, 255)
WOOD = (186, 143, 93, 255)
FABRIC = (215, 204, 180, 255)
METAL = (85, 92, 88, 255)
ZONE = (150, 170, 185, 30)


@dataclass(frozen=True)
class Part:
    name: str
    category: str
    level: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    color: tuple[int, int, int, int]
    rotate_x: float = 0.0
    shape: str = "box"


parts: list[Part] = []


def add(name, category, level, x, y, z, dx, dy, dz, color, rotate_x=0.0, shape="box"):
    if min(dx, dy, dz) <= 0:
        raise ValueError(f"Non-positive component: {name}")
    parts.append(
        Part(
            name,
            category,
            level,
            (x + dx / 2, y + dy / 2, z + dz / 2),
            (dx, dy, dz),
            color,
            rotate_x,
            shape,
        )
    )


def wall(name, category, level, axis, fixed, start, end, z, height, openings, thickness, color):
    """Segment a wall around actual apertures; offset,width,sill,height."""

    def block(suffix, offset, width, bottom, tall):
        if axis == "x":
            add(
                name + suffix, category, level, offset, fixed, bottom, width, thickness, tall, color
            )
        else:
            add(
                name + suffix, category, level, fixed, offset, bottom, thickness, width, tall, color
            )

    cursor = start
    for i, (offset, width, sill, h) in enumerate(sorted(openings)):
        if offset > cursor:
            block(f" pier {i}", cursor, offset - cursor, z, height)
        if sill:
            block(f" sill {i}", offset, width, z, sill)
        if sill + h < height:
            block(f" header {i}", offset, width, z + sill + h, height - sill - h)
        cursor = offset + width
    if end > cursor:
        block(" end", cursor, end - cursor, z, height)


def opening(name, level, side, offset, width, sill, height, kind="window"):
    z = (g.UPPER_SUBFLOOR_TOP if level == "Level 2" else g.GROUND_SLAB_TOP) + sill
    axis = "x" if side in ("south", "north") else "y"
    fixed = {"south": 0.12, "north": 19.8, "west": 0.12, "east": 23.8}[side]

    def element(suffix, a, b, w, h, material, category="Trim", depth=0.12):
        if axis == "x":
            add(name + suffix, category, level, a, fixed, b, w, depth, h, material)
        else:
            add(name + suffix, category, level, fixed, a, b, depth, w, h, material)

    category = "Door" if kind in ("entry", "garage") else "Window"
    color = DOOR if kind == "entry" else TRIM if kind == "garage" else GLASS
    element("", offset, z, width, height, color, category, 0.07)
    for a in (offset, offset + width - 0.1):
        element(" jamb " + str(a), a, z, 0.1, height, TRIM)
    for b in (z, z + height - 0.12):
        element(" rail " + str(b), offset, b, width, 0.12, TRIM)
    if kind in ("slider", "window", "garage"):
        element(
            " center mullion",
            offset + width / 2 - 0.04,
            z,
            0.08,
            height,
            DOOR if kind != "garage" else TRIM,
        )
    if kind == "window":
        element(" transom", offset, z + height * 0.65, width, 0.06, DOOR)
    if kind == "garage":
        for i in range(1, 4):
            element(f" panel rail {i}", offset, z + i * height / 4, width, 0.045, WOOD)
        for i in range(4):
            element(
                f" glazed light {i}",
                offset + 0.4 + i * 2.3,
                z + height - 1.3,
                1.8,
                0.8,
                GLASS,
                "Window",
            )
    if kind == "entry":
        element(" glazed light", offset + 0.35, z + 3.9, width - 0.7, 2.25, GLASS, "Window")


def furnishing(name, level, kind, x, y, dx, dy, h):
    lev = f"Level {level}"
    z = g.UPPER_SUBFLOOR_TOP if level == 2 else g.GROUND_SLAB_TOP

    def piece(suffix, a, b, c, w, d, t, col):
        add(name + suffix, "Furniture", lev, a, b, c, w, d, t, col)

    if kind in ("table", "chair"):
        top = h - 0.14 if kind == "table" else 1.5
        piece(" top", x, y, z + top, dx, dy, 0.14, WOOD)
        for a in (x + 0.12, x + dx - 0.25):
            for b in (y + 0.12, y + dy - 0.25):
                piece(f" leg {a} {b}", a, b, z, 0.12, 0.12, top, WOOD)
        if kind == "chair":
            piece(" back", x, y, z + 1.5, dx, 0.12, 1.2, WOOD)
    elif kind == "sofa":
        piece(" base", x, y, z + 0.22, dx, dy, 0.43, FABRIC)
        piece(" back", x + dx - 0.35, y, z + 0.65, 0.35, dy, h - 0.65, FABRIC)
        for b in (y, y + dy - 0.3):
            piece(" arm " + str(b), x, b, z + 0.65, dx - 0.35, 0.3, 1.25, FABRIC)
        for i in range(3):
            piece(
                " cushion " + str(i),
                x + 0.08,
                y + 0.35 + i * (dy - 0.7) / 3,
                z + 0.87,
                dx - 0.5,
                (dy - 0.8) / 3,
                0.5,
                FABRIC,
            )
    elif kind == "bed":
        piece(" base", x + 0.16, y, z + 0.15, dx - 0.16, dy, 0.65, WOOD)
        piece(" mattress", x + 0.05, y + 0.05, z + 0.8, dx - 0.1, dy - 0.1, 0.8, FABRIC)
        piece(
            " duvet", x + 1.7, y + 0.03, z + 1.6, dx - 1.75, dy - 0.06, 0.12, (159, 174, 151, 255)
        )
        for b in (y + 0.3, y + dy / 2 + 0.1):
            piece(" pillow " + str(b), x + 0.15, b, z + 1.6, 1.3, 2, 0.2, TRIM)
        piece(" headboard", x, y, z, 0.16, dy, 3, WOOD)
    elif kind in ("cabinet", "vanity"):
        piece(" base", x, y, z, dx, dy, h - 0.12, WALL if kind == "cabinet" else WOOD)
        piece(" stone top", x - 0.025, y - 0.025, z + h - 0.12, dx + 0.05, dy + 0.05, 0.12, TRIM)
        n = max(1, round(dx / 2))
        for i in range(1, n):
            piece(
                " front joint " + str(i),
                x + i * dx / n,
                y - 0.006,
                z + 0.18,
                0.014,
                0.015,
                h - 0.4,
                METAL,
            )
    elif kind == "bench":
        piece(" frame", x, y, z, dx, dy, h - 0.15, WOOD)
        piece(" cushion", x, y, z + h - 0.15, dx, dy, 0.2, FABRIC)
    elif kind == "laundry":
        piece(" cabinet", x, y, z, dx, dy, h, TRIM)
        for i in range(2):
            piece(
                " appliance face " + str(i),
                x + 0.18,
                y - 0.03,
                z + 0.5 + i * 2.8,
                dx - 0.36,
                0.05,
                2.1,
                METAL,
            )
    elif kind == "toilet":
        piece(" bowl", x + 0.15, y, z, 0.9, 1.6, 1.2, TRIM)
        piece(" tank", x, y + dy - 0.5, z, dx, 0.5, 2.3, TRIM)
    elif kind == "shower":
        piece(" tray", x, y, z, dx, dy, 0.12, TRIM)
        piece(" glass", x + dx - 0.04, y, z + 0.12, 0.04, dy, 6.2, GLASS)
    else:
        piece("", x, y, z, dx, dy, h, TRIM if kind == "appliance" else WOOD)


def guard(name, x0, y0, x1, y1, z):
    length = math.hypot(x1 - x0, y1 - y0)
    n = math.ceil(length / 0.42)
    along_x = abs(x1 - x0) > abs(y1 - y0)
    for i in range(n + 1):
        t = i / n
        add(
            f"{name} baluster {i}",
            "Guard",
            "Exterior",
            x0 + (x1 - x0) * t - 0.035,
            y0 + (y1 - y0) * t - 0.035,
            z + 0.12,
            0.07,
            0.07,
            2.78,
            TRIM,
        )
    for h in (0.12, 2.9):
        add(
            f"{name} rail {h}",
            "Guard",
            "Exterior",
            min(x0, x1) - 0.06,
            min(y0, y1) - 0.06,
            z + h,
            abs(x1 - x0) + 0.12 if along_x else 0.12,
            0.12 if along_x else abs(y1 - y0) + 0.12,
            0.1,
            TRIM,
        )


def build():
    parts.clear()
    add("Level 1 slab 20x24", "Floor slab", "Level 1", 0, 0, 0, 24, 20, 0.5, SLAB)
    add(
        "Level 2 floor assembly 20x24",
        "Floor slab",
        "Level 2",
        0,
        0,
        g.UPPER_FLOOR_BOTTOM,
        24,
        20,
        0.75,
        WOOD,
    )
    for level, z, h in ((1, 0.5, 8), (2, 9.25, 6.75)):
        lev = f"Level {level}"
        for side, axis, fixed, end in (
            ("south", "x", 0, 24),
            ("north", "x", 19.5, 24),
            ("west", "y", 0, 20),
            ("east", "y", 23.5, 20),
        ):
            wall(
                f"L{level} {side} wall",
                "Exterior wall",
                lev,
                axis,
                fixed,
                0.5 if axis == "y" else 0,
                end - 0.5 if axis == "y" else end,
                z,
                h,
                g.OPENINGS[f"l{level}_{side}"],
                0.5,
                WALL,
            )
        for name, axis, fixed, start, end, doors in g.PARTITIONS[lev]:
            wall(
                name,
                "Interior wall",
                lev,
                axis,
                fixed,
                start,
                end,
                z,
                h,
                [(a, w, 0, dh) for a, w, dh in doors],
                0.33,
                INNER,
            )
    # Gable ends are actual triangular prisms, not missing wall above the plate.
    for x, side in ((0, "west"), (23.5, "east")):
        add(
            f"{side} gable wall",
            "Exterior wall",
            "Roof",
            x,
            0,
            16,
            0.5,
            20,
            g.RIDGE_HEIGHT - 16,
            WALL,
            shape="gable",
        )
    opening("Garage overhead door", "Level 1", "west", *g.OPENINGS["l1_west"][0], kind="garage")
    opening("L1 east shop window", "Level 1", "east", *g.OPENINGS["l1_east"][0])
    opening("L1 east 6ft slider", "Level 1", "east", *g.OPENINGS["l1_east"][1], kind="slider")
    opening("L2 south entry door", "Level 2", "south", *g.OPENINGS["l2_south"][0], kind="entry")
    opening("L2 south living window", "Level 2", "south", *g.OPENINGS["l2_south"][1])
    opening("L2 west bedroom EERO window", "Level 2", "west", *g.OPENINGS["l2_west"][0])
    opening("L2 east 6ft slider", "Level 2", "east", *g.OPENINGS["l2_east"][0], kind="slider")
    opening("L2 east dining window", "Level 2", "east", *g.OPENINGS["l2_east"][1])
    for name, x, y, dx, dy in (("south", 11.5, -4, 16.5, 4), ("east", 24, 0, 4, 19.5)):
        add(
            "Ground " + ("south covered patio" if name == "south" else "east patio 4ft"),
            "Patio",
            "Level 1",
            x,
            y,
            0,
            dx,
            dy,
            0.5,
            SLAB,
        )
        add(
            "Upper " + ("south landing" if name == "south" else "east patio 4ft"),
            "Deck",
            "Level 2",
            x,
            y,
            8.95,
            dx,
            dy,
            0.3,
            DECK,
        )
    # Landing top now aligns to upper finished datum; no 4.2-inch extra step.
    add("South stair ground landing", "Patio", "Level 1", 0.5, -4, 0, 11, 4, 0.5, SLAB)
    stair_rise = (g.UPPER_SUBFLOOR_TOP - g.GROUND_SLAB_TOP) / 14
    for i in range(13):
        x = 0.5 + i * 11 / 13
        add(
            f"Stair tread {i + 1}",
            "Exterior stair",
            "Exterior",
            x,
            -4,
            0.5 + (i + 1) * stair_rise - 0.13,
            11 / 13,
            4,
            0.13,
            DECK,
        )
    for y in (-3.82, -0.18):
        for i in range(14):
            x = 0.5 + i * 11 / 13
            z = min(0.5 + (i + 1) * stair_rise, 9.25)
            add(
                f"Stair baluster {y} {i}",
                "Guard",
                "Exterior",
                x - 0.04,
                y - 0.04,
                z,
                0.08,
                0.08,
                2.9,
                TRIM,
            )
        # Segment the slope into short horizontal increments; handrail slope rendered as mesh.
        # rotation about Y would be needed for an X-running rail: custom shape handled below.
        add(
            f"Stair handrail {y}",
            "Guard",
            "Exterior",
            0.45,
            y - 0.06,
            0.5 + stair_rise + 2.9,
            11.1,
            0.12,
            8.75 - stair_rise + 0.12,
            TRIM,
            shape="stairrail",
        )
    for x, y in (
        (11.7, -3.8),
        (19.5, -3.8),
        (27.75, -3.8),
        (27.75, 6),
        (27.75, 13),
        (27.75, 19.25),
    ):
        add(
            f"Patio post {x} {y}",
            "Post",
            "Exterior",
            x - 0.14,
            y - 0.14,
            0.5,
            0.28,
            0.28,
            11.75,
            TRIM,
        )
    guard("South landing", 11.7, -3.8, 27.75, -3.8, 9.25)
    guard("East balcony", 27.75, -3.8, 27.75, 19.25, 9.25)
    guard("North balcony return", 24.15, 19.25, 27.75, 19.25, 9.25)
    # Thin roof planes entirely below maximum ridge, with no north/west overhang.
    rise = g.RIDGE_HEIGHT - g.EAVE_HEIGHT
    slope = math.hypot(10, rise)
    angle = math.atan2(rise, 10)
    t = 0.22
    for name, cy, rot in (
        ("South roof plane flush west", 5, angle),
        ("North roof plane flush north-west", 15, -angle),
    ):
        cz = (g.EAVE_HEIGHT + g.RIDGE_HEIGHT) / 2 - t / 2 * math.cos(angle)
        cy += t / 2 * math.sin(angle) if rot > 0 else -t / 2 * math.sin(angle)
        add(name, "Roof", "Roof", 0, cy - slope / 2, cz - t / 2, 24, slope, t, ROOF, rot)
    for name, (x, y, dx, dy) in g.ROOMS.items():
        add(
            name,
            "Room zone",
            name[:2],
            x,
            y,
            9.255 if name.startswith("L2") else 0.505,
            dx,
            dy,
            0.005,
            ZONE,
        )
    for name, level, kind, x, y, dx, dy, h in g.FURNITURE:
        furnishing(name, level, kind, x, y, dx, dy, h)
    add("Living rug", "Furniture", "Level 2", 13.7, 2.4, 9.26, 7.4, 5.2, 0.025, FABRIC)
    add("Wall mounted television", "Furniture", "Level 2", 10.54, 3.2, 12.0, 0.07, 3.5, 2, METAL)
    add("Kitchen sink", "Furniture", "Level 2", 16.0, 9.0, 12.24, 2, 1.5, 0.045, METAL)
    add("Induction hob", "Furniture", "Level 2", 21.05, 11.3, 12.26, 2.35, 2.3, 0.045, METAL)
    add(
        "Vehicle envelope 16x6", "Vehicle", "Level 1", 3, 2.5, 0.7, 16, 6, 2.9, (178, 184, 172, 255)
    )
    add("Vehicle cabin", "Vehicle", "Level 1", 7, 2.8, 3.6, 7, 5.4, 1.6, (129, 147, 147, 255))


def mesh_for(part):
    dx, dy, dz = part.size
    if part.shape == "gable":
        vertices = [
            [-dx / 2, -dy / 2, -dz / 2],
            [-dx / 2, dy / 2, -dz / 2],
            [-dx / 2, 0, dz / 2],
            [dx / 2, -dy / 2, -dz / 2],
            [dx / 2, dy / 2, -dz / 2],
            [dx / 2, 0, dz / 2],
        ]
        faces = [
            [0, 2, 1],
            [3, 4, 5],
            [0, 1, 4],
            [0, 4, 3],
            [1, 2, 5],
            [1, 5, 4],
            [2, 0, 3],
            [2, 3, 5],
        ]
        mesh = trimesh.Trimesh(vertices, faces, process=True)
    elif part.shape == "stairrail":
        length = math.hypot(dx, dz - 0.12)
        mesh = trimesh.creation.box(extents=(length, dy, 0.12))
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(-math.atan2(dz - 0.12, dx), [0, 1, 0])
        )
    else:
        mesh = trimesh.creation.box(extents=part.size)
    mesh.visual = ColorVisuals(
        mesh=mesh,
        vertex_colors=np.tile(np.array(part.color, dtype=np.uint8), (len(mesh.vertices), 1)),
    )
    transform = np.eye(4)
    if part.rotate_x:
        transform = trimesh.transformations.rotation_matrix(part.rotate_x, [1, 0, 0])
    transform[:3, 3] = part.center
    mesh.apply_transform(transform)
    return mesh


def ocp_shape(part):
    dx, dy, dz = (v * FT for v in part.size)
    cx, cy, cz = (v * FT for v in part.center)
    if part.shape == "gable":
        polygon = BRepBuilderAPI_MakePolygon()
        for point in (
            (-dx / 2, -dy / 2, -dz / 2),
            (-dx / 2, dy / 2, -dz / 2),
            (-dx / 2, 0, dz / 2),
        ):
            polygon.Add(gp_Pnt(*point))
        polygon.Close()
        face = BRepBuilderAPI_MakeFace(polygon.Wire()).Face()
        shape = BRepPrimAPI_MakePrism(face, gp_Vec(dx, 0, 0)).Shape()
    elif part.shape == "stairrail":
        length = math.hypot(dx, dz - 0.12 * FT)
        shape = BRepPrimAPI_MakeBox(
            gp_Pnt(-length / 2, -dy / 2, -0.06 * FT), length, dy, 0.12 * FT
        ).Shape()
        rot = gp_Trsf()
        rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), -math.atan2(dz - 0.12 * FT, dx))
        shape = BRepBuilderAPI_Transform(shape, rot, True).Shape()
    else:
        shape = BRepPrimAPI_MakeBox(gp_Pnt(-dx / 2, -dy / 2, -dz / 2), dx, dy, dz).Shape()
    if part.rotate_x:
        rot = gp_Trsf()
        rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), part.rotate_x)
        shape = BRepBuilderAPI_Transform(shape, rot, True).Shape()
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(cx, cy, cz))
    return BRepBuilderAPI_Transform(shape, tr, True).Shape()


def main():
    build()
    scene = trimesh.Scene()
    for part in parts:
        if part.category != "Room zone":
            scene.add_geometry(mesh_for(part), node_name=part.name, geom_name=part.name)
    scene.export(OUT / "adu-option-f.obj")
    gltf_scene = scene.copy()
    transform = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    transform[:3, :3] *= 0.3048
    gltf_scene.apply_transform(transform)
    gltf_scene.export(OUT / "adu-option-f.glb")
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    solid_parts = [p for p in parts if p.category != "Room zone"]
    for part in solid_parts:
        builder.Add(compound, ocp_shape(part))
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    if writer.Write(str(OUT / "adu-option-f.step")) != IFSelect_RetDone:
        raise RuntimeError("STEP export failed")
    if not BRepTools.Write_s(compound, str(OUT / "adu-option-f.brep")):
        raise RuntimeError("BREP export failed")
    payload = {"version": g.VERSION, "units": "feet", "parts": [asdict(p) for p in parts]}
    # Exact triangulated geometry for browser and rendering consumers.
    for item, part in zip(payload["parts"], parts, strict=True):
        mesh = mesh_for(part)
        item["vertices"] = np.round(mesh.vertices, 6).tolist()
        item["faces"] = mesh.faces.tolist()
    (OUT / "adu-option-f-scene.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    bounds = scene.bounds
    manifest = {
        "schema": "adu-option-f-model-manifest-v2",
        "design": g.DESIGN,
        "version": g.VERSION,
        "status": "schematic owner study; not for construction",
        "sources": ["model/option_f_geometry.py"],
        "units": "feet",
        "datums_ft": {"upper_subfloor": 9.25, "eave": 16.0, "ridge": round(g.RIDGE_HEIGHT, 3)},
        "bounds_ft": {"min": bounds[0].round(3).tolist(), "max": bounds[1].round(3).tolist()},
        "object_count": len(solid_parts),
        "clearances_ft": g.CLEARANCES,
        "objects": [
            {
                "name": p.name,
                "category": p.category,
                "level": p.level,
                "center_ft": p.center,
                "size_ft": p.size,
            }
            for p in parts
        ],
    }
    (OUT / "adu-option-f-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported {len(solid_parts)} solids, shared scene, CAD and glTF")


if __name__ == "__main__":
    main()
