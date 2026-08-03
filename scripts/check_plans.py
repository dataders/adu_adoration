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
import xml.etree.ElementTree as ET
import zipfile
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
    path = PLAN_DIR / "site-plan.dxf"
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
        frozenset({(16.5, 16.0), (32.5, 16.0), (32.5, 20.0)}),
        frozenset({(29.0, 20.0), (29.0, 39.5), (32.5, 39.5), (32.5, 20.0)}),
    }
    actual_open_access = {
        frozenset(normalized_points(entity))
        for entity in access_polylines
        if not getattr(entity, "closed")
    }
    require(
        actual_open_access == expected_open_access, "Option E landing or patio geometry changed"
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
        close_sequence(access_bounds, (5.5, 16.0, 32.5, 39.5)),
        f"Option E access geometry bounds changed: {access_bounds}",
    )

    dimensions = list(modelspace.query('DIMENSION[layer=="DIMENSIONS"]'))
    require(len(dimensions) == 14, f"expected 14 dimensions, found {len(dimensions)}")
    text = "\n".join(
        entity.dxf.text for entity in modelspace.query("TEXT") if entity.dxf.hasattr("text")
    )
    required_text = {
        "OPTION E ADU",
        "20 x 24  -  2 STORY",
        "18 x 6  -  108 SF - LOW PROFILE",
        "5' CLEAR SHED-TO-STAIR",
        "ADU N. SETBACK 5' - R-5 MIN MET",
        "FRONT SETBACK 25' (MEASURED)",
        "PRELIMINARY - NOT FOR CONSTRUCTION - DIMENSIONS APPROX, FIELD-VERIFY",
    }
    missing_text = sorted(value for value in required_text if value not in text)
    require(not missing_text, f"DXF missing required annotations: {missing_text}")


def load_manifest() -> dict[str, Any]:
    path = MODEL_DIR / "adu-option-e-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "adu-option-e-object-manifest-v1", "unknown manifest schema")
    require(payload.get("object_count") == 72, "manifest must describe 72 objects")
    objects = payload.get("objects")
    require(isinstance(objects, list) and len(objects) == 72, "manifest object list is incomplete")
    return payload


def validate_manifest(payload: dict[str, Any]) -> None:
    require(
        payload.get("units")
        == {
            "source_geometry": "millimetres",
            "reported_bounds": "feet",
            "reported_area": "square feet",
            "reported_volume": "cubic feet",
        },
        "manifest units changed",
    )
    bounds = payload["bounds_ft"]
    require(close_sequence(bounds["min"], (0.0, -4.0, 0.0)), "manifest minimum bounds changed")
    require(close_sequence(bounds["max"], (27.5, 20.0, 20.0)), "manifest maximum bounds changed")

    objects = payload["objects"]
    names = [item["name"] for item in objects]
    require(len(names) == len(set(names)), "manifest contains duplicate object names")
    require(all(item["design_source"] == "Option E" for item in objects), "design source changed")
    require(all(item["area_sq_ft"] > 0 for item in objects), "object with non-positive area")
    require(all(item["volume_cu_ft"] > 0 for item in objects), "object with non-positive volume")
    require(all(item["topology"]["solids"] >= 1 for item in objects), "object without a solid")

    stair_steps = [item for item in objects if item["category"] == "Exterior stair"]
    room_zones = [item for item in objects if item["category"] == "Room zone"]
    require(len(stair_steps) == 13, f"expected 13 stair steps, found {len(stair_steps)}")
    require(len(room_zones) == 10, f"expected 10 room zones, found {len(room_zones)}")

    objects_by_label = {item["label"]: item for item in objects}
    required_labels = {
        "Level 1 slab 20x24",
        "Level 2 floor assembly 20x24",
        "Ground south covered patio",
        "Upper south landing",
        "Upper east balcony",
        "South roof plane",
        "North roof plane",
    }
    require(required_labels <= objects_by_label.keys(), "manifest missing major model components")
    for label in ("Level 1 slab 20x24", "Level 2 floor assembly 20x24"):
        item_bounds = objects_by_label[label]["bounds_ft"]
        width = item_bounds["max"][0] - item_bounds["min"][0]
        depth = item_bounds["max"][1] - item_bounds["min"][1]
        require(close(width, 24.0) and close(depth, 20.0), f"{label} is not 24 ft x 20 ft")


def validate_fcstd(payload: dict[str, Any]) -> None:
    path = MODEL_DIR / "adu-option-e.FCStd"
    require(zipfile.is_zipfile(path), "FCStd is not a valid ZIP container")
    expected_shape_files = {f"{item['name']}.Shape.brp" for item in payload["objects"]}
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, "FCStd contains an entry with a bad CRC")
        entries = set(archive.namelist())
        require(
            {"Document.xml", "GuiDocument.xml", "ShapeAppearance"} <= entries, "FCStd is incomplete"
        )
        actual_shape_files = {name for name in entries if name.endswith(".Shape.brp")}
        require(
            actual_shape_files == expected_shape_files, "FCStd shapes do not match manifest objects"
        )
        root = ET.fromstring(archive.read("Document.xml"))

    objects_element = root.find("Objects")
    require(objects_element is not None, "FCStd Document.xml has no Objects section")
    document_names = {element.attrib["name"] for element in root.findall("./ObjectData/Object")}
    manifest_names = {item["name"] for item in payload["objects"]}
    require(manifest_names <= document_names, "FCStd Document.xml is missing manifest objects")


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
    status = reader.ReadFile(str(MODEL_DIR / "adu-option-e.step"))
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
    expected_solids = sum(item["topology"]["solids"] for item in payload["objects"])
    require(
        solid_count == expected_solids, f"STEP has {solid_count} solids; expected {expected_solids}"
    )

    box = box_type()
    bounds_api.Add_s(shape, box)
    raw_bounds = box.Get()
    step_min = [raw_bounds[index] / FT_IN_MM for index in range(3)]
    step_max = [raw_bounds[index] / FT_IN_MM for index in range(3, 6)]
    require(
        close_sequence(step_min, payload["bounds_ft"]["min"], tolerance=1e-5),
        f"STEP minimum bounds differ from manifest: {step_min}",
    )
    require(
        close_sequence(step_max, payload["bounds_ft"]["max"], tolerance=1e-5),
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
    path = MODEL_DIR / "adu-option-e.glb"
    payload = read_glb_json(path)
    require(payload.get("asset", {}).get("version") == "2.0", "GLB asset version is not 2.0")
    require(len(payload.get("scenes", [])) >= 1, "GLB has no scene")
    require(len(payload.get("nodes", [])) >= 1, "GLB has no nodes")
    require(len(payload.get("meshes", [])) == 18, "GLB must retain 18 material meshes")
    require(len(payload.get("materials", [])) == 18, "GLB must retain 18 materials")

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
    svg_path = PLAN_DIR / "site-plan.svg"
    svg_root = ET.parse(svg_path).getroot()
    require(svg_root.tag == "{http://www.w3.org/2000/svg}svg", "site-plan.svg has an invalid root")
    require(svg_root.attrib.get("viewBox") == "0 0 960 440", "site-plan.svg viewBox changed")
    svg_text = " ".join(element.text or "" for element in svg_root.iter())
    for expected in ("20 × 24 ft enclosed", "5 ft clear", "R-5 minimum met"):
        require(expected in svg_text, f"site-plan.svg missing text: {expected}")

    pypdf = importlib.import_module("pypdf")
    pdf = pypdf.PdfReader(PLAN_DIR / "site-plan-architect.pdf")
    require(len(pdf.pages) == 1, "architect PDF must contain exactly one page")
    page = pdf.pages[0]
    require(float(page.mediabox.width) > 600, "architect PDF page width is unexpectedly small")
    require(float(page.mediabox.height) > 300, "architect PDF page height is unexpectedly small")
    contents = page.get_contents()
    require(
        contents is not None and len(contents.get_data()) > 1_000, "architect PDF page is empty"
    )

    expected_pngs = {
        PLAN_DIR / "site-plan.png": (1920, 880),
        MODEL_DIR / "adu-option-e-level-1.png": (1600, 1200),
        MODEL_DIR / "adu-option-e-level-2.png": (1600, 1200),
        MODEL_DIR / "adu-option-e-axon.png": (1600, 1200),
    }
    for path, expected_dimensions in expected_pngs.items():
        require(png_dimensions(path) == expected_dimensions, f"{path.name} dimensions changed")


def validate_required_artifacts() -> None:
    required = {
        PLAN_DIR / "site-plan.dxf",
        PLAN_DIR / "site-plan.svg",
        PLAN_DIR / "site-plan.png",
        PLAN_DIR / "site-plan-architect.pdf",
        MODEL_DIR / "adu-option-e.FCStd",
        MODEL_DIR / "adu-option-e.step",
        MODEL_DIR / "adu-option-e.brep",
        MODEL_DIR / "adu-option-e.glb",
        MODEL_DIR / "adu-option-e.obj",
        MODEL_DIR / "adu-option-e-arch.obj",
        MODEL_DIR / "adu-option-e-arch.mtl",
        MODEL_DIR / "adu-option-e-manifest.json",
    }
    missing = sorted(str(path.relative_to(ROOT)) for path in required if not path.is_file())
    empty = sorted(
        str(path.relative_to(ROOT))
        for path in required
        if path.is_file() and path.stat().st_size == 0
    )
    require(not missing, f"missing required artifacts: {missing}")
    require(not empty, f"empty required artifacts: {empty}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    checks = [
        ("required artifacts", validate_required_artifacts),
        ("DXF audit and site geometry", validate_dxf),
    ]
    manifest = load_manifest()
    checks.extend(
        [
            ("FreeCAD semantic manifest", lambda: validate_manifest(manifest)),
            ("FCStd archive", lambda: validate_fcstd(manifest)),
            ("STEP BRep geometry", lambda: validate_step(manifest)),
            ("GLB model", validate_glb),
            ("SVG, PDF, and PNG outputs", validate_rendered_outputs),
        ]
    )

    try:
        for label, check in checks:
            check()
            print(f"ok: {label}")
    except (CheckFailure, OSError, ValueError, ET.ParseError, zipfile.BadZipFile) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("all architecture plan checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
