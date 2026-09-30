#!/usr/bin/env python3
"""Validate committed architectural plan and model artifacts."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import re
import shutil
import struct
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

import ezdxf
import ezdxf.units

ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "plan"
MODEL_DIR = ROOT / "model"
FT_IN_MM = 304.8
TOLERANCE = 1e-6


class CheckFailure(RuntimeError):
    """Raised when an artifact violates a project invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def close(actual: float, expected: float, *, tolerance: float = TOLERANCE) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)


def close_sequence(actual: Sequence[float], expected: Sequence[float], *, tolerance=1e-6) -> bool:
    return len(actual) == len(expected) and all(
        close(a, e, tolerance=tolerance) for a, e in zip(actual, expected, strict=True)
    )


def normalized_points(entity: Any) -> set[tuple[float, float]]:
    return {(round(float(point[0]), 6), round(float(point[1]), 6)) for point in entity.get_points()}


def find_closed_polyline(
    modelspace: Any, layer: str, expected_points: Iterable[tuple[float, float]]
):
    expected = set(expected_points)
    matches = [
        entity
        for entity in modelspace.query(f'LWPOLYLINE[layer=="{layer}"]')
        if entity.closed and normalized_points(entity) == expected
    ]
    require(
        len(matches) == 1, f"{layer}: expected one closed polyline with points {sorted(expected)}"
    )
    return matches[0]


def line_key(entity: Any) -> tuple[tuple[float, float], tuple[float, float]]:
    endpoints = sorted(
        (
            (round(float(entity.dxf.start.x), 6), round(float(entity.dxf.start.y), 6)),
            (round(float(entity.dxf.end.x), 6), round(float(entity.dxf.end.y), 6)),
        )
    )
    return endpoints[0], endpoints[1]


def validate_dxf() -> None:
    path = PLAN_DIR / "site-plan-option-f.dxf"
    document = ezdxf.readfile(path)
    auditor = document.audit()
    require(not auditor.errors, f"DXF audit found {len(auditor.errors)} error(s)")
    require(not auditor.fixes, f"DXF audit required {len(auditor.fixes)} repair(s)")
    require(document.units == ezdxf.units.FT, "DXF units must be feet")

    required_layers = {
        "LOT-BOUNDARY",
        "EXISTING-HOUSE",
        "EXISTING-HOUSE-DETAIL",
        "EXISTING-SHED-REMOVE",
        "PROPOSED-SHED",
        "PROPOSED-ADU",
        "PROPOSED-ADU-ACCESS",
        "R5-SETBACK",
        "DIMENSIONS",
        "TEXT",
        "NORTH-ARROW",
    }
    layers = {layer.dxf.name for layer in document.layers}
    require(required_layers <= layers, f"DXF missing layers: {sorted(required_layers - layers)}")

    modelspace = document.modelspace()
    find_closed_polyline(
        modelspace,
        "LOT-BOUNDARY",
        {(0.0, 0.0), (148.0, 0.0), (148.0, 45.0), (0.0, 45.0)},
    )
    find_closed_polyline(
        modelspace,
        "PROPOSED-SHED",
        {(8.0, 5.0), (26.0, 5.0), (26.0, 11.0), (8.0, 11.0)},
    )
    find_closed_polyline(
        modelspace,
        "PROPOSED-ADU",
        {(5.0, 20.0), (29.0, 20.0), (29.0, 40.0), (5.0, 40.0)},
    )
    find_closed_polyline(
        modelspace,
        "PROPOSED-ADU-ACCESS",
        {(5.5, 16.0), (16.5, 16.0), (16.5, 20.0), (5.5, 20.0)},
    )

    setback_lines = {line_key(entity) for entity in modelspace.query('LINE[layer=="R5-SETBACK"]')}
    expected_setbacks = {
        ((0.0, 5.0), (148.0, 5.0)),
        ((0.0, 40.0), (148.0, 40.0)),
        ((5.0, 0.0), (5.0, 45.0)),
        ((123.0, 0.0), (123.0, 45.0)),
    }
    require(setback_lines == expected_setbacks, "R-5 setback reference lines changed")

    access_polylines = list(modelspace.query('LWPOLYLINE[layer=="PROPOSED-ADU-ACCESS"]'))
    expected_open_access = {
        frozenset({(16.5, 16.0), (33.0, 16.0), (33.0, 20.0)}),
        frozenset({(29.0, 20.0), (29.0, 39.5), (33.0, 39.5), (33.0, 20.0)}),
    }
    actual_open_access = {
        frozenset(normalized_points(entity))
        for entity in access_polylines
        if not getattr(entity, "closed")
    }
    require(
        actual_open_access == expected_open_access, "Option F landing or patio geometry changed"
    )

    design_access_points = [
        point for entity in access_polylines for point in normalized_points(entity)
    ]
    design_access_points.extend([(16.5, 20.0), (29.0, 20.0)])
    access_bounds = (
        min(point[0] for point in design_access_points),
        min(point[1] for point in design_access_points),
        max(point[0] for point in design_access_points),
        max(point[1] for point in design_access_points),
    )
    require(
        close_sequence(access_bounds, (5.5, 16.0, 33.0, 39.5)),
        f"Option F access geometry bounds changed: {access_bounds}",
    )

    dimensions = list(modelspace.query('DIMENSION[layer=="DIMENSIONS"]'))
    require(len(dimensions) == 14, f"expected 14 dimensions, found {len(dimensions)}")
    text = "\n".join(
        entity.dxf.text for entity in modelspace.query("TEXT") if entity.dxf.hasattr("text")
    )
    required_text = {
        "OPTION F ADU",
        "20 x 24  -  2 STORY",
        "18 x 6  -  108 SF - LOW PROFILE",
        "5' CLEAR",
        "ADU NORTH SETBACK: 5 FT DESIGN BASIS",
        "FRONT SETBACK 25' (MEASURED)",
        "PRELIMINARY - NOT FOR CONSTRUCTION - DIMENSIONS APPROX, FIELD-VERIFY",
    }
    missing_text = sorted(value for value in required_text if value not in text)
    require(not missing_text, f"DXF missing required annotations: {missing_text}")


def load_manifest() -> dict[str, Any]:
    path = MODEL_DIR / "adu-option-f-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "adu-option-f-model-manifest-v2", "unknown manifest schema")
    require(
        payload.get("design") == "Option F · revision 2",
        "manifest design must be Option F revision 2",
    )
    require(payload.get("object_count", 0) > 0, "manifest has no physical objects")
    objects = payload.get("objects")
    require(isinstance(objects, list), "manifest object list is incomplete")
    physical = [item for item in objects if item["category"] != "Room zone"]
    require(len(physical) == payload["object_count"], "physical object count differs from manifest")
    return payload


def validate_manifest(payload: dict[str, Any]) -> None:
    require(payload.get("units") == "feet", "manifest units changed")
    require(payload.get("version") == "2026-09-30-option-f-basis-v2", "model version changed")
    require(
        payload.get("datums_ft") == {"upper_subfloor": 9.25, "eave": 16.0, "ridge": 19.833},
        "Option F vertical datums changed",
    )
    bounds = payload["bounds_ft"]
    require(close_sequence(bounds["min"], (0.0, -4.0, 0.0)), "manifest minimum bounds changed")
    require(
        close_sequence(bounds["max"], (28.0, 20.0, 19.833), tolerance=1e-3),
        f"manifest maximum bounds changed: {bounds['max']}",
    )

    objects = payload["objects"]
    names = [item["name"] for item in objects]
    require(len(names) == len(set(names)), "manifest contains duplicate object names")
    require(
        all(all(value > 0 for value in item["size_ft"]) for item in objects),
        "object with non-positive size",
    )

    stair_steps = [item for item in objects if item["category"] == "Exterior stair"]
    room_zones = [item for item in objects if item["category"] == "Room zone"]
    require(len(stair_steps) == 13, f"expected 13 stair steps, found {len(stair_steps)}")
    require(len(room_zones) == 10, f"expected 10 room zones, found {len(room_zones)}")

    objects_by_label = {item["name"]: item for item in objects}
    required_labels = {
        "Level 1 slab 20x24",
        "Level 2 floor assembly 20x24",
        "Ground south covered patio",
        "Upper south landing",
        "Ground east patio 4ft",
        "Upper east patio 4ft",
        "Garage overhead door",
        "South roof plane flush west",
        "North roof plane flush north-west",
    }
    require(required_labels <= objects_by_label.keys(), "manifest missing major model components")
    for label in ("Level 1 slab 20x24", "Level 2 floor assembly 20x24"):
        width, depth = objects_by_label[label]["size_ft"][:2]
        require(close(width, 24.0) and close(depth, 20.0), f"{label} is not 24 ft x 20 ft")


def validate_step(payload: dict[str, Any]) -> None:
    brep_check = importlib.import_module("OCP.BRepCheck")
    bnd = importlib.import_module("OCP.Bnd")
    brep_bnd_lib = importlib.import_module("OCP.BRepBndLib")
    if_select = importlib.import_module("OCP.IFSelect")
    step_control = importlib.import_module("OCP.STEPControl")
    top_abs = importlib.import_module("OCP.TopAbs")
    top_exp = importlib.import_module("OCP.TopExp")

    step_reader_type = getattr(step_control, "STEPControl_Reader")
    read_done = getattr(if_select, "IFSelect_RetDone")
    analyzer_type = getattr(brep_check, "BRepCheck_Analyzer")
    explorer_type = getattr(top_exp, "TopExp_Explorer")
    solid_type = getattr(top_abs, "TopAbs_SOLID")
    box_type = getattr(bnd, "Bnd_Box")
    bounds_api = getattr(brep_bnd_lib, "BRepBndLib")

    reader = step_reader_type()
    status = reader.ReadFile(str(MODEL_DIR / "adu-option-f.step"))
    require(status == read_done, f"OpenCascade could not read STEP: {status}")
    require(reader.TransferRoots() > 0, "STEP has no transferable roots")
    shape = reader.OneShape()
    require(not shape.IsNull(), "STEP produced a null shape")
    require(analyzer_type(shape).IsValid(), "STEP contains invalid BRep geometry")

    explorer = explorer_type(shape, solid_type)
    solid_count = 0
    while explorer.More():
        solid_count += 1
        explorer.Next()
    expected_solids = payload["object_count"]
    require(
        solid_count == expected_solids, f"STEP has {solid_count} solids; expected {expected_solids}"
    )

    box = box_type()
    bounds_api.Add_s(shape, box)
    raw_bounds = box.Get()
    step_min = [raw_bounds[index] / FT_IN_MM for index in range(3)]
    step_max = [raw_bounds[index] / FT_IN_MM for index in range(3, 6)]
    require(
        close_sequence(step_min, payload["bounds_ft"]["min"], tolerance=1e-3),
        f"STEP minimum bounds differ from manifest: {step_min}",
    )
    require(
        close_sequence(step_max, payload["bounds_ft"]["max"], tolerance=1e-3),
        f"STEP maximum bounds differ from manifest: {step_max}",
    )


def read_glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) >= 20, "GLB is truncated")
    magic, version, declared_length = struct.unpack_from("<4sII", data)
    require(magic == b"glTF", "GLB magic header is invalid")
    require(version == 2, f"GLB version must be 2, found {version}")
    require(declared_length == len(data), "GLB declared length does not match file size")
    json_length, chunk_type = struct.unpack_from("<II", data, 12)
    require(chunk_type == 0x4E4F534A, "GLB first chunk is not JSON")
    return json.loads(data[20 : 20 + json_length].decode("utf-8"))


def validate_glb() -> None:
    path = MODEL_DIR / "adu-option-f.glb"
    payload = read_glb_json(path)
    require(payload.get("asset", {}).get("version") == "2.0", "GLB asset version is not 2.0")
    require(len(payload.get("scenes", [])) >= 1, "GLB has no scene")
    require(len(payload.get("nodes", [])) >= 1, "GLB has no nodes")
    require(len(payload.get("meshes", [])) >= 1, "GLB has no meshes")

    # glTF requires metres and Y-up; verify the exported transform, not just its header.
    trimesh = importlib.import_module("trimesh")
    mesh_scene = trimesh.load(path, force="scene")
    bounds = load_manifest()["bounds_ft"]
    lo, hi = bounds["min"], bounds["max"]
    expected_min = [lo[0] * 0.3048, lo[2] * 0.3048, -hi[1] * 0.3048]
    expected_max = [hi[0] * 0.3048, hi[2] * 0.3048, -lo[1] * 0.3048]
    require(
        close_sequence(mesh_scene.bounds[0], expected_min, tolerance=1e-3),
        "GLB minimum bounds do not match metres/Y-up conversion",
    )
    require(
        close_sequence(mesh_scene.bounds[1], expected_max, tolerance=1e-3),
        "GLB maximum bounds do not match metres/Y-up conversion",
    )

    validator = shutil.which("gltf_validator")
    if validator is None:
        print("  note: official Khronos glTF validator not found; CI installs and runs it")
        return
    result = subprocess.run(
        [validator, "-o", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    require(result.returncode == 0, f"Khronos glTF validation failed:\n{result.stderr.strip()}")
    report = json.loads(result.stdout)
    issues = report["issues"]
    require(issues["numErrors"] == 0, "Khronos glTF validator reported errors")
    require(issues["numWarnings"] == 0, "Khronos glTF validator reported warnings")
    print(f"  Khronos report: 0 errors, 0 warnings, {issues['numHints']} hints")


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} has an invalid PNG header")
    return struct.unpack(">II", header[16:24])


def validate_rendered_outputs() -> None:
    pypdf = importlib.import_module("pypdf")
    pdf = pypdf.PdfReader(PLAN_DIR / "site-plan-option-f-architect.pdf")
    require(len(pdf.pages) == 1, "architect PDF must contain exactly one page")
    page = pdf.pages[0]
    require(float(page.mediabox.width) > 600, "architect PDF page width is unexpectedly small")
    require(float(page.mediabox.height) > 300, "architect PDF page height is unexpectedly small")
    contents = page.get_contents()
    require(
        contents is not None and len(contents.get_data()) > 1_000, "architect PDF page is empty"
    )

    expected_pngs = {
        PLAN_DIR / "site-plan-option-f.png": (1961, 960),
        ROOT / "apartment" / "option-f-recommended-development.png": (3308, 2336),
    }
    for path, expected_dimensions in expected_pngs.items():
        require(png_dimensions(path) == expected_dimensions, f"{path.name} dimensions changed")


def validate_required_artifacts() -> None:
    required = {
        PLAN_DIR / "site-plan-option-f.dxf",
        PLAN_DIR / "site-plan-option-f.png",
        PLAN_DIR / "site-plan-option-f-architect.pdf",
        MODEL_DIR / "adu-option-f.step",
        MODEL_DIR / "adu-option-f.brep",
        MODEL_DIR / "adu-option-f.glb",
        MODEL_DIR / "adu-option-f.obj",
        MODEL_DIR / "adu-option-f-manifest.json",
        MODEL_DIR / "site-model-3d.html",
        MODEL_DIR / "site-model.obj",
        MODEL_DIR / "adu-option-f-scene.json",
        MODEL_DIR / "viewer.js",
        MODEL_DIR / "viewer.css",
        MODEL_DIR / "vendor" / "three.module.js",
        ROOT / "apartment" / "option-f-level-1.svg",
        ROOT / "apartment" / "option-f-level-2.svg",
        ROOT / "apartment" / "option-f-alternative-garden.svg",
    }
    missing = sorted(str(path.relative_to(ROOT)) for path in required if not path.is_file())
    empty = sorted(
        str(path.relative_to(ROOT))
        for path in required
        if path.is_file() and path.stat().st_size == 0
    )
    require(not missing, f"missing required artifacts: {missing}")
    require(not empty, f"empty required artifacts: {empty}")


def validate_coordination_manifest() -> None:
    payload = json.loads((ROOT / "option-f-artifact-manifest.json").read_text())
    require(payload.get("design") == "Option F", "coordination manifest design changed")
    require(
        payload.get("schema") == "adu-option-f-artifact-coordination-v2",
        "coordination schema changed",
    )
    require(
        payload.get("authority_order", [None])[0] == "model/option_f_geometry.py",
        "canonical geometry must precede generated artifacts",
    )
    require(
        payload.get("version") == "2026-09-30-option-f-basis-v2",
        "coordination manifest version changed",
    )
    for role, relative_path in payload.get("current_artifacts", {}).items():
        require(
            (ROOT / relative_path).is_file(), f"current {role} artifact missing: {relative_path}"
        )
    require(
        payload.get("coordinated_invariants")
        == {
            "enclosed_footprint_ft": [24.0, 20.0],
            "upper_subfloor_ft": 9.25,
            "eave_ft": 16.0,
            "ridge_max_ft": 19.833333,
            "east_patio_depth_ft": 4.0,
            "east_slider_width_ft": 6.0,
            "stair_risers": 14,
            "stair_treads": 13,
            "guard_height_ft": 3.0,
            "north_wall_openings": 0,
            "west_upper_windows": 1,
            "south_upper_sliders": 0,
            "setback_roof_edges": ["north eave flush", "west rake flush"],
            "lower_hall_clear_ft": 3.25,
            "kitchen_approach_clear_ft": 4.47,
            "sofa_slider_route_clear_ft": 3.2,
            "dining_chair_counter_clear_ft": 3.3,
        },
        "coordinated invariants changed",
    )


def validate_shared_scene(payload: dict[str, Any]) -> None:
    """Catch stale exports and differing geometry between source, viewer, and CAD manifest."""
    sys.path.insert(0, str(MODEL_DIR))
    generator = importlib.import_module("generate_option_f_model")
    geometry = importlib.import_module("option_f_geometry")
    generator.build()
    source_parts = generator.parts
    scene = json.loads((MODEL_DIR / "adu-option-f-scene.json").read_text())
    require(scene["version"] == geometry.VERSION, "scene source version is stale")
    require(scene["units"] == "feet", "scene units must be feet")
    require(len(scene["parts"]) == len(source_parts), "scene parts differ from source")
    require(len(payload["objects"]) == len(source_parts), "manifest omits semantic parts")
    for source, stored, record in zip(
        source_parts, scene["parts"], payload["objects"], strict=True
    ):
        fields = json.loads(json.dumps(asdict(source)))
        require(
            all(stored.get(key) == value for key, value in fields.items()),
            f"stale scene part: {source.name}",
        )
        require(
            record["name"] == source.name and record["category"] == source.category,
            f"manifest identity mismatch: {source.name}",
        )
        require(
            close_sequence(record["center_ft"], source.center)
            and close_sequence(record["size_ft"], source.size),
            f"manifest geometry mismatch: {source.name}",
        )
        mesh = generator.mesh_for(source)
        require(stored["faces"] == mesh.faces.tolist(), f"stale mesh faces: {source.name}")
        require(
            len(stored["vertices"]) == len(mesh.vertices)
            and all(
                close_sequence(a, b) for a, b in zip(stored["vertices"], mesh.vertices, strict=True)
            ),
            f"stale mesh vertices: {source.name}",
        )
    viewer = (MODEL_DIR / "site-model-3d.html").read_text()
    match = re.search(
        r'<script id="model-data" type="application/json">(.*?)</script>', viewer, re.S
    )
    require(match is not None, "viewer missing shared scene JSON")
    embedded = json.loads(match.group(1)) if match else {}
    require(embedded.get("parts") == scene["parts"], "viewer geometry differs from exported scene")
    require(embedded.get("version") == scene["version"], "viewer version differs from scene")
    require('type="module" src="viewer.js"' in viewer, "viewer module missing")

    # Doorway clear volume must remain empty of wall solids. Decorative door leaves
    # are not wall solids and do not obscure this check of actual apertures.
    for level, partitions in geometry.PARTITIONS.items():
        floor = geometry.GROUND_SLAB_TOP if level == "Level 1" else geometry.UPPER_SUBFLOOR_TOP
        wall_parts = [
            part
            for part in source_parts
            if part.level == level and part.category == "Interior wall"
        ]
        for name, axis, fixed, _start, _end, doors in partitions:
            for offset, width, height in doors:
                if axis == "x":
                    low = (offset, fixed, floor)
                    high = (offset + width, fixed + geometry.INTERIOR_WALL, floor + height)
                else:
                    low = (fixed, offset, floor)
                    high = (fixed + geometry.INTERIOR_WALL, offset + width, floor + height)
                for part in wall_parts:
                    overlaps = all(
                        min(high[i], part.center[i] + part.size[i] / 2)
                        - max(low[i], part.center[i] - part.size[i] / 2)
                        > 1e-6
                        for i in range(3)
                    )
                    require(not overlaps, f"{name}: wall {part.name} blocks door aperture")

    # Exterior sliders, entry, garage door, and windows must also pass through
    # the wall, rather than sit as opaque markers on an uncut wall surface.
    for key, openings in geometry.OPENINGS.items():
        floor_key, side = key.split("_")
        level = "Level " + floor_key[1:]
        floor = geometry.GROUND_SLAB_TOP if level == "Level 1" else geometry.UPPER_SUBFLOOR_TOP
        wall_parts = [
            part
            for part in source_parts
            if part.level == level and part.category == "Exterior wall"
        ]
        for offset, width, sill, height in openings:
            fixed = {"south": 0.0, "north": 19.5, "west": 0.0, "east": 23.5}[side]
            if side in ("south", "north"):
                low = (offset, fixed, floor + sill)
                high = (offset + width, fixed + geometry.EXTERIOR_WALL, floor + sill + height)
            else:
                low = (fixed, offset, floor + sill)
                high = (fixed + geometry.EXTERIOR_WALL, offset + width, floor + sill + height)
            for part in wall_parts:
                overlaps = all(
                    min(high[i], part.center[i] + part.size[i] / 2)
                    - max(low[i], part.center[i] - part.size[i] / 2)
                    > 1e-6
                    for i in range(3)
                )
                require(not overlaps, f"{key}: wall {part.name} blocks exterior aperture")

    furniture = {item[0]: item for item in geometry.FURNITURE}
    room = geometry.ROOMS["L2 open living/kitchen/dining"]
    derived = {
        "lower_hall": geometry.ROOMS["L1 protected hall"][3],
        "entry_to_kitchen": furniture["Kitchen peninsula"][3] - room[0],
        "living_slider_route": geometry.BUILDING_WIDTH
        - geometry.EXTERIOR_WALL
        - (furniture["Sofa facing west"][3] + furniture["Sofa facing west"][5]),
        "dining_chair_to_counter": furniture["Dining chair 1"][4]
        - (furniture["Kitchen peninsula"][4] + furniture["Kitchen peninsula"][6]),
    }
    expected = {
        "lower_hall": 3.25,
        "entry_to_kitchen": 4.47,
        "living_slider_route": 3.2,
        "dining_chair_to_counter": 3.3,
    }
    for key, width in expected.items():
        require(close(derived[key], width), f"actual {key} clearance changed: {derived[key]}")
        require(
            close(payload["clearances_ft"][key], derived[key]),
            f"manifest clearance does not match geometry: {key}",
        )
    garage = next(part for part in source_parts if part.name == "Garage overhead door")
    require(
        garage.center[0] < 0.5 and garage.size[1] > 9, "garage door must occupy the west/alley wall"
    )
    steps = [part for part in source_parts if part.category == "Exterior stair"]
    tops = sorted(part.center[2] + part.size[2] / 2 for part in steps)
    riser = (geometry.UPPER_SUBFLOOR_TOP - geometry.GROUND_SLAB_TOP) / geometry.STAIR_RISERS
    heights = [geometry.GROUND_SLAB_TOP, *tops, geometry.UPPER_SUBFLOOR_TOP]
    require(
        all(close(b - a, riser) for a, b in zip(heights, heights[1:])),
        "exterior stair rises are inconsistent between ground landing and upper floor",
    )


def validate_render_provenance() -> None:
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = json.loads((ROOT / "renderings" / "model-render-manifest.json").read_text())
    scene_path = MODEL_DIR / "adu-option-f-scene.json"
    scene = json.loads(scene_path.read_text())
    expected = {
        "option-f-yard-model.png": "yard",
        "option-f-alley-model.png": "alley",
        "option-f-upper-cutaway.png": "upper",
        "option-f-lower-cutaway.png": "lower",
    }
    for name, view in expected.items():
        require(name in manifest, f"render provenance missing {name}")
        record = manifest[name]
        require(
            record.get("scene") == "model/adu-option-f-scene.json", f"wrong render source: {name}"
        )
        require(record.get("scene_sha256") == digest(scene_path), f"stale render scene: {name}")
        require(record.get("scene_version") == scene["version"], f"stale render version: {name}")
        require(
            record.get("renderer_sha256") == digest(MODEL_DIR / "render_model.py"),
            f"stale rendering script: {name}",
        )
        image_path = ROOT / "renderings" / name
        require(record.get("image_sha256") == digest(image_path), f"image hash mismatch: {name}")
        require(record.get("view") == view, f"wrong render camera: {name}")
        width, height = png_dimensions(image_path)
        require(
            width == record.get("width") and width >= 1000 and height >= 600,
            f"render image dimensions invalid: {name}",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    checks = [
        ("required artifacts", validate_required_artifacts),
        ("coordination manifest", validate_coordination_manifest),
        ("DXF audit and site geometry", validate_dxf),
    ]
    manifest = load_manifest()
    checks.extend(
        [
            ("Option F semantic manifest", lambda: validate_manifest(manifest)),
            (
                "shared scene, door apertures, and clearances",
                lambda: validate_shared_scene(manifest),
            ),
            ("STEP BRep geometry", lambda: validate_step(manifest)),
            ("GLB model", validate_glb),
            ("SVG, PDF, and PNG outputs", validate_rendered_outputs),
            ("model rendering provenance", validate_render_provenance),
        ]
    )

    try:
        for label, check in checks:
            check()
            print(f"ok: {label}")
    except (CheckFailure, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("all architecture plan checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
