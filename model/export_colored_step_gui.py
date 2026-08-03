"""FreeCAD GUI startup script for the color-preserving STEP export."""

from pathlib import Path

import FreeCAD as App  # ty: ignore[unresolved-import]
import FreeCADGui as Gui  # ty: ignore[unresolved-import]
import ImportGui  # ty: ignore[unresolved-import]

MODEL_DIR = Path(__file__).resolve().parent
SOURCE = MODEL_DIR / "adu-option-e.FCStd"
TARGET = MODEL_DIR / "adu-option-e.step"


doc = App.openDocument(str(SOURCE))
objects = sorted(
    (
        obj
        for obj in doc.Objects
        if "Category" in obj.PropertiesList and hasattr(obj, "Shape") and not obj.Shape.isNull()
    ),
    key=lambda obj: obj.Name,
)
if len(objects) != 72:
    raise RuntimeError(f"expected 72 model objects, found {len(objects)}")

for obj in objects:
    color = tuple(float(obj.DisplayColor[index]) for index in range(3))
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = tuple(max(0.0, channel - 0.25) for channel in color)
    obj.ViewObject.Transparency = int(obj.DisplayTransparency)

doc.recompute()
ImportGui.export(objects, str(TARGET))
print(f"wrote colored STEP {TARGET} ({TARGET.stat().st_size:,} bytes)")
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
