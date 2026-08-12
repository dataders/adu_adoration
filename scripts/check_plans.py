#!/usr/bin/env python3
"""Validate committed architectural plan and model artifacts."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import shutil
import struct
import subprocess
import sys
from collections.abc import Iterable, Sequence
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
        "ADU N. SETBACK 5' - R-5 MIN MET",
        "FRONT SETBACK 25' (MEASURED)",
        "PRELIMINARY - NOT FOR CONSTRUCTION - DIMENSIONS APPROX, FIELD-VERIFY",
    }
    missing_text = sorted(value for value in required_text if value not in text)
    require(not missing_text, f"DXF missing required annotations: {missing_text}")


def load_manifest() -> dict[str, Any]:
    path = MODEL_DIR / "adu-option-f-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "adu-option-f-model-manifest-v1", "unknown manifest schema")
    require(payload.get("design") == "Option F", "manifest design must be Option F")
    require(payload.get("object_count") == 79, "manifest must describe 79 objects")
    objects = payload.get("objects")
    require(isinstance(objects, list) and len(objects) == 79, "manifest object list is incomplete")
    return payload


def validate_manifest(payload: dict[str, Any]) -> None:
    require(payload.get("units") == "feet", "manifest units changed")
    require(payload.get("version") == "2026-08-03-option-f-basis-v1", "model version changed")
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
        "L1 east 6ft slider",
        "L2 east 6ft slider",
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
        PLAN_DIR / "site-plan-option-f.png": (1839, 960),
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
        payload.get("version") == "2026-08-03-option-f-basis-v1",
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
            "ridge_max_ft": 19.833,
            "east_patio_depth_ft": 4.0,
            "east_slider_width_ft": 6.0,
            "stair_risers": 14,
            "stair_treads": 13,
            "guard_height_ft": 3.0,
            "north_wall_openings": 0,
            "west_upper_windows": 1,
            "south_upper_sliders": 0,
            "setback_roof_edges": ["north eave flush", "west rake flush"],
        },
        "coordinated invariants changed",
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
            ("STEP BRep geometry", lambda: validate_step(manifest)),
            ("GLB model", validate_glb),
            ("SVG, PDF, and PNG outputs", validate_rendered_outputs),
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
