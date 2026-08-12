"""Generate true-scale Option F neutral CAD and mesh model artifacts.

Run: uv run --group architecture python model/generate_option_f_model.py

Outputs STEP/BREP for CAD exchange and GLB/OBJ for visualization. Source
geometry remains editable here and in option_f_geometry.py. Permit drawings,
structure, assemblies, and code clearances require licensed professionals.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import option_f_geometry as g
import trimesh
from OCP.BRep import BRep_Builder  # ty: ignore[unresolved-import]
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform  # ty: ignore[unresolved-import]
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox  # ty: ignore[unresolved-import]
from OCP.BRepTools import BRepTools  # ty: ignore[unresolved-import]
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec  # ty: ignore[unresolved-import]
from OCP.IFSelect import IFSelect_RetDone  # ty: ignore[unresolved-import]
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer  # ty: ignore[unresolved-import]
from OCP.TopoDS import TopoDS_Compound  # ty: ignore[unresolved-import]
from trimesh.visual import ColorVisuals

OUT = Path(__file__).resolve().parent
FT = 304.8


@dataclass(frozen=True)
class Part:
    name: str
    category: str
    level: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    color: tuple[int, int, int, int]
    rotate_x: float = 0.0


parts: list[Part] = []


def add(name, category, level, x, y, z, dx, dy, dz, color, rotate_x=0.0):
    parts.append(
        Part(
            name,
            category,
            level,
            (x + dx / 2, y + dy / 2, z + dz / 2),
            (dx, dy, dz),
            color,
            rotate_x,
        )
    )


WALL = (154, 171, 142, 255)
INNER = (230, 226, 214, 255)
SLAB = (184, 184, 178, 255)
ROOF = (62, 67, 66, 255)
DECK = (202, 192, 169, 255)
GLASS = (104, 170, 196, 150)
DOOR = (129, 62, 49, 255)
ZONE = (150, 170, 185, 80)


def wall_x(name, level, y, z, height, openings):
    cursor = 0.0
    for index, (offset, width, sill, opening_height) in enumerate(sorted(openings)):
        if offset > cursor:
            add(
                f"{name} segment {index}A",
                "Exterior wall",
                level,
                cursor,
                y,
                z,
                offset - cursor,
                g.EXTERIOR_WALL,
                height,
                WALL,
            )
        if sill > 0:
            add(
                f"{name} sill {index}",
                "Exterior wall",
                level,
                offset,
                y,
                z,
                width,
                g.EXTERIOR_WALL,
                sill,
                WALL,
            )
        top = sill + opening_height
        if top < height:
            add(
                f"{name} header {index}",
                "Exterior wall",
                level,
                offset,
                y,
                z + top,
                width,
                g.EXTERIOR_WALL,
                height - top,
                WALL,
            )
        cursor = offset + width
    if cursor < g.BUILDING_WIDTH:
        add(
            f"{name} final segment",
            "Exterior wall",
            level,
            cursor,
            y,
            z,
            g.BUILDING_WIDTH - cursor,
            g.EXTERIOR_WALL,
            height,
            WALL,
        )


def wall_y(name, level, x, z, height, openings):
    cursor = 0.0
    for index, (offset, width, sill, opening_height) in enumerate(sorted(openings)):
        if offset > cursor:
            add(
                f"{name} segment {index}A",
                "Exterior wall",
                level,
                x,
                cursor,
                z,
                g.EXTERIOR_WALL,
                offset - cursor,
                height,
                WALL,
            )
        if sill > 0:
            add(
                f"{name} sill {index}",
                "Exterior wall",
                level,
                x,
                offset,
                z,
                g.EXTERIOR_WALL,
                width,
                sill,
                WALL,
            )
        top = sill + opening_height
        if top < height:
            add(
                f"{name} header {index}",
                "Exterior wall",
                level,
                x,
                offset,
                z + top,
                g.EXTERIOR_WALL,
                width,
                height - top,
                WALL,
            )
        cursor = offset + width
    if cursor < g.BUILDING_DEPTH:
        add(
            f"{name} final segment",
            "Exterior wall",
            level,
            x,
            cursor,
            z,
            g.EXTERIOR_WALL,
            g.BUILDING_DEPTH - cursor,
            height,
            WALL,
        )


def opening_insert(name, level, axis, offset, width, sill, height, upper=False, door=False):
    z = (g.UPPER_SUBFLOOR_TOP if upper else g.GROUND_SLAB_TOP) + sill
    color = DOOR if door else GLASS
    if axis == "x":
        add(name, "Door" if door else "Window", level, offset, 0.22, z, width, 0.06, height, color)
    else:
        add(name, "Door" if door else "Window", level, 23.72, offset, z, 0.06, width, height, color)


def build():
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
        SLAB,
    )
    wall_x("L1 south wall", "Level 1", 0, 0.5, 8.0, g.OPENINGS["l1_south"])
    wall_x("L1 north wall", "Level 1", 19.5, 0.5, 8.0, g.OPENINGS["l1_north"])
    wall_y("L1 west wall", "Level 1", 0, 0.5, 8.0, g.OPENINGS["l1_west"])
    wall_y("L1 east wall", "Level 1", 23.5, 0.5, 8.0, g.OPENINGS["l1_east"])
    upper_h = g.EAVE_HEIGHT - g.UPPER_SUBFLOOR_TOP
    wall_x("L2 south wall", "Level 2", 0, g.UPPER_SUBFLOOR_TOP, upper_h, g.OPENINGS["l2_south"])
    wall_x(
        "L2 north blank wall",
        "Level 2",
        19.5,
        g.UPPER_SUBFLOOR_TOP,
        upper_h,
        g.OPENINGS["l2_north"],
    )
    wall_y("L2 west wall", "Level 2", 0, g.UPPER_SUBFLOOR_TOP, upper_h, g.OPENINGS["l2_west"])
    wall_y("L2 east wall", "Level 2", 23.5, g.UPPER_SUBFLOOR_TOP, upper_h, g.OPENINGS["l2_east"])

    # Simplified but dimensionally placed Option F partitions.
    add("L1 service band wall", "Interior wall", "Level 1", 0.5, 11.5, 0.5, 23.0, 0.33, 8.0, INNER)
    add("L1 support east wall", "Interior wall", "Level 1", 7.5, 11.5, 0.5, 0.33, 8.0, 8.0, INNER)
    add("L1 core east wall", "Interior wall", "Level 1", 14.0, 11.5, 0.5, 0.33, 8.0, 8.0, INNER)
    add("L1 powder south wall", "Interior wall", "Level 1", 7.5, 13.5, 0.5, 6.83, 0.33, 8.0, INNER)
    add("L2 bedroom east wall", "Interior wall", "Level 2", 10.2, 0.5, 9.25, 0.33, 9.5, 6.75, INNER)
    add(
        "L2 bedroom north wall",
        "Interior wall",
        "Level 2",
        0.5,
        10.0,
        9.25,
        10.03,
        0.33,
        6.75,
        INNER,
    )
    add(
        "L2 storage south wall",
        "Interior wall",
        "Level 2",
        0.5,
        13.5,
        9.25,
        13.83,
        0.33,
        6.75,
        INNER,
    )
    add("L2 bath west wall", "Interior wall", "Level 2", 7.5, 13.5, 9.25, 0.33, 6.0, 6.75, INNER)
    add("L2 bath east wall", "Interior wall", "Level 2", 14.0, 13.5, 9.25, 0.33, 6.0, 6.75, INNER)
    add("Low TV wall", "Interior wall", "Level 2", 13.0, 7.2, 9.25, 6.0, 0.35, 4.0, INNER)

    for name, (x, y, dx, dy) in g.ROOMS.items():
        z = 9.27 if name.startswith("L2") else 0.52
        add(name, "Room zone", name[:2], x, y, z, dx, dy, 0.025, ZONE)

    opening_insert("Garage overhead door", "Level 1", "y", 1.3, 9.7, 0, 7.5, door=True)
    opening_insert("L1 east shop window", "Level 1", "y", 4.0, 3.0, 3.0, 3.5)
    opening_insert("L1 east 6ft slider", "Level 1", "y", 12.3, 6.0, 0, 6.667)
    opening_insert(
        "L2 south entry door", "Level 2", "x", 11.5, 3.0, 0, 6.667, upper=True, door=True
    )
    opening_insert("L2 south living window", "Level 2", "x", 16.0, 5.0, 2.3, 3.5, upper=True)
    add("L2 west bedroom EERO window", "Window", "Level 2", 0.22, 3.0, 11.55, 0.06, 3.5, 3.5, GLASS)
    opening_insert("L2 east 6ft slider", "Level 2", "y", 1.5, 6.0, 0, 6.667, upper=True)
    opening_insert("L2 east dining window", "Level 2", "y", 15.0, 3.5, 2.3, 3.5, upper=True)

    add("Ground south covered patio", "Patio", "Level 1", 11.5, -4, 0, 16.5, 4, 0.25, DECK)
    add("Ground east patio 4ft", "Patio", "Level 1", 24, 0, 0, 4, 19.5, 0.25, DECK)
    add("Upper south landing", "Landing", "Level 2", 11.5, -4, 9.25, 16.5, 4, 0.35, DECK)
    add("Upper east patio 4ft", "Balcony", "Level 2", 24, 0, 9.25, 4, 19.5, 0.35, DECK)
    run = (g.STAIR_EAST - g.STAIR_WEST) / g.STAIR_TREADS
    rise = g.UPPER_SUBFLOOR_TOP / g.STAIR_RISERS
    for index in range(g.STAIR_TREADS):
        add(
            f"Exterior stair tread {index + 1:02d}",
            "Exterior stair",
            "Exterior",
            g.STAIR_WEST + index * run,
            -4,
            0,
            run + 0.02,
            4,
            (index + 1) * rise,
            DECK,
        )
    add("South landing guard", "Guard", "Exterior", 11.5, -4, 9.6, 16.5, 0.12, 3.0, DECK)
    add("East patio guard", "Guard", "Exterior", 27.88, 0, 9.6, 0.12, 19.5, 3.0, DECK)

    slope = math.hypot(10.0, g.RIDGE_HEIGHT - g.EAVE_HEIGHT)
    angle = math.atan2(g.RIDGE_HEIGHT - g.EAVE_HEIGHT, 10.0)
    half_t = 0.175
    roof_center_z = (g.EAVE_HEIGHT + g.RIDGE_HEIGHT) / 2 - half_t * math.cos(angle)
    north_flush_shift = half_t * math.sin(angle)
    add(
        "South roof plane flush west",
        "Roof",
        "Roof",
        0,
        5 - slope / 2,
        roof_center_z - 0.175,
        24,
        slope,
        0.35,
        ROOF,
        angle,
    )
    add(
        "North roof plane flush north-west",
        "Roof",
        "Roof",
        0,
        15 - slope / 2 - north_flush_shift,
        roof_center_z - 0.175,
        24,
        slope,
        0.35,
        ROOF,
        -angle,
    )


def mesh_for(part):
    mesh = trimesh.creation.box(extents=part.size)
    mesh.visual = ColorVisuals(
        mesh=mesh,
        vertex_colors=np.tile(np.array(part.color, dtype=np.uint8), (len(mesh.vertices), 1)),
    )
    transform = np.eye(4)
    if part.rotate_x:
        transform = trimesh.transformations.rotation_matrix(part.rotate_x, [1, 0, 0])
    transform[:3, 3] = np.array(part.center)
    mesh.apply_transform(transform)
    return mesh


def ocp_shape(part):
    dx, dy, dz = (value * FT for value in part.size)
    cx, cy, cz = (value * FT for value in part.center)
    shape = BRepPrimAPI_MakeBox(gp_Pnt(-dx / 2, -dy / 2, -dz / 2), dx, dy, dz).Shape()
    if part.rotate_x:
        rot = gp_Trsf()
        rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), part.rotate_x)
        shape = BRepBuilderAPI_Transform(shape, rot, True).Shape()
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(cx, cy, cz))
    shape = BRepBuilderAPI_Transform(shape, tr, True).Shape()
    return shape


def main():
    build()
    scene = trimesh.Scene()
    for part in parts:
        scene.add_geometry(mesh_for(part), node_name=part.name, geom_name=part.name)
    scene.export(OUT / "adu-option-f.glb")
    scene.export(OUT / "adu-option-f.obj")

    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for part in parts:
        builder.Add(compound, ocp_shape(part))
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    if writer.Write(str(OUT / "adu-option-f.step")) != IFSelect_RetDone:
        raise RuntimeError("STEP export failed")
    if not BRepTools.Write_s(compound, str(OUT / "adu-option-f.brep")):
        raise RuntimeError("BREP export failed")

    bounds = scene.bounds
    manifest = {
        "schema": "adu-option-f-model-manifest-v1",
        "design": g.DESIGN,
        "version": g.VERSION,
        "status": "schematic design basis; not for construction",
        "sources": [
            "apartment/option-f-recommended-development.svg",
            "plan/site-plan-option-f.dxf",
            "output/pdf/adu-option-f-construction-engineering-basis.pdf",
        ],
        "units": "feet",
        "datums_ft": {
            "upper_subfloor": g.UPPER_SUBFLOOR_TOP,
            "eave": g.EAVE_HEIGHT,
            "ridge": round(g.RIDGE_HEIGHT, 3),
        },
        "bounds_ft": {"min": bounds[0].round(3).tolist(), "max": bounds[1].round(3).tolist()},
        "object_count": len(parts),
        "objects": [
            {
                "name": part.name,
                "category": part.category,
                "level": part.level,
                "center_ft": part.center,
                "size_ft": part.size,
            }
            for part in parts
        ],
    }
    (OUT / "adu-option-f-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote Option F STEP/BREP/GLB/OBJ + manifest ({len(parts)} objects)")


if __name__ == "__main__":
    main()
