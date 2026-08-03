"""Export the Option E FreeCAD model for web, interchange, and review.

Run with FreeCAD's bundled Python runtime:

    PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib \
      /Applications/FreeCAD.app/Contents/Resources/bin/python \
        model/export_freecad_formats.py
"""

import json
import sys
from pathlib import Path

import FreeCAD as App  # ty: ignore[unresolved-import]
import Part  # ty: ignore[unresolved-import]

FT = 304.8
OUT_DIR = Path(__file__).resolve().parent
SOURCE = OUT_DIR / "adu-option-e.FCStd"


def model_objects(doc):
    return sorted(
        (
            obj
            for obj in doc.Objects
            if "Category" in obj.PropertiesList and hasattr(obj, "Shape") and not obj.Shape.isNull()
        ),
        key=lambda obj: obj.Name,
    )


def stored_color(obj):
    color = obj.DisplayColor
    return tuple(float(color[index]) for index in range(3))


def export_manifest(objects, path):
    compound = Part.makeCompound([obj.Shape for obj in objects])
    bounds = compound.BoundBox
    payload = {
        "schema": "adu-option-e-object-manifest-v1",
        "units": {
            "source_geometry": "millimetres",
            "reported_bounds": "feet",
            "reported_area": "square feet",
            "reported_volume": "cubic feet",
        },
        "object_count": len(objects),
        "bounds_ft": {
            "min": [round(value / FT, 6) for value in (bounds.XMin, bounds.YMin, bounds.ZMin)],
            "max": [round(value / FT, 6) for value in (bounds.XMax, bounds.YMax, bounds.ZMax)],
        },
        "objects": [],
    }
    for obj in objects:
        shape = obj.Shape
        box = shape.BoundBox
        color = stored_color(obj)
        payload["objects"].append(
            {
                "name": obj.Name,
                "label": obj.Label,
                "category": obj.Category,
                "level": obj.Level,
                "design_source": obj.DesignSource,
                "color_rgb": [round(channel, 6) for channel in color],
                "color_hex": "#" + "".join(f"{round(channel * 255):02x}" for channel in color),
                "transparency_percent": int(obj.DisplayTransparency),
                "bounds_ft": {
                    "min": [round(value / FT, 6) for value in (box.XMin, box.YMin, box.ZMin)],
                    "max": [round(value / FT, 6) for value in (box.XMax, box.YMax, box.ZMax)],
                },
                "area_sq_ft": round(shape.Area / (FT * FT), 6),
                "volume_cu_ft": round(shape.Volume / (FT * FT * FT), 6),
                "topology": {
                    "solids": len(shape.Solids),
                    "faces": len(shape.Faces),
                    "edges": len(shape.Edges),
                    "vertices": len(shape.Vertexes),
                },
            }
        )
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    import Import  # ty: ignore[unresolved-import]
    import Mesh  # ty: ignore[unresolved-import]

    sys.path.insert(0, str(Path(App.getHomePath()).resolve() / "Mod" / "BIM" / "importers"))
    import importOBJ  # ty: ignore[unresolved-import]

    doc = App.openDocument(str(SOURCE))
    objects = model_objects(doc)
    if len(objects) != 72:
        raise RuntimeError(f"expected 72 model objects, found {len(objects)}")

    invalid = [obj.Label for obj in objects if not obj.Shape.isValid()]
    if invalid:
        raise RuntimeError(f"invalid FreeCAD shapes: {invalid}")

    doc.recompute()

    # Native glTF/GLB export. The Arch OBJ below supplies colors for a
    # deterministic OBJ-to-GLB conversion step after this script runs.
    glb_path = OUT_DIR / "adu-option-e.glb"
    Import.export(objects, str(glb_path))

    # Generic triangulated Wavefront export.
    obj_path = OUT_DIR / "adu-option-e.obj"
    Mesh.export(objects, str(obj_path))

    # BIM/Arch Wavefront export: named objects plus companion color material file.
    arch_obj_path = OUT_DIR / "adu-option-e-arch.obj"
    colors = {obj.Name: stored_color(obj) for obj in objects}
    importOBJ.export(objects, str(arch_obj_path), colors=colors)

    # Headless STEP baseline. GUI export can overwrite this with presentation
    # colors while retaining the same exact source solids.
    step_path = OUT_DIR / "adu-option-e.step"
    Import.export(objects, str(step_path))

    # ASCII OpenCASCADE geometry for low-level textual inspection.
    brep_path = OUT_DIR / "adu-option-e.brep"
    Part.makeCompound([obj.Shape for obj in objects]).exportBrep(str(brep_path))

    # Stable semantic summary: most useful review artifact for Git diffs.
    manifest_path = OUT_DIR / "adu-option-e-manifest.json"
    export_manifest(objects, manifest_path)

    for path in (
        glb_path,
        obj_path,
        arch_obj_path,
        arch_obj_path.with_suffix(".mtl"),
        step_path,
        brep_path,
        manifest_path,
    ):
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"export missing or empty: {path}")
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")

    App.closeDocument(doc.Name)


if __name__ == "__main__":
    main()
