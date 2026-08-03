"""Prepare FreeCAD's Arch OBJ for Sweet Home 3D units and orientation."""

from pathlib import Path

import numpy as np
import trimesh


MODEL_DIR = Path(__file__).resolve().parent
SOURCE_OBJ = MODEL_DIR / "adu-option-e-arch.obj"
SOURCE_MTL = MODEL_DIR / "adu-option-e-arch.mtl"
SOURCE_SIMPLE_OBJ = MODEL_DIR / "adu-option-e.obj"
TARGET_OBJ = MODEL_DIR / "adu-option-e-sweethome.obj"
TARGET_MTL = MODEL_DIR / "adu-option-e-sweethome.mtl"
TARGET_SIMPLE_OBJ = MODEL_DIR / "adu-option-e-sweethome-simple.obj"


def main():
    scene = trimesh.load_scene(SOURCE_OBJ, process=False)
    if len(scene.geometry) != 18:
        raise RuntimeError(f"expected 18 material geometries, found {len(scene.geometry)}")

    output = ["# Sweet Home 3D optimized OBJ", f"mtllib {TARGET_MTL.name}"]
    vertex_offset = 0
    for name, mesh in sorted(scene.geometry.items()):
        # FreeCAD OBJ: millimetres, Z-up. Sweet Home 3D: centimetres, Y-up.
        vertices = np.column_stack(
            (mesh.vertices[:, 0] / 10, mesh.vertices[:, 2] / 10, -mesh.vertices[:, 1] / 10)
        )
        output.extend((f"o {name}", f"usemtl {name}"))
        output.extend(f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in vertices)
        for triangle in mesh.faces:
            indices = [int(index) + 1 + vertex_offset for index in triangle]
            output.append("f " + " ".join(str(index) for index in indices))
        vertex_offset += len(vertices)

    TARGET_OBJ.write_text("\n".join(output) + "\n", encoding="utf-8")
    TARGET_MTL.write_text(SOURCE_MTL.read_text(encoding="utf-8"), encoding="utf-8")

    simple_output = ["# Sweet Home 3D fallback OBJ: single mesh without materials"]
    for line in SOURCE_SIMPLE_OBJ.read_text(encoding="utf-8").splitlines():
        if line.startswith("v "):
            _, x, y, z = line.split()
            simple_output.append(
                f"v {float(x) / 10:.6f} {float(z) / 10:.6f} {-float(y) / 10:.6f}"
            )
        else:
            simple_output.append(line)
    TARGET_SIMPLE_OBJ.write_text("\n".join(simple_output) + "\n", encoding="utf-8")

    print(f"wrote {TARGET_OBJ}")
    print(f"wrote {TARGET_MTL}")
    print(f"wrote {TARGET_SIMPLE_OBJ}")


if __name__ == "__main__":
    main()
