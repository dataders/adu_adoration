"""Convert color-material Arch OBJ to a web-oriented, metre-scale GLB."""

from pathlib import Path

import numpy as np
import trimesh


MODEL_DIR = Path(__file__).resolve().parent
SOURCE = MODEL_DIR / "adu-option-e-arch.obj"
TARGET = MODEL_DIR / "adu-option-e.glb"


def main():
    scene = trimesh.load_scene(SOURCE, process=False)
    # Trimesh batches the 72 OBJ objects into one geometry per color material.
    if len(scene.geometry) != 18:
        raise RuntimeError(f"expected 18 material geometries, found {len(scene.geometry)}")

    # FreeCAD OBJ is millimetres and Z-up. glTF is metres and Y-up.
    transform = np.array(
        [
            [0.001, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.001, 0.0],
            [0.0, -0.001, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    scene.apply_transform(transform)
    TARGET.write_bytes(scene.export(file_type="glb"))
    print(f"wrote {TARGET} ({TARGET.stat().st_size:,} bytes; {len(scene.geometry)} materials)")


if __name__ == "__main__":
    main()
